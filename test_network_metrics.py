import pandas as pd
import pytest

from utils.analyser import compute_statistics


def test_compute_statistics_handles_snmp_snapshot():
    df = pd.DataFrame([
        ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/0", 1, 100.0, 50.0],
        ["2026-09-19T09:26:57", "CORE1", "192.168.80.10", "FastEthernet0/1", 2, 200.0, 80.0],
        ["2026-09-19T09:26:57", "CORE2", "192.168.80.11", "FastEthernet0/0", 1, 150.0, 75.0],
    ], columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])

    stats = compute_statistics(df)

    assert stats["total_devices"] == 2
    assert stats["avg_in_mbps"] == pytest.approx(150.0)
    assert stats["avg_out_mbps"] == pytest.approx(68.33, abs=0.01)
    assert stats["status"]["UP"] == 2
    assert stats["status"]["WARNING"] == 1
