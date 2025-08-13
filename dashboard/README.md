# Dashboard Development (Parity & Phase 1)

## Purpose
Local analytics extension for readiness score explainability (trend, contributions, completeness, errors) — mirrors wearable algorithm.

## Layout
```
/dashboard
  score/engine.py        # Python parity engine
  tests/test_vectors.py  # Example A/B/C parity tests
  schema/daily_record.schema.json  # Daily record JSON schema
```

## Quick Run (Manual)
```bash
# From project root:
PYTHONPATH=/Users/sharonsciammas/well_being python3 dashboard/score/engine.py          # Show example scores
PYTHONPATH=/Users/sharonsciammas/well_being python3 dashboard/tests/test_vectors.py    # Run parity assertions
```

Expected output:
```
{'A': 65, 'B': 88, 'C': 25}
All vector tests passed.
```

## Flags
Match wearable feature flags:
- enable_sleep
- enable_stress
- enable_hrv (placeholder)

## Contribution Integrity
Sum(contrib) ~= score/100 (after inverse rounding). Will enforce with validator script (future micro-issue).

## Next Steps
1. Integrate schema validator & integrity check.
2. Historical export script producing JSON lines conforming to schema.
3. InfluxDB ingestion scripts for wb_score, wb_contrib, wb_quality.
4. Provision baseline Grafana panels via JSON.

## Historical Export (Synthetic Placeholder)
Generate 30 days synthetic records (will later be replaced by real fetch):
```bash
PYTHONPATH=. python3 dashboard/scripts/export_historical.py dashboard/tests/synth_export.jsonl
PYTHONPATH=. python3 dashboard/scripts/validate_daily_records.py dashboard/tests/synth_export.jsonl
```
You should see `Exported 30 synthetic days` then `VALIDATION PASSED`.

## Validation Script
Run schema + integrity validation on sample records:
```bash
PYTHONPATH=. python3 dashboard/scripts/validate_daily_records.py dashboard/tests/sample_daily_records.jsonl
```
Expected: `VALIDATION PASSED`

## InfluxDB Ingestion (Phase 1)
Ingest validated JSON Lines records into InfluxDB for Grafana visualization:
```bash
# Prerequisites: InfluxDB running, .env configured with INFLUXDB_TOKEN
PYTHONPATH=. python3 dashboard/scripts/ingest_influxdb.py dashboard/tests/synth_export.jsonl
```
Creates measurements: `wb_score`, `wb_contrib`, `wb_quality`

### Complete Pipeline Demo
```bash
PYTHONPATH=. python3 dashboard/scripts/demo_ingestion.py
```
Runs full pipeline: export → validate → ingest. Requires InfluxDB setup.

## Grafana Dashboard (Phase 1 Complete)
4 baseline panels for well-being score analysis and monitoring:

### Manual Dashboard Import
```bash
# Import pre-built dashboard JSON
# Grafana UI: + → Import → Upload dashboard/grafana/wellbeing-dashboard.json
```

### Automated Provisioning
```bash
# Prerequisites: Grafana running, .env with GRAFANA_ADMIN_PASSWORD
PYTHONPATH=. python3 dashboard/scripts/provision_grafana.py
```
Auto-creates InfluxDB datasource + provisions dashboard

### Complete Setup (Recommended)
```bash  
# Full pipeline: data generation → ingestion → dashboard provisioning
PYTHONPATH=. python3 dashboard/scripts/setup_dashboard.py
```
One-command setup for complete dashboard experience.

### 📊 Dashboard Panels
1. **Score Timeline**: Daily score trends with threshold colors
2. **Metric Contributions**: Stacked view of per-metric contributions  
3. **Data Completeness**: Percentage of available metrics per day
4. **Error Code Frequency**: System health and data quality monitoring

Access: http://localhost:3000/d/wellbeing/wellbeing-dashboard
## Notes
- Do not store personal raw exports in repo; use `private/` directory.
- Formula version pinned via WB_FORMULA_VERSION (.env).
