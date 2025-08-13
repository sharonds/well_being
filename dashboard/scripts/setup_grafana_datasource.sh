#!/bin/bash

echo "Setting up InfluxDB datasource in Grafana..."
echo "This script will configure the connection between Grafana and InfluxDB"
echo ""

# InfluxDB connection details
INFLUX_URL="http://wellbeing-influxdb:8086"
INFLUX_ORG="local"
INFLUX_TOKEN="t78smnt4C278Z0AIDKbka8L0a5ELPe1o93K2aArEXf3zHg2rIUH9c6gyTEXCYgJkZBlMaClt8d50-8e1xkQvTg=="
INFLUX_BUCKET="metrics"

echo "📊 Datasource Configuration:"
echo "   URL: $INFLUX_URL"
echo "   Organization: $INFLUX_ORG"
echo "   Bucket: $INFLUX_BUCKET"
echo ""

cat > /tmp/datasource.json <<EOF
{
  "name": "InfluxDB-Wellness",
  "type": "influxdb",
  "typeName": "InfluxDB",
  "access": "proxy",
  "url": "$INFLUX_URL",
  "password": "",
  "user": "",
  "database": "",
  "basicAuth": false,
  "isDefault": true,
  "jsonData": {
    "defaultBucket": "$INFLUX_BUCKET",
    "httpMode": "POST",
    "organization": "$INFLUX_ORG",
    "version": "Flux"
  },
  "secureJsonData": {
    "token": "$INFLUX_TOKEN"
  },
  "readOnly": false
}
EOF

echo "To add this datasource to Grafana:"
echo "1. Go to http://localhost:3001"
echo "2. Navigate to: Configuration → Data Sources → Add data source"
echo "3. Select 'InfluxDB'"
echo "4. Configure with these settings:"
echo "   - Query Language: Flux"
echo "   - URL: http://wellbeing-influxdb:8086"
echo "   - Auth: Turn OFF 'Basic auth'"
echo "   - InfluxDB Details:"
echo "     - Organization: local"
echo "     - Token: $INFLUX_TOKEN"
echo "     - Default Bucket: metrics"
echo "5. Click 'Save & Test'"
echo ""
echo "Then refresh your dashboard at:"
echo "http://localhost:3001/d/feuvemq52yzuoe/well-being-dashboard"