#!/usr/bin/env python3
"""Grafana dashboard provisioning script.
Creates/updates the Well-Being dashboard via Grafana API.

Usage:
  PYTHONPATH=. python3 dashboard/scripts/provision_grafana.py

Prerequisites:
- Grafana running on localhost:3000
- Admin credentials configured in .env
- InfluxDB data source configured in Grafana

Environment (.env):
  GRAFANA_URL=http://localhost:3000
  GRAFANA_ADMIN_USER=admin
  GRAFANA_ADMIN_PASSWORD=your_password
"""
from __future__ import annotations
import os, sys, json, pathlib
import requests
from typing import Dict, Any

def load_env():
    """Load environment variables from .env file."""
    env_path = pathlib.Path(".env")
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def get_grafana_config():
    """Get Grafana configuration from environment."""
    env_vars = load_env()
    
    config = {
        "url": env_vars.get("GRAFANA_URL") or os.getenv("GRAFANA_URL", "http://localhost:3000"),
        "user": env_vars.get("GRAFANA_ADMIN_USER") or os.getenv("GRAFANA_ADMIN_USER", "admin"),
        "password": env_vars.get("GRAFANA_ADMIN_PASSWORD") or os.getenv("GRAFANA_ADMIN_PASSWORD", "")
    }
    
    if not config["password"]:
        raise ValueError("GRAFANA_ADMIN_PASSWORD not found in .env or environment")
    
    return config

def load_dashboard_json() -> Dict[str, Any]:
    """Load dashboard JSON from file."""
    dashboard_path = pathlib.Path("dashboard/grafana/wellbeing-dashboard.json")
    if not dashboard_path.exists():
        raise FileNotFoundError(f"Dashboard JSON not found: {dashboard_path}")
    
    with open(dashboard_path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_grafana_health(config: Dict[str, str]) -> bool:
    """Check if Grafana is accessible."""
    try:
        response = requests.get(f"{config['url']}/api/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_or_create_influx_datasource(config: Dict[str, str]) -> str:
    """Get or create InfluxDB data source, return UID."""
    auth = (config["user"], config["password"])
    
    # Check existing datasources
    try:
        response = requests.get(f"{config['url']}/api/datasources", auth=auth)
        response.raise_for_status()
        datasources = response.json()
        
        # Look for InfluxDB datasource
        for ds in datasources:
            if ds.get("type") == "influxdb" and "garmin" in ds.get("database", "").lower():
                print(f"✅ Found existing InfluxDB datasource: {ds['name']} (UID: {ds['uid']})")
                return ds["uid"]
    
    except requests.RequestException as e:
        print(f"Warning: Could not check existing datasources: {e}")
    
    # Create new datasource
    env_vars = load_env()
    influx_config = {
        "name": "InfluxDB-Garmin",
        "type": "influxdb", 
        "url": env_vars.get("INFLUXDB_URL", "http://localhost:8086"),
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "version": "Flux",
            "organization": env_vars.get("INFLUXDB_ORG", "local"),
            "defaultBucket": env_vars.get("INFLUXDB_BUCKET", "garmin")
        },
        "secureJsonData": {
            "token": env_vars.get("INFLUXDB_TOKEN", "")
        }
    }
    
    try:
        response = requests.post(f"{config['url']}/api/datasources", 
                               auth=auth, 
                               json=influx_config)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Created InfluxDB datasource: {result['datasource']['name']} (UID: {result['datasource']['uid']})")
        return result["datasource"]["uid"]
    
    except requests.RequestException as e:
        print(f"❌ Failed to create InfluxDB datasource: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        raise

def provision_dashboard(config: Dict[str, str], dashboard_data: Dict[str, Any]) -> bool:
    """Provision dashboard to Grafana."""
    auth = (config["user"], config["password"])
    
    # Prepare dashboard for API
    payload = {
        "dashboard": dashboard_data["dashboard"],
        "overwrite": True,
        "message": "Provisioned via automation script"
    }
    
    try:
        response = requests.post(f"{config['url']}/api/dashboards/db",
                               auth=auth,
                               json=payload)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Dashboard provisioned successfully")
        print(f"   URL: {config['url']}{result['url']}")
        print(f"   UID: {result['uid']}")
        print(f"   Version: {result['version']}")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Failed to provision dashboard: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return False

def main():
    print("🚀 Grafana Dashboard Provisioning")
    print("=" * 40)
    
    try:
        # Load configuration
        config = get_grafana_config()
        print(f"📊 Grafana URL: {config['url']}")
        
        # Check Grafana health
        if not check_grafana_health(config):
            print(f"❌ Grafana not accessible at {config['url']}")
            print("   Make sure Grafana is running and accessible")
            return 1
        
        print("✅ Grafana is accessible")
        
        # Set up InfluxDB data source
        print("\n🔌 Setting up InfluxDB data source...")
        datasource_uid = get_or_create_influx_datasource(config)
        
        # Load dashboard JSON
        print("\n📋 Loading dashboard configuration...")
        dashboard_data = load_dashboard_json()
        
        # Update dashboard to use the correct datasource
        # Note: In a production setup, you'd update the dashboard JSON 
        # to reference the correct datasource UID
        
        # Provision dashboard
        print("\n🚀 Provisioning dashboard...")
        if provision_dashboard(config, dashboard_data):
            print("\n✅ Dashboard provisioning complete!")
            print(f"🎯 Access your dashboard: {config['url']}/d/wellbeing/wellbeing-dashboard")
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())