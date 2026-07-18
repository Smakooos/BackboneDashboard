from utils.parser import load_csv
from utils.analyser import compute_statistics

# Load the CSV file
df = load_csv("data/sample.csv")

if df is not None:
    stats = compute_statistics(df)

    print("=== Network Statistics ===")
    print(stats)