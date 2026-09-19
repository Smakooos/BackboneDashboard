import pandas as pd

df = pd.read_csv('data/network_metrics.csv', header=None, names=['timestamp', 'device', 'ip', 'interface', 'status', 'in_mbps', 'out_mbps'])

df['timestamp'] = pd.to_datetime(df['timestamp'])
df_recent = df[df['timestamp'] == df['timestamp'].max()].copy()

print(f'Total rows before: {len(df)}')
print(f'Total rows after (latest timestamp only): {len(df_recent)}')
print(f'Latest timestamp: {df_recent["timestamp"].iloc[0]}')
print(f'Status values in recent data: {sorted(df_recent["status"].unique())}')
print()
print('Sample recent data:')
print(df_recent.head(20))
print()
print('Status counts in recent data:')
print(df_recent['status'].value_counts().sort_index())
