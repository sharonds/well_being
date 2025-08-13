# Phase 3.3: Ops Guardrails & Release Readiness

## Executive Summary
Goal (keep it simple): eliminate residual operational risks and lock release quality signals without adding new product surface.

## Current State (Context)
- Phase 3.1/3.2 completed: unified scoring, boundary tests, central config, privacy scanner, auto‑run normalization, remediation tools; integrity failures at 0% (per latest verification).
- Remaining risks: duplicate guard version-format gap, non‑atomic writes, no retention policy, CI gates not enforcing integrity/privacy.

## Scope (Minimal, High ROI)
P1 (critical to release):
1) Schema Version Normalization in Duplicate Guard
   - Normalize schema_version (strip leading 'v', coerce semver) before duplicate checks.
   - Update migration test to assert same-date duplicates are blocked across version styles.

2) Centralize Band Mapping
   - Add map_score_to_band(score) in engine; refactor fetcher and integrity monitor to use it.
   - Remove any duplicate band logic to prevent future drift.

3) Atomic Writes
   - Write-to-temp + os.replace for ingestion, remediation, and self-healing to prevent partial-file corruption.

4) Retention Policy
   - Config-driven pruning for telemetry and quarantine folders (e.g., RETENTION_DAYS).

5) CI Gates
   - PR checks: privacy scan (no raw metrics in telemetry) and integrity monitor (<1% failure) on sample data; fail PR on violation.

P2 (operational polish):
- Lightweight retry/backoff for Garmin API calls.
- Prometheus/Grafana-friendly metrics export for integrity and auto-run.

## Acceptance Criteria
- Duplicate guard treats 'v1.0.0' and '2.0.0' the same for duplicate detection; updated tests pass.
- Single band-mapping source in engine; integrity monitor shows zero band–score mismatches.
- Atomic write test proves no corruption after simulated write failure.
- Retention job removes files older than RETENTION_DAYS (dry-run + apply modes).
- CI blocks PRs on privacy violations or integrity ≥1% and posts a concise report.

## Deliverables & File Touches
- Code: `dashboard/scripts/duplicate_guard.py`, `dashboard/score/engine.py`, ingestion/remediation writers.
- Tests: `dashboard/tests/test_migration_safety.py` (update), new atomic write and retention tests, quick CI fixtures.
- CI: minimal workflow to run integrity + privacy checks.
- Docs: update Phase 3.2/3.3 references where needed.

## Tasks (P1)
- [ ] Normalize schema_version in duplicate guard and update tests
- [ ] Add map_score_to_band() in engine; refactor fetcher + integrity monitor
- [ ] Introduce atomic write helper and adopt across writers
- [ ] Implement retention script and Config knobs
- [ ] Add CI job: privacy scan + integrity monitor gate

## Blockers
- Current duplicate keying uses (date, schema_version) without normalization → risk of silent duplicates.
- Direct file writes can corrupt on crash/interrupt → need atomic writes.
- No retention → risk of unbounded disk usage.

## Validation Plan
- Unit/integration tests for each item; run remediation/integrity monitors after changes.
- Smoke CI run on PR to verify gates.

## Success Criteria for Phase 3.3
- [ ] All P1 tasks complete and tests passing
- [ ] CI gates active and effective
- [ ] 14‑day integrity failure rate remains <1%
- [ ] No privacy violations in telemetry
- [ ] Sign-off for production release readiness

---

Generated: 2025-08-13
Purpose: Track Phase 3.3 execution with minimal scope and clear goal
