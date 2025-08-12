# Garmin Well-Being MVP Implementation (Personal Use)

PRD: /docs/PRD.md  
Execution Plan: /execution_plan.md  
Scope: Single-user on-device MVP. Out-of-scope: charts >2 days, ML/AI, cloud sync, notifications, social, monetization, companion mobile app, localization.

## Phases & Tasks Checklist

### Phase 1 – Foundational Slice
- [ ] **P0: Project & CI Scaffold** (manifest, build workflow, CodeQL)  
  Acceptance: CI build + dummy test pass, CodeQL runs. Ref: PRD Section 13 (Definition of Done)
- [ ] **Core Metric Interfaces** (steps + resting HR stubs)  
  Acceptance: Stub returns deterministic values; missing path safe. Ref: PRD Section 7.1 & 8.2
- [ ] **Prototype Score Engine** (subset with weight redistribution)  
  Acceptance: Examples A & C scores match PRD Section 14.1; bounds enforced. Implement redistribution algorithm per PRD Section 7.2. Ref: PRD Section 8.1
- [ ] **Recommendation Mapping**  
  Acceptance: 3 bands with edge tests (39/40, 69/70). Ref: PRD Section 7.3 & 8.5
- [ ] **Minimal UI + Manual Refresh + Throttle**  
  Acceptance: START recompute (>=5 min), UI updates <1s. Ref: PRD Section 7.7 (UI Layout) & 8.3

### Phase 2 – Metrics Expansion & Persistence
- [ ] **Extend Metrics** (sleep, stress) with graceful fallback  
  Ref: PRD Section 7.1
- [ ] **Enhanced Score Engine** (full weights) + Example B test  
  Acceptance: Example B from PRD Section 14.1 validates to score 88
- [ ] **Persistence & Day Rollover** (delta storage)  
  Ref: PRD Section 7.4 & 8.6
- [ ] **Delta UI Indicator**  
  Ref: PRD Section 7.7
- [ ] **Expanded Test Vectors** (missing combos)  
  Mandatory: All test cases from PRD Section 14.1 (Examples A, B, C)

### Phase 3 – Stability & Automation
- [ ] **Morning Auto Refresh Logic** (single daily trigger)  
  Ref: PRD Section 7.5 & 8.4
- [ ] **HRV Toggle Integration** (if supported)  
  Ref: PRD Section 7.6 & 8.7
- [ ] **Error Handling & Logging Buffer** (cap 20)  
  Ref: PRD Section 7.8
- [ ] **Throttle Edge Case Tests** (day rollover)  
  Ref: PRD Section 8.8
- [ ] **Regression Suite Consolidation**  
  Ref: PRD Section 9

### Phase 4 – Polish & Observability
- [ ] **Debug Screen** (hidden trigger)  
  Ref: PRD Section 7.10
- [ ] **Copy Centralization** (bands, disclaimer)  
  Ref: PRD Section 7.3
- [ ] **Performance Timing Harness** (<50ms compute)  
  Ref: PRD Section 7.9
- [ ] **Documentation Finalization** (README, architecture)
- [ ] **Final Acceptance & Issue Closure Summary**

## Acceptance Criteria (Enhanced)
Each task must validate against specific PRD sections referenced above. Score always 0–100, redistribution correct per Section 7.2, band edges validated per Section 7.3, persistence correct after Phase 2 per Section 7.4, auto refresh single-fire after Phase 3 per Section 7.5.

## Test Plan Overview
- **Unit**: score calc, normalization, redistribution (PRD Section 7.2), bands (Section 7.3), persistence (Section 7.4), throttle, auto refresh gating
- **Integration** (sim): end-to-end refresh with metric stubs
- **Edge**: all metrics missing, extremes, 04:59 vs 05:00, rapid refresh attempts, day rollover
- **Mandatory Test Vectors**: PRD Section 14.1 Examples A, B, C must pass

## Bugs / To-do (log here only)
- [ ] (empty)

## Definition of Done
All tasks checked with passing CI + CodeQL; summary comment compares shipped vs PRD; remaining bugs listed. Each phase must validate against referenced PRD sections.

**Coding Agent Instructions**: Implement tasks sequentially, validating each against specified PRD sections. Use Examples A, B, C from Section 14.1 as acceptance tests.
