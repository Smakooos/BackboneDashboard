import pandas as pd
from datetime import datetime, timedelta

# Créer des données pour les 4 routeurs avec des statuts mixtes UP/DOWN
devices = [
    {"name": "CORE1", "ip": "192.168.80.10"},
    {"name": "EDGE1", "ip": "10.0.1.1"},
    {"name": "EDGE2", "ip": "10.0.1.9"},
    {"name": "CORE2", "ip": "10.0.1.18"},
]

interfaces_per_device = 20

# Générer 20 snapshots pour avoir des données historiques
data = []
base_time = datetime(2026, 9, 19, 12, 0, 0)

# Pattern pour chaque device: certaines interfaces UP, d'autres DOWN
interface_patterns = {
    "CORE1": {"up": 11, "down": 9},    # 11 UP, 9 DOWN
    "EDGE1": {"up": 5, "down": 15},    # 5 UP, 15 DOWN
    "EDGE2": {"up": 5, "down": 15},    # 5 UP, 15 DOWN
    "CORE2": {"up": 9, "down": 11},    # 9 UP, 11 DOWN
}

for ts_offset in range(0, 200, 10):  # 20 snapshots
    timestamp = base_time - timedelta(seconds=ts_offset)
    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
    
    for device in devices:
        device_name = device["name"]
        device_ip = device["ip"]
        pattern = interface_patterns[device_name]
        
        # Générer interfaces UP
        for i in range(pattern["up"]):
            interface = f"FastEthernet0/{i}" if i < 8 else f"FastEthernet1/{i-8}"
            data.append({
                "timestamp": timestamp_str,
                "device": device_name,
                "ip": device_ip,
                "interface": interface,
                "status": "1",  # UP
                "in_mbps": 0.0,
                "out_mbps": 0.0
            })
        
        # Générer interfaces DOWN
        for i in range(pattern["down"]):
            interface_idx = pattern["up"] + i
            interface = f"FastEthernet1/{interface_idx - 8}" if interface_idx >= 8 else f"FastEthernet0/{interface_idx}"
            data.append({
                "timestamp": timestamp_str,
                "device": device_name,
                "ip": device_ip,
                "interface": interface,
                "status": "2",  # DOWN
                "in_mbps": 0.0,
                "out_mbps": 0.0
            })
        
        # Ajouter les interfaces spéciales (Vlan, Loopback)
        for special in ["Vlan1", "Loopback0"]:
            data.append({
                "timestamp": timestamp_str,
                "device": device_name,
                "ip": device_ip,
                "interface": special,
                "status": "1",  # Toujours UP
                "in_mbps": 0.0,
                "out_mbps": 0.0
            })

df = pd.DataFrame(data)

# Sauvegarder
df.to_csv('data/network_metrics.csv', index=False, header=False)

print(f"CSV recréé avec {len(df)} lignes")
print(f"Devices: {df['device'].unique()}")
print(f"\nInterfacespar device:")
for device in ["CORE1", "EDGE1", "EDGE2", "CORE2"]:
    device_df = df[df['device'] == device]
    status_counts = device_df['status'].value_counts().to_dict()
    print(f"  {device}: {len(device_df)} interfaces | Status 1 (UP): {status_counts.get('1', 0)} | Status 2 (DOWN): {status_counts.get('2', 0)}")
