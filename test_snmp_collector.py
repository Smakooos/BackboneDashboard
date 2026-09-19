import csv
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from collector import snmp_collector as collector


def snapshot(interface="FastEthernet0/0", status="UP", inbound=0, outbound=0):
    return {
        "sys_name": "router",
        "interfaces": {
            "1": {
                "interface": interface,
                "status": status,
                "in_octets": inbound,
                "out_octets": outbound,
            }
        },
    }


class MultiRouterCollectorTests(unittest.IsolatedAsyncioTestCase):
    def test_lab_devices_and_oper_status_mapping(self):
        self.assertEqual(
            collector.DEVICES,
            [
                {"name": "CORE1", "ip": "192.168.80.10"},
                {"name": "EDGE1", "ip": "10.0.1.1"},
                {"name": "EDGE2", "ip": "10.0.1.9"},
                {"name": "CORE2", "ip": "10.0.1.18"},
            ],
        )
        self.assertEqual(collector.oper_status_label(1), "UP")
        self.assertEqual(collector.oper_status_label(2), "CRITICAL")

    def test_initial_baseline_rate_and_counter_reset(self):
        device = collector.DEVICES[0]
        baselines = {}
        start = datetime(2026, 9, 19, 12, 0, 0)

        self.assertEqual(collector.rows_from_snapshot(device, snapshot(inbound=1000, outbound=2000), start, baselines), [])

        rows = collector.rows_from_snapshot(
            device, snapshot(inbound=1_251_000, outbound=627_000), start + timedelta(seconds=10), baselines
        )
        self.assertEqual(rows[0][1:5], ["CORE1", "192.168.80.10", "FastEthernet0/0", "UP"])
        self.assertEqual(rows[0][5:], [1.0, 0.5])

        reset_rows = collector.rows_from_snapshot(
            device, snapshot(inbound=50, outbound=70), start + timedelta(seconds=20), baselines
        )
        self.assertEqual(reset_rows[0][5:], [0.0, 0.0])

    def test_baselines_do_not_merge_same_interface_name_between_devices(self):
        first, second = collector.DEVICES[0], collector.DEVICES[1]
        baselines = {}
        start = datetime(2026, 9, 19, 12, 0, 0)
        collector.rows_from_snapshot(first, snapshot(inbound=0, outbound=0), start, baselines)
        collector.rows_from_snapshot(second, snapshot(inbound=10_000, outbound=10_000), start, baselines)

        first_rows = collector.rows_from_snapshot(first, snapshot(inbound=1_250_000, outbound=0), start + timedelta(seconds=10), baselines)
        second_rows = collector.rows_from_snapshot(second, snapshot(inbound=10_000, outbound=1_260_000), start + timedelta(seconds=10), baselines)

        self.assertEqual(first_rows[0][5], 1.0)
        self.assertEqual(second_rows[0][6], 1.0)
        self.assertEqual(set(baselines), {("CORE1", "FastEthernet0/0"), ("EDGE1", "FastEthernet0/0")})

    async def test_unreachable_router_does_not_stop_other_router(self):
        async def fake_collect(_, device):
            if device["name"] == "EDGE1":
                raise RuntimeError("timeout")
            return snapshot(inbound=100, outbound=200)

        baselines = {}
        with patch.object(collector, "collect_device_snapshot", new=AsyncMock(side_effect=fake_collect)):
            rows = await collector.collect_cycle(None, collector.DEVICES[:2], baselines, datetime(2026, 9, 19, 12, 0, 0))

        self.assertEqual(rows, [])
        self.assertIn(("CORE1", "FastEthernet0/0"), baselines)
        self.assertNotIn(("EDGE1", "FastEthernet0/0"), baselines)


class CsvOutputTests(unittest.TestCase):
    def test_csv_header_and_rows_match_dashboard_schema(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "network_metrics.csv"
            collector.initialize_csv(output)
            collector.append_csv_rows(
                [["2026-09-19T12:00:10", "CORE1", "192.168.80.10", "FastEthernet0/0", "UP", 1.0, 0.5]],
                output,
            )
            with output.open(newline="", encoding="utf-8") as file:
                rows = list(csv.reader(file))

        self.assertEqual(rows[0], collector.CSV_COLUMNS)
        self.assertEqual(rows[1], ["2026-09-19T12:00:10", "CORE1", "192.168.80.10", "FastEthernet0/0", "UP", "1.0", "0.5"])
