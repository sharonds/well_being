#!/bin/bash
# Well-Being Dashboard Startup Script
# Uses ports 3001 (Grafana) and 8087 (InfluxDB) to avoid conflicts

set -e

echo "🏥 Starting Well-Being Dashboard..."
echo "📊 Grafana will be available at: http://localhost:3001"
echo "📈 InfluxDB will be available at: http://localhost:8087"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "💡 Please copy .env.example to .env and configure your credentials"
    exit 1
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required variables
if [ -z "$GRAFANA_ADMIN_USER" ] || [ -z "$GRAFANA_ADMIN_PASSWORD" ]; then
    echo "⚠️  Warning: Grafana credentials not set in .env"
    echo "   Using defaults (change these in production!)"
fi

if [ -z "$INFLUXDB_TOKEN" ]; then
    echo "⚠️  Warning: InfluxDB token not set in .env"
    echo "   Using default token (change this in production!)"
fi

echo "🚀 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for InfluxDB
echo "   Checking InfluxDB..."
until curl -sf http://localhost:${INFLUXDB_PORT:-8087}/ping > /dev/null 2>&1; do
    sleep 2
    echo "   Still waiting for InfluxDB..."
done
echo "✅ InfluxDB ready"

# Wait for Grafana
echo "   Checking Grafana..."
until curl -sf http://localhost:${GRAFANA_PORT:-3001}/api/health > /dev/null 2>&1; do
    sleep 2
    echo "   Still waiting for Grafana..."
done
echo "✅ Grafana ready"

echo ""
echo "🎉 Well-Being Dashboard is ready!"
echo ""
echo "📊 Grafana: http://localhost:${GRAFANA_PORT:-3001}"
echo "   Username: ${GRAFANA_ADMIN_USER:-wellbeing_admin}"
echo "   Password: ${GRAFANA_ADMIN_PASSWORD:-wellbeing_secure_password}"
echo ""
echo "📈 InfluxDB: http://localhost:${INFLUXDB_PORT:-8087}"
echo "   Organization: ${INFLUXDB_ORG:-local}"
echo "   Bucket: ${INFLUXDB_BUCKET:-garmin}"
echo ""
echo "🔧 Next steps:"
echo "   1. Configure your Garmin credentials in .env"
echo "   2. Run: PYTHONPATH=. python3 dashboard/scripts/setup_dashboard.py"
echo "   3. View your dashboard at http://localhost:${GRAFANA_PORT:-3001}"