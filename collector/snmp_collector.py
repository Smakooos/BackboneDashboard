"""Append interface throughput snapshots collected through SNMPv2c.

Set SNMP_DEVICE_IP and SNMP_COMMUNITY before running this module. Optional:
SNMP_DEVICE_NAME, SNMP_PORT, SNMP_POLL_INTERVAL and SNMP_DATA_FILE.
"""

import asyncio
import csv
import os
from datetime import datetime
from pathlib import Path

from pysnmp.hlapi.v3arch.asyncio import (CommunityData, ContextData, ObjectIdentity,
                                         ObjectType, SnmpEngine, UdpTransportTarget, next_cmd)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = Path(os.getenv("SNMP_DATA_FILE", BASE_DIR / "data" / "network_metrics.csv"))
DEVICE_IP = os.getenv("SNMP_DEVICE_IP")
DEVICE_NAME = os.getenv("SNMP_DEVICE_NAME", DEVICE_IP or "unnamed-device")
COMMUNITY = os.getenv("SNMP_COMMUNITY")
PORT = int(os.getenv("SNMP_PORT", "161"))
POLL_INTERVAL = max(1, int(os.getenv("SNMP_POLL_INTERVAL", "30")))
CSV_COLUMNS = ["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"]
IF_DESCR = "1.3.6.1.2.1.2.2.1.2"
IF_OPER_STATUS = "1.3.6.1.2.1.2.2.1.8"
IF_HC_IN_OCTETS = "1.3.6.1.2.1.31.1.1.1.6"
IF_HC_OUT_OCTETS = "1.3.6.1.2.1.31.1.1.1.10"


def initialize_csv():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(CSV_COLUMNS)


def write_csv_row(timestamp, interface, status, in_mbps, out_mbps):
    with DATA_FILE.open("a", newline="", encoding="utf-8") as file:
        csv.writer(file).writerow([timestamp, DEVICE_NAME, DEVICE_IP, interface, status,
                                   round(in_mbps, 3), round(out_mbps, 3)])


async def walk_column(engine, target, oid):
    """Return one SNMP table column keyed by interface index."""
    values, current_oid = {}, ObjectIdentity(oid)
    while True:
        error, status, _, var_binds = await next_cmd(
            engine, CommunityData(COMMUNITY, mpModel=1), target, ContextData(),
            ObjectType(current_oid), lexicographicMode=False,
        )
        if error or status or not var_binds:
            if error or status:
                print(f"SNMP walk failed for {oid}: {error or status}")
            break
        name, value = var_binds[0]
        name_text = str(name)
        if not name_text.startswith(f"{oid}."):
            break
        values[name_text.rsplit(".", 1)[-1]] = value.prettyPrint()
        current_oid = ObjectIdentity(name)
    return values


async def collect_snapshot(engine, target):
    names, statuses, inbound, outbound = await asyncio.gather(
        walk_column(engine, target, IF_DESCR), walk_column(engine, target, IF_OPER_STATUS),
        walk_column(engine, target, IF_HC_IN_OCTETS), walk_column(engine, target, IF_HC_OUT_OCTETS),
    )
    return {index: {"interface": names.get(index, f"ifIndex-{index}"),
                    "status": statuses.get(index, "unknown"),
                    "in_octets": int(inbound[index]) if index in inbound else None,
                    "out_octets": int(outbound[index]) if index in outbound else None}
            for index in names}


async def main():
    if not DEVICE_IP or not COMMUNITY:
        raise SystemExit("Set SNMP_DEVICE_IP and SNMP_COMMUNITY before starting the collector.")
    initialize_csv()
    engine, target = SnmpEngine(), await UdpTransportTarget.create((DEVICE_IP, PORT))
    previous_snapshot, previous_time = None, None
    print(f"Collecting {DEVICE_NAME} ({DEVICE_IP}) every {POLL_INTERVAL}s")
    while True:
        try:
            snapshot, now = await collect_snapshot(engine, target), datetime.now()
            if previous_snapshot is not None:
                elapsed = (now - previous_time).total_seconds()
                for index, current in snapshot.items():
                    previous = previous_snapshot.get(index)
                    if not previous or None in (current["in_octets"], current["out_octets"], previous["in_octets"], previous["out_octets"]):
                        continue
                    in_mbps = max(0, current["in_octets"] - previous["in_octets"]) * 8 / elapsed / 1_000_000
                    out_mbps = max(0, current["out_octets"] - previous["out_octets"]) * 8 / elapsed / 1_000_000
                    write_csv_row(now.isoformat(timespec="seconds"), current["interface"], current["status"], in_mbps, out_mbps)
            previous_snapshot, previous_time = snapshot, now
        except Exception as error:
            print(f"Collector error: {error}")
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
