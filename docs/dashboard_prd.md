# Product Requirements Document (Dashboard Extension)

## 0. Meta
- Product Name: Garmin Well-Being Dashboard MVP
- Owner: You (personal project)
- Created: 2025-08-13
- Status: Phase 0 FOUNDATION / Phase 1 PLANNING
- Canonical Location: /docs/dashboard_prd.md
- Relation: Extends core wearable app PRD (/docs/PRD.md) – keeps single-user, personal, offline scope.

## 1. Purpose / Problem Statement
Provide deeper insight into daily readiness trends than the watch UI can offer by surfacing: (a) historical score trajectory, (b) per-metric contribution breakdown, and (c) data quality / completeness – enabling faster iteration on the scoring model while preserving privacy and simplicity.

## 2. Primary User & Use Case
- User: Same single individual as core app.
- Use Cadence: Brief daily review + weekly retrospective.
- Environment: Local machine (no cloud), private data, offline-capable once synced.
- Key Decisions Supported:
       1. “Why did today’s score change?” (metric contribution deltas)
       2. “Is my data trustworthy?” (missing metrics, API error rate)
       3. “Are trends improving?” (rolling averages)

## 3. MVP Vision (Concise)
Minimum viable dashboard delivers within one evening:
1. Local Docker (garmin-grafana) stack running.
2. 30 days of raw metrics ingested.
3. Well-being score & per-metric contributions computed from ingested data (algorithm parity with device: same normalization, weights, redistribution, rounding rule floor(x+0.5)).
4. Four baseline Grafana panels: Score Timeline, Metric Contributions (stacked), Data Completeness (% metrics present), Error Code Frequency.
5. Everything versioned locally; no external publishing of personal data.

## 4. Strategic Rationale
| Constraint | On-Device Limitation | Dashboard Advantage |
|-----------|----------------------|---------------------|
| Screen space | 1–2 metrics visible | Multi-panel analytical view |
| History window | Short (7 day planned) | 30–90 day rolling insights |
| Iteration speed | Rebuild & deploy CIQ | Hot reload / config change |
| Explainability | Single score only | Contribution decomposition |
| Data validation | Minimal logging | Panels surface gaps/errors |

First principle: Only build panels that change decisions; defer “nice eye candy”.

## 5. Non-Goals (MVP)
- Multi-user / sharing
- Cloud hosting / remote access
- Mobile responsive tuning
- ML, anomaly detection, alerts
- Cross-platform health aggregation
- Real-time streaming (<1h freshness not required)

## 6. Feature List (MVP Scope – MUST HAVES ONLY)
| ID | Feature | Description | Acceptance (Binary) |
|----|---------|-------------|---------------------|
| F1 | Local Stack Bootstrap | Launch garmin-grafana (InfluxDB + Grafana) | `docker compose up` succeeds <15 min |
| F2 | Historical Import | Ingest ≥30 days steps, resting HR, sleep, stress, HRV(if present) | All days show metrics or marked missing |
| F3 | Score Parity Engine | Python port of wearable algorithm (flags, redistribution, rounding) | Sample vector A/B/C scores match device/unit tests |
| F4 | Contribution Computation | Persist per-metric weighted contributions + active weights | Sum(contrib)=raw_score±0.5 rounding tolerance |
| F5 | Core Panels | 4 baseline panels (Score Timeline, Contributions, Completeness, Error Codes) | Panels render without manual query edits |
| F6 | Data Quality Layer | Compute & store missing metric list + error codes | Completeness panel shows % present/day |
| F7 | Security & Privacy Safeguards | Local credentials + no PII leakage to repo | README warning + .env usage |

Deferred (Phase 2+): Delta Explanation panel (per-day delta breakdown), Rolling Averages, Correlation matrix, Recommendation panel, Weight simulation toggle.

### 6.1 Implementation Parameters
| Item | Decision | Rationale |
|------|----------|-----------|
| Stack | garmin-grafana upstream | Reuse proven ingestion & infra |
| DB | InfluxDB | Native to upstream; time-series optimized |
| Scoring Service | Lightweight Python module | Easier unit tests & parity with Monkey C |
| Data Granularity | Daily (midnight-local aggregated) | Aligns with wearable score cadence |
| Export Schema | JSON line per day before ingestion | Human diffable, versionable |
| Formula Version | `WB_FORMULA_VERSION` constant | Audit & backward compatibility |
| Automation | Micro-issues (single file / panel) | High success rate, low blast radius |

## 7. Phased Delivery (Iterative)
### Phase 0 (Foundation – IN PROGRESS)
- Clone & run upstream stack
- **SECURITY HARDENING (CRITICAL)**:
  - [ ] Change Grafana default credentials (admin/admin)
  - [ ] Change InfluxDB default credentials (influxdb_user/influxdb_secret_password)
  - [ ] Set token directory permissions to 700 (not 777)
  - [x] Configure .env with API credentials (never commit)
  - [x] Verify no PII in commit history
- **API SAFETY CONFIGURATION**:
  - [ ] Set conservative sync interval (24h minimum)
  - [ ] Test with dedicated Garmin account first
  - [ ] Implement respectful rate limiting
- Validate metrics arrive (spot-check steps, resting HR)
- Document credential handling (.env)

### Phase 1 (Minimum Insight) – Target First Review
- [x] Implement Python scoring + verify vectors
- [x] Generate synthetic historical scores + contributions
- [ ] Ingest into InfluxDB (measurement: `wb_score`, `wb_contrib`)
- [ ] Build 4 baseline panels (JSON provisioned)
- [ ] Add completeness & error code aggregation

### Phase 2 (Explainability & Quality)
- Delta decomposition (per metric delta day-over-day)
- Rolling 7 & 30 day averages panel
- Recommendation band overlay (color zones on timeline)
- Schema validator + CI check (automation issue)

### Phase 3 (Refinement)
- Correlation matrix (norm metrics vs score)
- Weight toggle simulation (exclude metric “what-if”) 
- Performance profiling (query latency targets)

## 8. Detailed Requirements (Must-Have Focus)
### 8.1 Data Acquisition
Minimal set: steps, restingHR, sleepHours, stress, hrv (optional). Each record tagged with presence/absence.

### 8.2 Score Parity
Exact reproduction of: normalization caps, redistribution formula, rounding floor(x+0.5), feature flags (sleep, stress, HRV). Failing any parity test blocks Phase 1 completion.

### 8.3 Daily Record Schema (Pre-Ingest JSON)
```
{
       "date": "YYYY-MM-DD",
       "compute_ts_utc": 1691904000000,
       "score": 88,
       "band": "Go for it",
       "metrics_raw": {"steps":12000,"rhr":48,"sleep_h":7,"stress":35,"hrv":70},
       "metrics_norm": {"steps":1.0,"rhr_inv":0.8,"sleep":0.875,"stress_inv":0.65,"hrv":0.625},
       "weights_active": {"steps":0.40,"rhr":0.30,"sleep":0.20,"stress":0.10},
       "contrib": {"steps":0.40,"rhr":0.24,"sleep":0.175,"stress":0.065},
       "missing": [],
       "flags": {"sleep":true,"stress":true,"hrv":false},
       "formula_version": "1.0.0",
       "run_mode": "batch",
       "error_codes": [],
       "tz_offset_min": -420
}
```
Integrity rule: abs(sum(contrib.values) - (score/100.0)) < 0.01 after inverse rounding.

### 8.4 InfluxDB Measurements (Phase 1)
- `wb_score` fields: score(int), band(tag), formula_version(tag)
- `wb_contrib` fields: steps, rhr, sleep, stress, hrv (floats); tags: date
- `wb_quality` fields: metrics_present(int), metrics_expected(int), missing_count(int), error_count(int)

### 8.5 Panels (Phase 1 Definition)
Panel | Source | Goal
------|--------|-----
Score Timeline | wb_score.score | Identify overall trend
Contributions Stacked | wb_contrib.* | Explain daily score composition
Data Completeness | wb_quality.* | Detect ingestion or device gaps
Error Codes | wb_quality.error_count (grouped) | Surface systemic acquisition issues

### 8.6 Automation Alignment
Micro-Issues examples:
- `dashboard-score-service` (Python parity module)
- `dashboard-contrib-panels` (Grafana JSON add)
- `dashboard-quality-panel` (completeness)
- `dashboard-error-panel` (error codes)
Each: single file or focused change; branch auto-<task>-<timestamp>; PR template includes parity checklist.

### 8.7 Security & Privacy
- Credentials only in `.env` (excluded via .gitignore).
- Personal data (raw exports) never committed; only derived schema sample with synthetic numbers in open-source repo.
- Warning banner in README + PR template item.
- **Mandatory security hardening checklist** documented and completed before data ingestion.
- **Conservative API usage**: 24-hour minimum sync intervals with exponential backoff on failures.

## 9. Acceptance Criteria (Phase 1)
**Phase 0 Prerequisites (Security Gate)**:
0. All Phase 0 security hardening items completed and verified

**Phase 1 Delivery**:
1. Stack starts: `docker compose up` yields healthy Grafana/Influx in <15 min.
2. 30 consecutive days ingest produce ≥95% non-missing primary metrics (sleep/HRV allowed lower).
3. Score parity: A(65), B(88), C(25) match within exact integers.
4. Contribution sum integrity passes for all ingested days.
5. Four panels render, no manual query edits required.
6. Data completeness panel shows each day; missing days explicitly zeroed not silently absent.
7. Error panel lists codes when synthetic failures injected (test harness day with forced null metric).
8. No credentials or personal raw JSON committed.
9. **API usage demonstrates respectful patterns** (24h intervals, proper backoff).

## 10. Testing Strategy
- Parity tests (vectors) – automated Python unit tests.
- Schema validator – fail CI if required keys absent / sum mismatch.
- Panel provision test – lint dashboard JSON for required panel UIDs.
- Synthetic missing-day injection – ensure completeness panel reflects gap.

## 11. Success Metrics
Metric | Target (Phase 1)
-------|-----------------
Setup time | <30 min first run
Parity failures | 0
Days ingested coverage | ≥95% core metrics
Panel load time | <2s local
Contribution integrity failures | 0

## 12. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Garmin account suspension** | **Critical - data loss** | Use dedicated test account; conservative 24h sync intervals; monitor account health |
| **Default credentials exposure** | **Critical - data breach** | Phase 0 security hardening checklist (mandatory) |
| Unofficial API breakage | High - Data gap | Cache raw JSON locally; fallback manual export; implement exponential backoff |
| Parity drift after wearable change | Medium - Misleading trends | Formula version bump + automated test gate |
| Token file exposure | Medium - Account compromise | Secure file permissions (700); .env credential storage |
| Schema creep | Low - Complexity | Freeze Phase 1 schema; append only in later phases |
| Sensitive data commit | Low - Privacy breach | Pre-commit hook (deny real dates / large step counts) |
| Panel sprawl | Low - Loss of focus | Hard cap: 4 panels Phase 1 |

## 13. Open Questions
- Acceptable HRV missing rate before panel annotation?
- Do we need timezone normalization for travel now or defer?
- Minimum retention window (90 days vs indefinite)?

## 14. Out-of-Scope (Phase 1)
Alerts, ML anomaly detection, sharing links, mobile layout, what-if simulations, multi-user.

## 15. Definition of Done (Phase 1)
- All Phase 1 AC met & tests green
- Parity report attached to PR
- Dashboard JSON committed & loads cleanly
- README updated with setup + privacy warning

Medical Disclaimer: Personal experimentation only; not medical advice.

## 16. Architecture (Simplified Phase 1)
```
Garmin (Unofficial API) -> Ingestion Script -> JSON Daily Records -> Score/Contrib Compute -> InfluxDB -> Grafana Panels
```

## 17. Future (Phase 2+ Preview – Not Commitments)
- Delta decomposition panel
- Rolling averages overlays
- Correlation & weight simulation
- Automated export from device (optional)

---
This dashboard PRD intentionally narrows initial scope to rapidly inspect readiness trends with explainability, then iteratively layers sophistication only if insights drive new decisions.