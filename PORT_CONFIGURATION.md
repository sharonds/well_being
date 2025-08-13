# Port Configuration Guide

Your well-being dashboard is configured to use **different ports** to avoid conflicts with your existing app on port 3000.

## Port Allocation

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Grafana** | **3001** | http://localhost:3001 | Well-being dashboard UI |
| **InfluxDB** | **8087** | http://localhost:8087 | Time-series database |

## Quick Start

1. **Configure credentials** in `.env`:
   ```bash
   # Copy example and edit
   cp .env .env.local  # if needed
   # Edit .env with your credentials
   ```

2. **Start the dashboard**:
   ```bash
   ./start-dashboard.sh
   ```

3. **Access your dashboard**:
   - **Grafana**: http://localhost:3001
   - **InfluxDB**: http://localhost:8087

## Environment Variables (in .env)

```bash
# Ports (configured to avoid conflicts)
GRAFANA_PORT=3001
INFLUXDB_PORT=8087
INFLUXDB_URL=http://localhost:8087

# Credentials (CHANGE THESE!)
GRAFANA_ADMIN_USER=your_grafana_user
GRAFANA_ADMIN_PASSWORD=your_grafana_password
INFLUXDB_ADMIN_USER=your_influx_user
INFLUXDB_ADMIN_PASSWORD=your_influx_password
INFLUXDB_TOKEN=your_influx_token
```

## Why These Ports?

- **Port 3001**: Standard alternative to 3000, commonly used for secondary apps
- **Port 8087**: Alternative to standard InfluxDB port 8086, avoids any potential conflicts

## Verification

After starting:
```bash
# Check services are running on correct ports
curl http://localhost:3001/api/health  # Grafana
curl http://localhost:8087/ping        # InfluxDB
```

## Integration

All dashboard scripts automatically use these ports via environment variables:
- `dashboard/scripts/ingest_influxdb.py` → uses `INFLUXDB_URL`
- `dashboard/scripts/provision_grafana.py` → uses `GRAFANA_PORT` 
- Docker Compose → uses both port variables

No code changes needed - just configure your `.env` file and run `./start-dashboard.sh`!