# ==========================
# Alert thresholds
# ==========================

import pandas as pd


INBOUND_THRESHOLD_MBPS = 80
OUTBOUND_THRESHOLD_MBPS = 80


def empty_statistics():
    """Return the complete template/API contract when no data is available."""
    return {
        "total_devices": 0, "total_interfaces": 0,
        "avg_in_mbps": 0.0, "avg_out_mbps": 0.0,
        "status": {"labels": ["UP", "WARNING", "CRITICAL"], "values": [0, 0, 0],
                   "UP": 0, "WARNING": 0, "CRITICAL": 0},
        "device_in": {"labels": [], "values": []},
        "interface_labels": [], "interface_in": [], "interface_out": [],
        "device_breakdown": [],
        "alerts": {"high_inbound": 0, "high_outbound": 0},
    }


def _normalize_status(value):
    if pd.isna(value):
        return "CRITICAL"

    value_str = str(value).strip().lower()

    if value_str in {"1", "up", "online", "active"}:
        return "UP"

    if value_str in {"3", "warning", "warn", "testing"}:
        return "WARNING"

    return "CRITICAL"


def _snmp_statistics(df):
    latest_snapshot = df.copy()

    if "timestamp" in latest_snapshot.columns:
        latest_snapshot["timestamp"] = pd.to_datetime(latest_snapshot["timestamp"], errors="coerce")
        latest_snapshot = latest_snapshot.sort_values("timestamp").drop_duplicates(
            subset=["device", "interface"], keep="last"
        )

    latest_snapshot["in_mbps"] = pd.to_numeric(latest_snapshot["in_mbps"], errors="coerce").fillna(0.0)
    latest_snapshot["out_mbps"] = pd.to_numeric(latest_snapshot["out_mbps"], errors="coerce").fillna(0.0)
    latest_snapshot["status"] = latest_snapshot["status"].apply(_normalize_status)

    status_rank = {"UP": 0, "WARNING": 1, "CRITICAL": 2}
    latest_snapshot["status_rank"] = latest_snapshot["status"].map(status_rank)
    device_summary = latest_snapshot.groupby("device", as_index=False, sort=False).agg(
        in_mbps=("in_mbps", "mean"),
        out_mbps=("out_mbps", "mean"),
        status_rank=("status_rank", "max"),
    )
    device_summary["status"] = device_summary["status_rank"].map(
        {value: key for key, value in status_rank.items()}
    )

    status_counts = latest_snapshot["status"].value_counts().to_dict()
    status_values = {
        "UP": int(status_counts.get("UP", 0)),
        "WARNING": int(status_counts.get("WARNING", 0)),
        "CRITICAL": int(status_counts.get("CRITICAL", 0)),
    }

    interface_summary = latest_snapshot.groupby("interface", as_index=False, sort=False).agg(
        in_mbps=("in_mbps", "mean"),
        out_mbps=("out_mbps", "mean")
    )

    statistics = {
        "total_devices": int(latest_snapshot["device"].nunique()),
        "total_interfaces": int(latest_snapshot["interface"].nunique()),
        "avg_in_mbps": round(float(latest_snapshot["in_mbps"].mean()), 2),
        "avg_out_mbps": round(float(latest_snapshot["out_mbps"].mean()), 2),
        "status": {
            "labels": ["UP", "WARNING", "CRITICAL"],
            "values": [
                status_values["UP"],
                status_values["WARNING"],
                status_values["CRITICAL"],
            ],
            "UP": status_values["UP"],
            "WARNING": status_values["WARNING"],
            "CRITICAL": status_values["CRITICAL"],
        },
        "device_in": {
            "labels": [str(device) for device in device_summary["device"].tolist()],
            "values": [round(float(value), 2) for value in device_summary["in_mbps"].tolist()],
        },
        "interface_labels": [str(item) for item in interface_summary["interface"].tolist()],
        "interface_in": [round(float(value), 2) for value in interface_summary["in_mbps"].tolist()],
        "interface_out": [round(float(value), 2) for value in interface_summary["out_mbps"].tolist()],
        "device_breakdown": [
            {
                "device": str(row["device"]),
                "in_mbps": round(float(row["in_mbps"]), 2),
                "out_mbps": round(float(row["out_mbps"]), 2),
                "status": str(row["status"]),
            }
            for row in device_summary.to_dict("records")
        ],
        "alerts": {
            "high_inbound": int((device_summary["in_mbps"] > INBOUND_THRESHOLD_MBPS).sum()),
            "high_outbound": int((device_summary["out_mbps"] > OUTBOUND_THRESHOLD_MBPS).sum()),
        },
    }

    return statistics


def compute_statistics(df):
    """
    Compute the main network statistics from a Pandas DataFrame.

    The dashboard accepts the normalized SNMP export produced by the collector.
    """

    if df is None or df.empty:
        return empty_statistics()

    df = df.copy()
    df.columns = [str(column).strip().lower() for column in df.columns]

    if {"device", "status", "in_mbps", "out_mbps"}.issubset(df.columns):
        return _snmp_statistics(df)

    return empty_statistics()
