# ==========================
# Alert thresholds
# ==========================

import pandas as pd


INBOUND_THRESHOLD_MBPS = 80
OUTBOUND_THRESHOLD_MBPS = 80

# Inventory of monitored routers.
# A router is considered UP when it is present in the latest SNMP data.
DEVICE_INVENTORY = {
    "CORE1": "192.168.80.10",
    "EDGE1": "10.0.1.1",
    "EDGE2": "10.0.1.9",
    "CORE2": "10.0.1.18",
}


def empty_statistics():
    """Return the complete template/API contract when no data is available."""
    return {
        "total_devices": 0,
        "total_interfaces": 0,
        "avg_in_mbps": 0.0,
        "avg_out_mbps": 0.0,
        "status": {
            "labels": ["UP", "DOWN", "WARNING", "CRITICAL"],
            "values": [0, 0, 0, 0],
            "UP": 0,
            "DOWN": 0,
            "WARNING": 0,
            "CRITICAL": 0,
        },
        "device_traffic": {
            "labels": [],
            "inbound": [],
            "outbound": [],
        },
        "device_status": {
            "labels": ["UP", "DOWN", "WARNING", "CRITICAL"],
            "values": [0, 0, 0, 0],
        },
        "interface_labels": [],
        "interface_in": [],
        "interface_out": [],
        "device_breakdown": [],
        "alerts": {
            "high_inbound": 0,
            "high_outbound": 0,
        },
    }


def _normalize_status(value):
    """Normalize SNMP interface status."""
    if pd.isna(value):
        return "CRITICAL"

    value_str = str(value).strip().lower()

    if value_str in {"1", "up", "online", "active"}:
        return "UP"

    if value_str in {"2", "down", "offline", "inactive"}:
        return "DOWN"

    if value_str in {"3", "warning", "warn", "testing"}:
        return "WARNING"

    return "CRITICAL"


def _snmp_statistics(df):
    latest_snapshot = df.copy()

    # Normalize timestamp.
    if "timestamp" in latest_snapshot.columns:
        latest_snapshot["timestamp"] = pd.to_datetime(
            latest_snapshot["timestamp"],
            errors="coerce",
        )

        latest_snapshot = latest_snapshot.sort_values("timestamp")

        # Keep the latest measurement for every device/interface pair.
        latest_snapshot = latest_snapshot.drop_duplicates(
            subset=["device", "interface"],
            keep="last",
        )

    # Numeric traffic values.
    latest_snapshot["in_mbps"] = pd.to_numeric(
        latest_snapshot["in_mbps"],
        errors="coerce",
    ).fillna(0.0)

    latest_snapshot["out_mbps"] = pd.to_numeric(
        latest_snapshot["out_mbps"],
        errors="coerce",
    ).fillna(0.0)

    # Interface status.
    latest_snapshot["status"] = latest_snapshot["status"].apply(
        _normalize_status
    )

    # ---------------------------------------------------------
    # INTERFACE STATISTICS
    # ---------------------------------------------------------

    status_counts = latest_snapshot["status"].value_counts().to_dict()

    interface_status_values = {
        "UP": int(status_counts.get("UP", 0)),
        "DOWN": int(status_counts.get("DOWN", 0)),
        "WARNING": int(status_counts.get("WARNING", 0)),
        "CRITICAL": int(status_counts.get("CRITICAL", 0)),
    }

    # ---------------------------------------------------------
    # DEVICE STATISTICS
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # Device status is NOT calculated from interface status.
    #
    # If a router appears in the SNMP data, it successfully
    # responded to SNMP and is therefore considered UP.
    #
    # Its interfaces can independently be UP / DOWN / CRITICAL.
    # ---------------------------------------------------------

    device_rows = []

    for device_name, device_ip in DEVICE_INVENTORY.items():

        device_data = latest_snapshot[
            latest_snapshot["device"].astype(str) == device_name
        ].copy()

        if device_data.empty:
            # No recent SNMP data for this router.
            device_status = "DOWN"

            device_rows.append({
                "device": device_name,
                "ip": device_ip,
                "interfaces": 0,
                "interfaces_up": 0,
                "interfaces_down": 0,
                "interfaces_critical": 0,
                "in_mbps": 0.0,
                "out_mbps": 0.0,
                "status": device_status,
            })

            continue

        # Router itself is UP because SNMP data exists.
        device_status = "UP"

        interfaces_up = int(
            (device_data["status"] == "UP").sum()
        )

        interfaces_down = int(
            (device_data["status"] == "DOWN").sum()
        )

        interfaces_critical = int(
            (device_data["status"] == "CRITICAL").sum()
        )

        device_rows.append({
            "device": device_name,
            "ip": device_ip,
            "interfaces": int(len(device_data)),
            "interfaces_up": interfaces_up,
            "interfaces_down": interfaces_down,
            "interfaces_critical": interfaces_critical,
            "in_mbps": round(
                float(device_data["in_mbps"].mean()),
                2,
            ),
            "out_mbps": round(
                float(device_data["out_mbps"].mean()),
                2,
            ),
            "status": device_status,
        })

    device_summary = pd.DataFrame(device_rows)

    # ---------------------------------------------------------
    # DEVICE STATUS COUNTS
    # ---------------------------------------------------------

    device_status_counts = device_summary["status"].value_counts().to_dict()

    device_status_values = {
        "UP": int(device_status_counts.get("UP", 0)),
        "DOWN": int(device_status_counts.get("DOWN", 0)),
        "WARNING": int(device_status_counts.get("WARNING", 0)),
        "CRITICAL": int(device_status_counts.get("CRITICAL", 0)),
    }

    # ---------------------------------------------------------
    # INTERFACE CHART
    # ---------------------------------------------------------

    interface_summary = latest_snapshot[
        [
            "device",
            "interface",
            "in_mbps",
            "out_mbps",
        ]
    ].copy()

    # Interface names can repeat between routers.
    # Prefix with device name so they remain distinct.
    interface_summary["label"] = (
        interface_summary["device"].astype(str)
        + " / "
        + interface_summary["interface"].astype(str)
    )

    # ---------------------------------------------------------
    # FINAL STATISTICS
    # ---------------------------------------------------------

    statistics = {
        "total_devices": int(len(device_summary)),

        # Number of actual device/interface combinations.
        "total_interfaces": int(len(latest_snapshot)),

        "avg_in_mbps": round(
            float(latest_snapshot["in_mbps"].mean()),
            2,
        ),

        "avg_out_mbps": round(
            float(latest_snapshot["out_mbps"].mean()),
            2,
        ),

        # Interface status statistics.
        "status": {
            "labels": [
                "UP",
                "DOWN",
                "WARNING",
                "CRITICAL",
            ],
            "values": [
                interface_status_values["UP"],
                interface_status_values["DOWN"],
                interface_status_values["WARNING"],
                interface_status_values["CRITICAL"],
            ],
            "UP": interface_status_values["UP"],
            "DOWN": interface_status_values["DOWN"],
            "WARNING": interface_status_values["WARNING"],
            "CRITICAL": interface_status_values["CRITICAL"],
        },

        # Traffic per router.
        "device_traffic": {
            "labels": [
                str(device)
                for device in device_summary["device"].tolist()
            ],
            "inbound": [
                round(float(value), 2)
                for value in device_summary["in_mbps"].tolist()
            ],
            "outbound": [
                round(float(value), 2)
                for value in device_summary["out_mbps"].tolist()
            ],
        },

        # Device status statistics.
        "device_status": {
            "labels": [
                "UP",
                "DOWN",
                "WARNING",
                "CRITICAL",
            ],
            "values": [
                device_status_values["UP"],
                device_status_values["DOWN"],
                device_status_values["WARNING"],
                device_status_values["CRITICAL"],
            ],
        },

        # Interface traffic chart.
        "interface_labels": [
            str(item)
            for item in interface_summary["label"].tolist()
        ],

        "interface_in": [
            round(float(value), 2)
            for value in interface_summary["in_mbps"].tolist()
        ],

        "interface_out": [
            round(float(value), 2)
            for value in interface_summary["out_mbps"].tolist()
        ],

        # Device cards/table.
        "device_breakdown": [
            {
                "device": str(row["device"]),
                "ip": str(row["ip"]),
                "interfaces": int(row["interfaces"]),
                "interfaces_up": int(row["interfaces_up"]),
                "interfaces_down": int(row["interfaces_down"]),
                "interfaces_critical": int(row["interfaces_critical"]),
                "in_mbps": round(float(row["in_mbps"]), 2),
                "out_mbps": round(float(row["out_mbps"]), 2),
                "status": str(row["status"]),
            }
            for row in device_summary.to_dict("records")
        ],

        "alerts": {
            "high_inbound": int(
                (device_summary["in_mbps"] > INBOUND_THRESHOLD_MBPS).sum()
            ),
            "high_outbound": int(
                (device_summary["out_mbps"] > OUTBOUND_THRESHOLD_MBPS).sum()
            ),
        },
    }

    return statistics


def compute_statistics(df):
    """
    Compute network statistics from the normalized SNMP export.
    """

    if df is None or df.empty:
        return empty_statistics()

    df = df.copy()

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    if {
        "device",
        "status",
        "in_mbps",
        "out_mbps",
    }.issubset(df.columns):

        return _snmp_statistics(df)

    return empty_statistics()