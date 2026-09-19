# Djezzy Backbone Dashboard

A Flask dashboard for viewing the latest SNMP interface throughput snapshot and generating an in-memory PDF report.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. Development debug mode is opt-in: `$env:FLASK_DEBUG = "true"`.

## Data format

The dashboard reads `data/network_metrics.csv`. The collector writes this CSV with the columns `timestamp, device, ip, interface, status, in_mbps, out_mbps`. `status` uses standard SNMP `ifOperStatus` values: `1` is UP and `2` is treated as CRITICAL (down). The dashboard shows the latest measurement for each device/interface pair.

The included CSV is a local capture. For a fresh deployment, run the collector or supply a CSV in the documented format before opening the dashboard.

## SNMP collector

Set credentials through environment variables; do not store the community string in source control.

```powershell
$env:SNMP_DEVICE_IP = "192.0.2.10"
$env:SNMP_COMMUNITY = "your-read-only-community"
$env:SNMP_DEVICE_NAME = "CORE1" # optional
python collector/snmp_collector.py
```

Optional variables: `SNMP_PORT` (default `161`), `SNMP_POLL_INTERVAL` (default `30` seconds), and `SNMP_DATA_FILE`.

## Tests

```powershell
python -B -m unittest discover -v
```

Tests generate PDFs entirely in memory and do not write reports to the repository.
