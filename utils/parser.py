import os

import pandas as pd


SNMP_COLUMNS = [
    "timestamp",
    "device",
    "ip",
    "interface",
    "status",
    "in_mbps",
    "out_mbps",
]


def load_csv(file_path):
    """
    Load a CSV file and return it as a Pandas DataFrame.

    The collector may write either a headered CSV or an existing headerless
    SNMP export. Both are normalized to the dashboard schema.
    """

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    try:
        dataframe = pd.read_csv(file_path)

        if dataframe.empty:
            print("Error: The CSV file is empty.")
            return None

        normalized_columns = [str(column).strip().lower() for column in dataframe.columns]

        if {"timestamp", "device"}.issubset(set(normalized_columns)):
            dataframe.columns = normalized_columns
            return dataframe

        if {"device", "status", "in_mbps", "out_mbps"}.issubset(set(normalized_columns)):
            dataframe.columns = normalized_columns
            return dataframe

        dataframe = pd.read_csv(file_path, header=None, names=SNMP_COLUMNS)
        return dataframe

    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return None

    except Exception as exc:
        print(f"Unexpected error: {exc}")
        return None
