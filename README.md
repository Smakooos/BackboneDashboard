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

The dashboard reads `data/network_metrics.csv`. The collector writes this CSV with the columns `timestamp, device, ip, interface, status, in_mbps, out_mbps`. `status` uses standard SNMP `ifOperStatus` values: `1` is UP and `2` is treated as CRITICAL (down). The dashboard shows the latest measurement for each `(device, interface)` pair, so identically named interfaces on different routers remain distinct.

The included CSV is a local capture. For a fresh deployment, run the collector or supply a CSV in the documented format before opening the dashboard.

## SNMP collector

The collector polls these GNS3 lab routers every 10 seconds by default:

- `CORE1` — `192.168.80.10`
- `EDGE1` — `10.0.1.1`
- `EDGE2` — `10.0.1.9`
- `CORE2` — `10.0.1.18`

Set the read-only community through an environment variable; the lab default is `BackboneRead`.

```powershell
$env:SNMP_COMMUNITY = "your-read-only-community"
python collector/snmp_collector.py
```

Optional variables: `SNMP_PORT` (default `161`), `SNMP_POLL_INTERVAL` (default `10` seconds), and `SNMP_DATA_FILE`.

## Tests

```powershell
python -B -m unittest discover -v
```

Tests generate PDFs entirely in memory and do not write reports to the repository.
