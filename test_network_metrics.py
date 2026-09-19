import pandas as pd
import unittest

from utils.analyser import compute_statistics


class NetworkMetricsTests(unittest.TestCase):
    def test_statistics_use_latest_snapshot_and_worst_device_status(self):
        df = pd.DataFrame([
        ["2026-09-19T09:20:00", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 50.0, 25.0],
        ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 100.0, 50.0],
        ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/1", 2, 200.0, 80.0],
        ["2026-09-19T09:26:57", "CORE2", "192.168.80.11", "FastEthernet0/0", 1, 150.0, 75.0],
        ], columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])

        stats = compute_statistics(df)

        self.assertEqual(stats["total_devices"], 2)
        self.assertAlmostEqual(stats["avg_in_mbps"], 150.0)
        self.assertAlmostEqual(stats["avg_out_mbps"], 68.33, places=2)
        self.assertEqual(stats["status"]["UP"], 2)
        self.assertEqual(stats["status"]["CRITICAL"], 1)
        self.assertEqual(stats["device_breakdown"][0]["status"], "CRITICAL")
