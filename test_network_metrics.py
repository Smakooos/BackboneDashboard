import unittest

import pandas as pd

from utils.analyser import compute_statistics


class NetworkMetricsTests(unittest.TestCase):
    def test_latest_snapshot_and_worst_status_are_used(self):
        df = pd.DataFrame([
            ["2026-09-19T09:20:00", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 50.0, 25.0],
            ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 100.0, 50.0],
            ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/1", 2, 200.0, 80.0],
            ["2026-09-19T09:26:57", "CORE2", "10.0.1.18", "FastEthernet0/0", 1, 150.0, 75.0],
        ], columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])

        stats = compute_statistics(df)
        devices = {item["device"]: item for item in stats["device_breakdown"]}

        self.assertEqual(stats["total_devices"], 2)
        self.assertAlmostEqual(stats["avg_in_mbps"], 150.0)
        self.assertEqual(stats["status"]["UP"], 2)
        self.assertEqual(stats["status"]["DOWN"], 1)
        self.assertEqual(stats["status"]["CRITICAL"], 0)
        self.assertEqual(devices["CORE1"]["status"], "DOWN")
        self.assertEqual(devices["CORE2"]["status"], "UP")

    def test_same_interface_names_on_two_devices_remain_separate(self):
        df = pd.DataFrame([
            ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 10.0, 5.0],
            ["2026-09-19T09:26:57", "EDGE1", "10.0.1.1", "FastEthernet0/0", 1, 20.0, 10.0],
        ], columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])

        stats = compute_statistics(df)

        self.assertEqual(stats["total_interfaces"], 2)
        self.assertEqual(stats["interface_labels"], ["CORE1 / FastEthernet0/0", "EDGE1 / FastEthernet0/0"])

    def test_four_devices_have_independent_ip_metrics_and_worst_status(self):
        df = pd.DataFrame([
            ["2026-09-19T12:00:00", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 10.0, 5.0],
            ["2026-09-19T12:00:00", "CORE1", "192.168.80.10", "FastEthernet0/1", 2, 30.0, 15.0],
            ["2026-09-19T12:00:00", "EDGE1", "10.0.1.1", "FastEthernet0/0", 1, 20.0, 10.0],
            ["2026-09-19T12:00:00", "EDGE2", "10.0.1.9", "FastEthernet0/0", 3, 40.0, 20.0],
            ["2026-09-19T12:00:00", "CORE2", "10.0.1.18", "FastEthernet0/0", 1, 50.0, 25.0],
        ], columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])

        stats = compute_statistics(df)
        devices = {item["device"]: item for item in stats["device_breakdown"]}

        self.assertEqual(set(devices), {"CORE1", "EDGE1", "EDGE2", "CORE2"})
        self.assertEqual(devices["CORE1"]["ip"], "192.168.80.10")
        self.assertEqual(devices["CORE1"]["interfaces"], 2)
        self.assertEqual(devices["CORE1"]["interfaces_up"], 1)
        self.assertEqual(devices["CORE1"]["interfaces_down"], 1)
        self.assertEqual(devices["CORE1"]["interfaces_critical"], 0)
        self.assertEqual(devices["CORE1"]["status"], "DOWN")
        self.assertEqual(devices["CORE1"]["in_mbps"], 20.0)
        self.assertEqual(devices["EDGE1"]["in_mbps"], 20.0)
        self.assertEqual(devices["EDGE2"]["status"], "WARNING")
        self.assertEqual(stats["device_traffic"]["labels"], ["CORE1", "EDGE1", "EDGE2", "CORE2"])

    def test_distinguish_down_from_critical(self):
        """Verify that status 2 (DOWN) is distinct from CRITICAL."""
        df = pd.DataFrame([
            ["2026-09-19T12:00:00", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 10.0, 5.0],
            ["2026-09-19T12:00:00", "CORE1", "192.168.80.10", "FastEthernet0/1", 2, 0.0, 0.0],
            ["2026-09-19T12:00:00", "CORE1", "192.168.80.10", "FastEthernet0/2", "down", 0.0, 0.0],
            ["2026-09-19T12:00:00", "CORE1", "192.168.80.10", "FastEthernet0/3", 4, 0.0, 0.0],
        ], columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])

        stats = compute_statistics(df)
        
        # Verify status counts
        self.assertEqual(stats["status"]["UP"], 1)
        self.assertEqual(stats["status"]["DOWN"], 2)
        self.assertEqual(stats["status"]["CRITICAL"], 1)
        
        # Verify device breakdown
        device = stats["device_breakdown"][0]
        self.assertEqual(device["interfaces_up"], 1)
        self.assertEqual(device["interfaces_down"], 2)
        self.assertEqual(device["interfaces_critical"], 1)
        # Device status should be worst, which is CRITICAL
        self.assertEqual(device["status"], "CRITICAL")
