## Status Update (12 Aug 2025)
✅ Phase 1 COMPLETE (merged PR #2) — score engine (steps + resting HR), recommendation bands, manual refresh + throttle, baseline tests.
🚧 Phase 2 IN PROGRESS — adding sleep, stress, persistence, delta UI, Example B test.
Repository: https://github.com/sharonds/well_being
Branch protection + CI + CodeQL enabled
# Execution Plan (Automation-Prioritized)

Goal: Rapid, low-friction delivery of personal Garmin Well-Being MVP with maximum leverage from automation (planning → Coding Agent → CI gates). Scope constrained to single-user, on-device MVP defined in /docs/PRD.md.

Legend: Priority (P0 critical blocker; P1 high; P2 medium), Impact (H/M/L), Effort (S/M/L). Sequence generally follows priority; some P1 items can run in parallel after P0 foundation.

## P0 – Automation Foundations (Must Land Before Coding Agent Executes)
| # | Task | Priority | Impact | Effort | Rationale / Success Criteria |
|---|------|----------|--------|--------|------------------------------|
| 1 | Finalize PRD (current v0.1 + gap additions) | P0 | H | S | Stable scope anchor; linkable for Issue. |
| 2 | Create Single GitHub Issue draft (checklist + out-of-scope) | P0 | H | S | Enables Coding Agent; single source of truth. |
| 3 | Add Branch Protection rules (main) | P0 | H | S | Enforces CI + CodeQL pass before merge. |
| 4 | Enable CodeQL default setup | P0 | H | S | Security scan baseline; required quality gate. |
| 5 | Set up CI Workflow (build + unit tests placeholder) | P0 | H | M | Agent PRs get immediate feedback loop. |
| 6 | Tooling Doc (README bootstrap + build instructions) | P0 | M | S | Agent + future self-consistency; prevents mis-scaffold. |

## P1 – Minimal Executable Slice (Agent-Friendly Scaffold)
| # | Task | Priority | Impact | Effort | Rationale / Success Criteria |
|---|------|----------|--------|--------|------------------------------|
| 7 | Connect IQ project skeleton (manifest, Monkey C main, app properties) | P1 | H | M | Provides build target for CI; basis for incremental commits. |
| 8 | Test Harness Setup (unit test framework or stubs) | P1 | H | M | Enables automated verification of formula logic. |
| 9 | Core Metric Interfaces (steps, resting HR stubs) | P1 | M | S | Stable abstraction for later real sensor integration. |
|10 | Prototype Score Engine (subset weights + redistribution util) | P1 | H | M | Central logic under test early. |
|11 | Recommendation Mapping module | P1 | M | S | Deterministic mapping; easy early win; testable. |
|12 | Manual Refresh Controller + Throttle logic | P1 | M | S | User interaction path; ensures early usability. |

## P1.5 – Feedback & Persistence (Phase 2 Enablers)
| # | Task | Priority | Impact | Effort | Rationale / Success Criteria |
|---|------|----------|--------|--------|------------------------------|
|13 | Extend Metrics: sleep, stress (graceful fallback) | P1 | M | M | Increases score richness; tests redistribution. |
|14 | Persistence layer (App Properties) + day rollover logic | P1 | H | S | Unlocks delta comparison UX; required for Phase 2 acceptance. |
|15 | Delta UI element (arrow/sign) | P1 | M | S | Visual motivation; low code size. |
|16 | Expanded test vectors (A,B,C + new with missing combos) | P1 | H | S | Strengthens regression safety net. |

## P2 – Stability & Automation Enhancements
| # | Task | Priority | Impact | Effort | Rationale / Success Criteria |
|---|------|----------|--------|--------|------------------------------|
|17 | Morning Auto Refresh logic (+ clock abstraction) | P2 | M | M | Reduces manual steps; adds convenience automation. |
|18 | HRV optional integration + toggle (if API present) | P2 | M | M | Optional metric; ensures feature gating. |
|19 | Ring Logging Buffer (20 entries) + debug capture | P2 | M | S | Diagnostics for future tuning; keeps lightweight. |
|20 | Error injection tests (simulated metric failures) | P2 | H | M | Ensures resiliency; closes reliability risk. |
|21 | Throttle edge tests (day rollover, first-run) | P2 | M | S | Verifies protective logic; prevents silent regressions. |

## P2.5 – Observability & Copy Polish
| # | Task | Priority | Impact | Effort | Rationale / Success Criteria |
|---|------|----------|--------|--------|------------------------------|
|22 | Debug screen (hidden trigger) | P2 | M | M | Supports manual inspection without cluttering UI. |
|23 | Copy centralization (bands, disclaimer) | P2 | L | S | Simplifies future adjustments. |
|24 | Performance timing harness (informal) | P2 | M | S | Documents compute <50ms; battery sanity. |
|25 | README expansion (architecture, test strategy, automation flow) | P2 | M | S | Clarity for Coding Agent iterations + future self. |

## P3 – Finalization & Closure
| # | Task | Priority | Impact | Effort | Rationale / Success Criteria |
|---|------|----------|--------|--------|------------------------------|
|26 | Full regression suite run & flakiness check | P3 | H | S | Confidence before closure. |
|27 | Code cleanup & dead code pruning | P3 | M | S | Maintainability. |
|28 | Final acceptance review against PRD | P3 | H | S | Ensures scope fidelity. |
|29 | Issue summary & closure (shipped vs planned, residual bugs) | P3 | M | S | Clean lifecycle end. |
|30 | Tag release v0.1.0 | P3 | M | S | Traceable state. |

## Cross-Cutting Automation Enhancements (Parallelizable)
| Task | Trigger | Impact | Notes |
|------|---------|--------|-------|
| Add PR / Issue templates | Early (post scaffold) | M | Reinforces scope & checklists. |
| Lint or static style checks | After first code | L | Only if available; optional for speed. |
| CI cache (SDK) | After stable build | M | Speeds iteration. |
| Dependency / SDK version lock file | Post initial build | M | Reproducibility. |

## Dependencies & Sequencing Notes
- CI + CodeQL (Tasks 3–5) precede any agent-driven implementation to enforce guardrails.
- Score Engine (10) depends on metric interface contract (9) but not on UI (12) — can be parallel.
- Persistence (14) should land before delta UI (15).
- HRV integration (18) deferred until stable base to avoid churn.

## Automation-Focused Critical Path (Minimal Path to Agent Productivity)
1. PRD finalized (1)
2. Issue with checklist (2)
3. Branch protection + CodeQL (3–4)
4. CI build workflow (5)
5. Project skeleton (7)
6. Test harness + prototype score (8 + 10)
7. Metric stubs (9)
8. Recommendation mapping (11)
9. Manual refresh + throttle (12) → Usable slice
10. Commit & assign Issue to @copilot → Agent begins incremental expansion

## Definition of Done (Automation Layer)
- All P0 tasks complete before assigning Issue to Coding Agent.
- CI demonstrates green baseline (build + dummy tests) and CodeQL completes.
- Each subsequent PR from Agent must add or update tests for modified logic.
- No merges possible with failing checks (enforced by branch protection).

## Out-of-Scope (Restated for Automation)
- Any attempt to add analytics, external APIs, or cloud sync to automation workflows is rejected until P3 closure.
- Performance optimization automation beyond simple timing harness.

## Status Update (12 Aug 2025)
✅ Phase 1 COMPLETE (merged PR #2) — score engine (steps + resting HR), recommendation bands, manual refresh + throttle, baseline tests.
✅ Phase 2 COMPLETE — adding sleep, stress, persistence, delta UI, Example B test.
✅ Phase 3 COMPLETE — morning auto-refresh, background processing, logging, HRV integration, enhanced error handling.
Repository: https://github.com/sharonds/well_being
Branch protection + CI + CodeQL enabled
Deterministic acceptance criteria documented in PRD & copilot instructions.

### Phase 3 Objectives & Success Criteria (COMPLETE)
| Objective | Success Criteria | Status |
|-----------|------------------|--------|
| Morning Auto-Refresh | Single daily trigger 06:00-08:00, respects throttle | ✅ COMPLETE |
| Background Scheduling | Lightweight scheduler, missed window detection | ✅ COMPLETE |
| Logging Ring Buffer | 20 entries max, timestamp+level+message | ✅ COMPLETE |
| Enhanced Error Handling | Graceful metric failures, weight redistribution | ✅ COMPLETE |
| ENABLE_HRV Feature Flag | Default false, scaffolding ready | ✅ COMPLETE |
| HRV Metric Integration | Weight redistribution, 20-120ms normalization | ✅ COMPLETE |
| Backward Compatibility | Phase 1/2 scores unchanged when flags off | ✅ COMPLETE |
| Persistence Expansion | autoRefreshDate, lastRunMode keys | ✅ COMPLETE |
| Performance | Score computation < 50ms with timing harness | ✅ COMPLETE |

### Phase 3 Implementation Summary
- **Logger.mc**: Ring buffer with 20-entry capacity, oldest overwritten
- **Scheduler.mc**: Auto-refresh logic, morning window detection, persistence tracking
- **ScoreEngine.mc**: ENABLE_HRV flag, dynamic weight system, HRV normalization
- **MetricProvider.mc**: HRV metric provider with graceful fallback
- **WellBeingApp.mc**: Auto-refresh integration, enhanced error handling, performance timing
- **PerformanceTimer.mc**: Comprehensive timing harness for performance validation
- **TestRunner.mc**: Extended tests for all Phase 3 features and edge cases

### All Test Vectors Maintained
- Example A: Steps=8000, RHR=55 → Score=65 ✅
- Example B: Steps=12500, RHR=48, Sleep=7h, Stress=35 → Score=88 ✅  
- Example C: Steps=3000, RHR=70 → Score=25 ✅

## Next Immediate Actions Recommendation
~~If executing now inside repo:~~
~~1. (We already have PRD) -> Create Issue body file draft locally for copy/paste.~~
~~2. Scaffold CI + placeholder project directories so Issue tasks reflect actual paths.~~

**COMPLETED**: Issue #1 enhanced with explicit PRD section references for systematic implementation validation.
