# ==========================
# Alert thresholds
# ==========================

CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 80
LATENCY_THRESHOLD = 30


def compute_statistics(df):
    """
    Compute the main network statistics from a Pandas DataFrame.

    Args:
        df (pandas.DataFrame): Network monitoring data.

    Returns:
        dict: Dictionary containing KPIs and alerts.
    """

    if df is None or df.empty:
        return {}

    statistics = {
        "total_devices": df["Device"].nunique(),

        "avg_cpu": round(df["CPU"].mean(), 2),

        "avg_memory": round(df["Memory"].mean(), 2),

        "avg_bandwidth": round(df["Bandwidth"].mean(), 2),

        "avg_latency": round(df["Latency"].mean(), 2),

        "status": {
            "labels": ["UP", "WARNING", "CRITICAL"],
            "values": [
                int((df["Status"] == "UP").sum()),
                int((df["Status"] == "WARNING").sum()),
                int((df["Status"] == "CRITICAL").sum())
            ],
            "UP": int((df["Status"] == "UP").sum()),
            "WARNING": int((df["Status"] == "WARNING").sum()),
            "CRITICAL": int((df["Status"] == "CRITICAL").sum())
        },

        "device_cpu": {
            "labels": [str(device) for device in df["Device"].tolist()],
            "values": [round(float(value), 2) for value in df["CPU"].tolist()]
        },

        "alerts": {
            "high_cpu": int((df["CPU"] > CPU_THRESHOLD).sum()),
            "high_memory": int((df["Memory"] > MEMORY_THRESHOLD).sum()),
            "high_latency": int((df["Latency"] > LATENCY_THRESHOLD).sum())
        },
    }

    return statistics