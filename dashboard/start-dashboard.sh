#!/usr/bin/env bash
# Well-Being Dashboard Startup Script
# Ports (host): Grafana ${GRAFANA_PORT:-3001}, InfluxDB ${INFLUXDB_PORT:-8087}

set -euo pipefail

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'

abort() { echo -e "${RED}❌ $1${NC}"; exit 1; }
warn()  { echo -e "${YELLOW}⚠️  $1${NC}"; }
info()  { echo -e "${BLUE}$1${NC}"; }
ok()    { echo -e "${GREEN}✅ $1${NC}"; }

trap 'abort "Script aborted (line $LINENO)"' ERR

echo "🏥 Starting Well-Being Dashboard..."

# ----------------------------------------------------------------------------
# Environment
# ----------------------------------------------------------------------------
if [ ! -f .env ]; then
    abort ".env file not found. Copy .env.example to .env and configure values."
fi

# Safer env loading (supports empty values, ignores comments)
set -o allexport
source <(grep -v '^[[:space:]]*#' .env | sed '/^[[:space:]]*$/d')
set +o allexport

: "${GRAFANA_PORT:=3001}"  # default if not set
: "${INFLUXDB_PORT:=8087}"  # host port mapping (container 8086)

echo "📊 Grafana will be available at: http://localhost:${GRAFANA_PORT}"
echo "📈 InfluxDB will be available at: http://localhost:${INFLUXDB_PORT}"
echo ""

if [[ -z "${GRAFANA_ADMIN_USER:-}" || -z "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
    warn "Grafana admin credentials not set (using defaults - CHANGE BEFORE INGESTING REAL DATA)"
fi

# Security check: Refuse to start with default credentials (addresses ChatGPT-5 security gap)
if [[ "${GRAFANA_ADMIN_USER:-}" == "admin" ]] || [[ "${GRAFANA_ADMIN_PASSWORD:-}" == "admin" ]]; then
    abort "SECURITY RISK: Default Grafana credentials detected. Change GRAFANA_ADMIN_USER and GRAFANA_ADMIN_PASSWORD in .env before starting."
fi

if [[ -z "${INFLUXDB_TOKEN:-}" ]]; then
    warn "InfluxDB token not set (using default - CHANGE BEFORE INGESTING REAL DATA)"
fi

# ----------------------------------------------------------------------------
# Docker Compose detection
# ----------------------------------------------------------------------------
compose_cmd=""
if command -v docker-compose >/dev/null 2>&1; then
    compose_cmd="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    compose_cmd="docker compose"
else
    abort "Neither 'docker-compose' nor 'docker compose' found. Install Docker Desktop or docker-compose."
fi

info "Using compose command: $compose_cmd"

# ----------------------------------------------------------------------------
# Start services
# ----------------------------------------------------------------------------
echo "🚀 Starting containers..."
$compose_cmd up -d

echo "⏳ Waiting for services to be ready..."

# Wait for InfluxDB (container listens on 8086, host forwarded port is $INFLUXDB_PORT)
info "Checking InfluxDB health endpoint..."
until curl -sf "http://localhost:${INFLUXDB_PORT}/ping" >/dev/null 2>&1; do
    sleep 2
    echo "   Still waiting for InfluxDB..."
done
ok "InfluxDB ready"

# Wait for Grafana
info "Checking Grafana health endpoint..."
until curl -sf "http://localhost:${GRAFANA_PORT}/api/health" >/dev/null 2>&1; do
    sleep 2
    echo "   Still waiting for Grafana..."
done
ok "Grafana ready"

echo ""
echo "🎉 Well-Being Dashboard is ready!"
echo ""
echo "📊 Grafana:  http://localhost:${GRAFANA_PORT}"
echo "   Username: ${GRAFANA_ADMIN_USER:-wellbeing_admin}"
echo "   Password: ${GRAFANA_ADMIN_PASSWORD:-wellbeing_secure_password}"
echo ""
echo "📈 InfluxDB: http://localhost:${INFLUXDB_PORT} (container port 8086)"
echo "   Organization: ${INFLUXDB_ORG:-local}"
echo "   Bucket:       ${INFLUXDB_BUCKET:-garmin}"
echo "   Token:        ${INFLUXDB_TOKEN:-(not set)}"
echo ""
echo "� Security reminders:"
echo "   - Change default credentials BEFORE adding real data"
echo "   - Ensure pre-commit guard remains active"
echo ""
echo "🔧 Next steps:"
echo "   1. (Optional) Run parity & validation: PYTHONPATH=. python3 -m dashboard.tests.test_vectors"
echo "   2. (Upcoming) Ingestion script will load JSONL -> InfluxDB"
echo "   3. Access Grafana and import/provision baseline dashboard JSON when added"
echo ""
exit 0