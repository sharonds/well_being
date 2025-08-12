# Garmin Well-Being MVP Implementation (Personal Use)

PRD: /docs/PRD.md
Execution Plan: /execution_plan.md
Scope: Single-user on-device MVP. Out-of-scope: charts >2 days, ML/AI, cloud sync, notifications, social, monetization, companion mobile app, localization.

## Phases & Tasks Checklist

### Phase 1 – Foundational Slice
- [ ] P0: Project & CI Scaffold (manifest, build workflow, CodeQL)  
  Acceptance: CI build + dummy test pass, CodeQL runs.
- [ ] Core Metric Interfaces (steps + resting HR stubs)  
  Acceptance: Stub returns deterministic values; missing path safe.
- [ ] Prototype Score Engine (subset)  
  Acceptance: Examples A & C scores match PRD; bounds enforced.
- [ ] Recommendation Mapping  
  Acceptance: 3 bands with edge tests (39/40,69/70).
- [ ] Minimal UI + Manual Refresh + Throttle  
  Acceptance: START recompute (>=5 min), UI updates <1s.

### Phase 2 – Metrics Expansion & Persistence
- [ ] Extend Metrics (sleep, stress) with graceful fallback
- [ ] Enhanced Score Engine (full weights) + Example B test
- [ ] Persistence & Day Rollover (delta storage)
- [ ] Delta UI Indicator
- [ ] Expanded Test Vectors (missing combos)

### Phase 3 – Stability & Automation
- [ ] Morning Auto Refresh Logic (single daily trigger)
- [ ] HRV Toggle Integration (if supported)
- [ ] Error Handling & Logging Buffer (cap 20)
- [ ] Throttle Edge Case Tests (day rollover)
- [ ] Regression Suite Consolidation

### Phase 4 – Polish & Observability
- [ ] Debug Screen (hidden trigger)
- [ ] Copy Centralization (bands, disclaimer)
- [ ] Performance Timing Harness (<50ms compute)
- [ ] Documentation Finalization (README, architecture)
- [ ] Final Acceptance & Issue Closure Summary

## Acceptance Criteria (Condensed)
Refer to PRD section 8; each task must add/update tests. Score always 0–100, redistribution correct, band edges validated, persistence correct after Phase 2, auto refresh single-fire after Phase 3.

## Test Plan Overview
- Unit: score calc, normalization, redistribution, bands, persistence, throttle, auto refresh gating.
- Integration (sim): end-to-end refresh with metric stubs.
- Edge: all metrics missing, extremes, 04:59 vs 05:00, rapid refresh attempts, day rollover.

## Bugs / To-do (log here only)
- [ ] (empty)

## Definition of Done
All tasks checked with passing CI + CodeQL; summary comment compares shipped vs PRD; remaining bugs listed.

Assign this Issue to @copilot to initiate Coding Agent after Phase 1 scaffold commit is ready.
