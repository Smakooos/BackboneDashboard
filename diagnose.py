#!/usr/bin/env python
"""Diagnostic script to check DOWN vs CRITICAL status."""

from utils.parser import load_csv
from utils.analyser import compute_statistics

df = load_csv('data/network_metrics.csv')
if df is not None:
    print('=== CSV Data Sample (last 10 rows) ===')
    print(df.tail(10))
    print()
    print('=== Status Value Counts ===')
    print(df['status'].value_counts().sort_index())
    print()
    stats = compute_statistics(df)
    print('=== Statistics ===')
    print(f"Total Devices: {stats['total_devices']}")
    print(f"Total Interfaces: {stats['total_interfaces']}")
    print(f"Global Status Counts: {stats['status']}")
    print()
    print('=== Device Breakdown ===')
    for device in stats['device_breakdown']:
        print(f"{device['device']:6s} | IP: {device['ip']:15s} | Intf: {device['interfaces']:2d} | UP: {device['interfaces_up']:2d} | DOWN: {device['interfaces_down']:2d} | CRITICAL: {device['interfaces_critical']:2d} | Status: {device['status']}")
