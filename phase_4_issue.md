# Phase 4.0: Production Rollout & Observability

## Executive Summary
Goal (keep it simple): ship a safe, observable production rollout with a 30‑day burn‑in and actionable alerts.

## Current Context
- Phase 3.1–3.3 complete: unified scoring, guardrails, CI gates, retention; integrity rate at 0%.
- Focus now shifts from correctness to stable operations, visibility, and response.

## Scope (Minimal, High ROI)
P1 (release blockers):
1) 30‑Day Burn‑In Schedule
   - Daily integrity + remediation job; freeze formula/config unless incident.
2) Observability & Alerts
   - Export metrics (integrity rate, auto‑run %, remediation actions).
   - Alerts for integrity ≥1%, privacy violations, ingestion failures.
3) SLOs & Runbooks
   - Publish SLOs (e.g., integrity <1%, ingestion success >99%).
   - Create incident/runbook docs and define ownership/on‑call.
4) Release Hygiene
   - Final release checklist (gates, backups, retention verified) and sign‑off flow.

P2 (nice‑to‑have):
- Dashboard panels for SLOs; weekly ops report automation.

## Acceptance Criteria
- No integrity alerts during 30‑day burn‑in; 14‑day integrity <1% throughout.
- Alerts reach the chosen channel with remediation summary within 2 minutes of breach.
- SLO dashboard live; runbooks committed under `docs/runbooks/` and linked in README.
- Release checklist completed and signed off for GA.

## Deliverables & File Touches
- Metrics/alerts: `dashboard/scripts/ops/metrics_exporter.py`, `dashboard/scripts/ops/alerts.py` (or reuse existing infra), Grafana panels.
- Scheduling: cron/systemd/GitHub Actions workflow for daily integrity+remediation.
- Docs: `docs/runbooks/` (incident, remediation, rollback), `docs/SLOs.md`, `RELEASE_CHECKLIST.md`.

## Tasks (P1)
- [ ] Add/export ops metrics (integrity, auto‑run, remediation counts)
- [ ] Implement alerting for integrity ≥1%, privacy violations, ingestion failures
- [ ] Schedule daily integrity+remediation job (burn‑in window)
- [ ] Publish SLOs and owner/on‑call; add runbooks
- [ ] Add final release checklist and wire to CI (block release if incomplete)

## Risks / Blockers
- Alert destination + credentials (Slack/Email) provisioning
- Secrets management for CI/alerts (tokens, webhooks)
- External dependencies (Garmin API stability, rate limits, MFA flows)

## Validation Plan
- Simulate threshold breaches; verify alert delivery + runbook linkage
- CI job to sanity‑check metrics endpoint and alert rules
- Weekly burn‑in review: integrity trend, incidents, MTTR

## Success Criteria (Exit)
- [ ] 30‑day burn‑in completed with <1% integrity failures and no unresolved incidents
- [ ] Alerts reliably delivered; ops response within target MTTR
- [ ] SLO dashboard live; runbooks current
- [ ] Release checklist signed; system declared GA

---
Generated: 2025‑08‑13
Purpose: Track Phase 4 execution with minimal scope and clear goal
