"""Collect per-interface SNMP throughput from the four GNS3 lab routers.

The collector appends rows compatible with ``data/network_metrics.csv``.  It
does not store the SNMP community in source code: set ``SNMP_COMMUNITY`` to
override the lab's read-only default.
"""

import asyncio
import csv
import os
from datetime import datetime
from pathlib import Path

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
    next_cmd,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = Path(os.getenv("SNMP_DATA_FILE", BASE_DIR / "data" / "network_metrics.csv"))
COMMUNITY = os.getenv("SNMP_COMMUNITY", "BackboneRead")
PORT = int(os.getenv("SNMP_PORT", "161"))
POLL_INTERVAL = max(1, int(os.getenv("SNMP_POLL_INTERVAL", "10")))

DEVICES = [
    {"name": "CORE1", "ip": "192.168.80.10"},
    {"name": "EDGE1", "ip": "10.0.1.1"},
    {"name": "EDGE2", "ip": "10.0.1.9"},
    {"name": "CORE2", "ip": "10.0.1.18"},
]

CSV_COLUMNS = ["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"]
SYS_NAME = "1.3.6.1.2.1.1.5.0"
IF_DESCR = "1.3.6.1.2.1.2.2.1.2"
IF_OPER_STATUS = "1.3.6.1.2.1.2.2.1.8"
IF_HC_IN_OCTETS = "1.3.6.1.2.1.31.1.1.1.6"
IF_HC_OUT_OCTETS = "1.3.6.1.2.1.31.1.1.1.10"


def oper_status_label(value):
    """Map the relevant SNMP ifOperStatus values to dashboard statuses."""
    value = str(value).strip().lower()
    if value in {"1", "up"}:
        return "UP"
    if value in {"2", "down"}:
        return "DOWN"
    if value in {"3", "testing"}:
        return "WARNING"
    return "CRITICAL"


def initialize_csv(file_path=DATA_FILE):
    """Create a header only for a new/empty metrics file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists() or file_path.stat().st_size == 0:
        with file_path.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(CSV_COLUMNS)


def append_csv_rows(rows, file_path=DATA_FILE):
    """Append already-normalized collector rows to the dashboard CSV."""
    if not rows:
        return
    with Path(file_path).open("a", newline="", encoding="utf-8") as file:
        csv.writer(file).writerows(rows)


async def get_scalar(engine, target, oid):
    error, status, _, var_binds = await get_cmd(
        engine, CommunityData(COMMUNITY, mpModel=1), target, ContextData(), ObjectType(ObjectIdentity(oid))
    )
    if error or status or not var_binds:
        raise RuntimeError(error or status or f"No value returned for {oid}")
    return var_binds[0][1].prettyPrint()


async def walk_column(engine, target, oid):
    """Return an SNMP interface-table column keyed by ifIndex."""
    values, current_oid = {}, ObjectIdentity(oid)
    while True:
        error, status, _, var_binds = await next_cmd(
            engine,
            CommunityData(COMMUNITY, mpModel=1),
            target,
            ContextData(),
            ObjectType(current_oid),
            lexicographicMode=False,
        )
        if error or status or not var_binds:
            if error or status:
                raise RuntimeError(error or status)
            break
        name, value = var_binds[0]
        name_text = str(name)
        if not name_text.startswith(f"{oid}."):
            break
        values[name_text.rsplit(".", 1)[-1]] = value.prettyPrint()
        current_oid = ObjectIdentity(name)
    return values


async def collect_device_snapshot(engine, device):
    """Fetch sysName, descriptions, status and 64-bit counters for one router."""
    target = await UdpTransportTarget.create((device["ip"], PORT))
    sys_name, names, statuses, inbound, outbound = await asyncio.gather(
        get_scalar(engine, target, SYS_NAME),
        walk_column(engine, target, IF_DESCR),
        walk_column(engine, target, IF_OPER_STATUS),
        walk_column(engine, target, IF_HC_IN_OCTETS),
        walk_column(engine, target, IF_HC_OUT_OCTETS),
    )
    interfaces = {}
    for if_index, interface in names.items():
        if interface.lower() == "null0":
            continue
        interfaces[if_index] = {
            "interface": interface,
            "status": oper_status_label(statuses.get(if_index, "unknown")),
            "in_octets": int(inbound[if_index]) if if_index in inbound else None,
            "out_octets": int(outbound[if_index]) if if_index in outbound else None,
        }
    return {"sys_name": sys_name, "interfaces": interfaces}


def rows_from_snapshot(device, snapshot, observed_at, baselines):
    """Calculate rates and update baselines keyed by (device, interface).

    The first observation for an interface is intentionally not emitted: it
    establishes the counter baseline and prevents a false throughput value.
    """
    rows = []
    for current in snapshot["interfaces"].values():
        interface = current["interface"]
        key = (device["name"], interface)
        previous = baselines.get(key)
        baselines[key] = {"in_octets": current["in_octets"], "out_octets": current["out_octets"], "time": observed_at}

        if previous is None or None in (current["in_octets"], current["out_octets"], previous["in_octets"], previous["out_octets"]):
            continue
        elapsed = (observed_at - previous["time"]).total_seconds()
        if elapsed <= 0:
            continue
        in_delta = max(0, current["in_octets"] - previous["in_octets"])
        out_delta = max(0, current["out_octets"] - previous["out_octets"])
        rows.append([
            observed_at.isoformat(timespec="seconds"),
            device["name"],
            device["ip"],
            interface,
            current["status"],
            round(in_delta * 8 / elapsed / 1_000_000, 3),
            round(out_delta * 8 / elapsed / 1_000_000, 3),
        ])
    return rows


async def collect_cycle(engine, devices, baselines, observed_at=None):
    """Poll all routers concurrently; an unavailable router does not stop peers."""
    observed_at = observed_at or datetime.now()
    results = await asyncio.gather(
        *(collect_device_snapshot(engine, device) for device in devices), return_exceptions=True
    )
    rows = []
    for device, result in zip(devices, results):
        if isinstance(result, Exception):
            print(f"SNMP error for {device['name']} ({device['ip']}): {result}")
            continue
        rows.extend(rows_from_snapshot(device, result, observed_at, baselines))
        print(f"Collected {device['name']} (sysName: {result['sys_name']}, interfaces: {len(result['interfaces'])})")
    return rows


async def main():
    initialize_csv()
    engine = SnmpEngine()
    baselines = {}
    print(f"Monitoring {len(DEVICES)} routers every {POLL_INTERVAL}s; writing to {DATA_FILE}")
    while True:
        rows = await collect_cycle(engine, DEVICES, baselines)
        append_csv_rows(rows)
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
