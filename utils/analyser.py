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
            "UP": (df["Status"] == "UP").sum(),
            "WARNING": (df["Status"] == "WARNING").sum(),
            "CRITICAL": (df["Status"] == "CRITICAL").sum()
        },

        "alerts": {
            "high_cpu": (df["CPU"] > CPU_THRESHOLD).sum(),
            "high_memory": (df["Memory"] > MEMORY_THRESHOLD).sum(),
            "high_latency": (df["Latency"] > LATENCY_THRESHOLD).sum()
        }
    }

    return statistics