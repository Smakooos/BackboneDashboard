# ==========================
# Alert thresholds
# ==========================

import pandas as pd


CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80
LATENCY_THRESHOLD = 30


def _normalize_status(value):
    if pd.isna(value):
        return "CRITICAL"

    value_str = str(value).strip().lower()

    if value_str in {"1", "up", "online", "active"}:
        return "UP"

    if value_str in {"2", "warning", "warn"}:
        return "WARNING"

    return "CRITICAL"


def _legacy_statistics(df):
    statistics = {
        "total_devices": int(df["device"].nunique()),
        "avg_cpu": round(float(df["cpu"].mean()), 2),
        "avg_memory": round(float(df["memory"].mean()), 2),
        "avg_bandwidth": round(float(df["bandwidth"].mean()), 2),
        "avg_latency": round(float(df["latency"].mean()), 2),
        "status": {
            "labels": ["UP", "WARNING", "CRITICAL"],
            "values": [
                int((df["status"] == "UP").sum()),
                int((df["status"] == "WARNING").sum()),
                int((df["status"] == "CRITICAL").sum()),
            ],
            "UP": int((df["status"] == "UP").sum()),
            "WARNING": int((df["status"] == "WARNING").sum()),
            "CRITICAL": int((df["status"] == "CRITICAL").sum()),
        },
        "device_cpu": {
            "labels": [str(device) for device in df["device"].tolist()],
            "values": [round(float(value), 2) for value in df["cpu"].tolist()],
        },
        "alerts": {
            "high_cpu": int((df["cpu"] > CPU_THRESHOLD).sum()),
            "high_memory": int((df["memory"] > MEMORY_THRESHOLD).sum()),
            "high_latency": int((df["latency"] > LATENCY_THRESHOLD).sum()),
        },
    }
    return statistics


def _snmp_statistics(df):
    latest_snapshot = df.copy()

    if "timestamp" in latest_snapshot.columns:
        latest_snapshot = latest_snapshot.sort_values("timestamp").drop_duplicates(
            subset=["device", "interface"], keep="last"
        )

    latest_snapshot["in_mbps"] = pd.to_numeric(latest_snapshot["in_mbps"], errors="coerce").fillna(0.0)
    latest_snapshot["out_mbps"] = pd.to_numeric(latest_snapshot["out_mbps"], errors="coerce").fillna(0.0)
    latest_snapshot["status"] = latest_snapshot["status"].apply(_normalize_status)

    device_summary = latest_snapshot.groupby("device", as_index=False).agg(
        in_mbps=("in_mbps", "mean"),
        out_mbps=("out_mbps", "mean"),
        status=("status", lambda s: s.mode().iloc[0] if not s.empty else "CRITICAL")
    )

    status_counts = latest_snapshot["status"].value_counts().to_dict()
    status_values = {
        "UP": int(status_counts.get("UP", 0)),
        "WARNING": int(status_counts.get("WARNING", 0)),
        "CRITICAL": int(status_counts.get("CRITICAL", 0)),
    }

    interface_summary = latest_snapshot.groupby("interface", as_index=False).agg(
        in_mbps=("in_mbps", "mean"),
        out_mbps=("out_mbps", "mean")
    )

    statistics = {
        "total_devices": int(latest_snapshot["device"].nunique()),
        "total_interfaces": int(latest_snapshot["interface"].nunique()),
        "avg_in_mbps": round(float(latest_snapshot["in_mbps"].mean()), 2),
        "avg_out_mbps": round(float(latest_snapshot["out_mbps"].mean()), 2),
        "avg_latency": 0.0,
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
        "device_cpu": {
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
            "high_cpu": int((device_summary["in_mbps"] > CPU_THRESHOLD).sum()),
            "high_memory": int((device_summary["out_mbps"] > MEMORY_THRESHOLD).sum()),
            "high_latency": 0,
        },
    }

    return statistics


def compute_statistics(df):
    """
    Compute the main network statistics from a Pandas DataFrame.

    The CSV can either describe the legacy demo dataset or the SNMP export from
    the network collector. This function handles both layouts.
    """

    if df is None or df.empty:
        return {}

    df = df.copy()
    df.columns = [str(column).strip().lower() for column in df.columns]

    if {"device", "cpu", "memory", "bandwidth", "latency", "status"}.issubset(df.columns):
        return _legacy_statistics(df)

    if {"device", "status", "in_mbps", "out_mbps"}.issubset(df.columns):
        return _snmp_statistics(df)

    return {}
