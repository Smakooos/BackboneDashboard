import pandas as pd

# Lire le CSV avec le bon format
df = pd.read_csv('data/network_metrics.csv', header=None, names=['timestamp', 'device', 'ip', 'interface', 'status', 'in_mbps', 'out_mbps'])

# Garder SEULEMENT les lignes avec les statuts numériques correctes (1 et 2)
df_clean = df[df['status'].isin(['1', '2'])].copy()

print(f'Total rows before: {len(df)}')
print(f'Total rows after (numeric statuses only): {len(df_clean)}')
print(f'Status counts in clean data:')
print(df_clean['status'].value_counts().sort_index())

# Sauvegarder le CSV nettoyé
df_clean.to_csv('data/network_metrics.csv', index=False, header=False)

print('\nCSV nettoyé et sauvegardé!')
