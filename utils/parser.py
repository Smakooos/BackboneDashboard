import pandas as pd


def load_csv(file_path):
    """
    Load a CSV file and return it as a Pandas DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pandas.DataFrame
    """

    try:
        dataframe = pd.read_csv(file_path)
        return dataframe

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None