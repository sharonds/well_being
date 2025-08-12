## Implementation Approach
### Phase 2 (Next – Guardrails)
- Add sleep & stress metrics behind feature flags ENABLE_SLEEP / ENABLE_STRESS
- Implement persistence (keys: lastScore, lastScoreDate) & delta display (hide first day)
- Add Example B (score 88) + redistribution permutation tests
- Maintain backward compatibility (Phase 1 score must remain identical when new flags off)
# Copilot Coding Agent Instructions

## Repository Overview
This is a Garmin Connect IQ watch app for personal well-being tracking. It computes daily readiness scores based on health metrics.

## Key Documents
- **PRD**: `/docs/PRD.md` - Product requirements (source of truth)
- **Execution Plan**: `/execution_plan.md` - Implementation roadmap
- **Test Vectors**: PRD Section 14.1 - Examples A, B, C must pass

## Development Guidelines

### Code Standards
- **Language**: Monkey C for Connect IQ
- **Target Device**: Forerunner 965 (primary)
- **SDK Version**: 7.2.0
- **App Type**: Watch App (not widget/data field)

### Architecture Patterns
- Use modular design with clear separation of concerns
- Follow existing patterns in `source/` directory
- Implement graceful degradation for missing metrics
- Use weight redistribution when metrics unavailable (PRD Section 7.2)

### Testing Requirements
- All PRD test vectors (Examples A, B, C) must validate
- Include edge case testing (boundaries, null values)
- Test recommendation band transitions (39/40, 69/70)
- Validate throttling logic (5-minute minimum)

## File Ownership

### DO NOT MODIFY (without explicit permission)
- `.gitignore` - Comprehensive security version must be preserved
- `SECURITY.md` - Security policy is finalized
- `.github/workflows/ci.yml` - CI pipeline is stable

### Always Preserve
- Existing test cases in `tests/`
- PRD examples and formulas
- Security best practices

## Before Starting Work

### Prerequisites Checklist
1. Check for active PRs: `gh pr list`
2. Pull latest from main: `git pull origin main`
3. Review the specific Issue requirements
4. Verify no one else is working on same files

### Coordination Protocol
- Create draft PR early to signal work in progress
- Use descriptive branch names: `phase-2-persistence`, not `fix-1`
- Comment on Issue when starting/stopping work
- Reference PRD sections in commits

## Implementation Approach

### Phase 1-3 (Complete) ✅
- Score engine with all metrics (steps, resting HR, sleep, stress, HRV)
- Weight redistribution with feature flags
- Persistence with delta display
- Auto-refresh scheduling (morning window)
- Ring buffer logging (20 entries)

### Phase 4 (Current – Production Integration)
- Replace ALL stub functions with real APIs (no hardcoded dates/times)
- Implement 7-day score history with circular buffer
- Add runtime settings menu for feature flag toggles
- Performance validation (<50ms score computation)
- Real Garmin health metrics integration (graceful fallbacks)
- UI enhancements (delta display, auto/manual indicators)

### Hybrid Automation Approach (Current)
- **GitHub Actions First**: Use `.github/workflows/phase4-automation.yml` for complex multi-task issues
- **Manual Refinement**: Human validation and completion of automated implementations  
- **Real API Integration**: Workflows handle actual Garmin SDK integration vs stubs
- **Structured Output**: Automated commits follow conventional format with AC references

### GitHub Actions Workflow Guidelines
- **Trigger Method**: Manual dispatch or "automate-phase-4" issue comments
- **Implementation Scope**: Core repetitive tasks (Clock, metrics, persistence)
- **Human Validation Required**: UI decisions, performance testing, edge cases
- **Branch Pattern**: `{phase}-automated-implementation` for workflow branches

### Legacy Copilot Agent Guidelines (Enterprise Only)
- **Multi-task Issues**: Follow Implementation Plan priority order exactly
- **Acceptance Criteria**: Each AC must be individually validated and confirmed
- **Performance Requirements**: Validate timing with test harness, not assumptions
- **Backward Compatibility**: All existing Phase 1-3 functionality must remain identical
- **Error Handling**: Wrap ALL API calls with try-catch and structured logging
- **Branch Naming**: Use descriptive names like `phase-4-implementation`, not generic names

### Weight Redistribution Formula (All Phases)
activeWeight(metric) = baseWeight(metric) / Σ(baseWeight for present metrics)
score = round( Σ activeWeight * normalizedMetric * 100 ) with round = floor(x + 0.5)

### Base Weights (When All Present, no HRV)
steps 0.40, restingHR 0.30, sleep 0.20, stress 0.10

### Test Vector Table (Must Stay Stable)
| Example | Steps | RestHR | Sleep | Stress | Expected | Band |
|---------|-------|--------|-------|--------|----------|------|
| A | 8000 | 55 | -- | -- | 65 | Maintain |
| B | 12500 | 48 | 7h | 35 | 88 | Go for it |
| C | 3000 | 70 | -- | -- | 25 | Take it easy |

### Formula Implementation
```
// Always use PRD Section 7.2 formulas
steps_norm = min(steps, 12000) / 12000
rhr_inv_norm = (80 - clamp(rhr, 40, 80)) / 40
score = (weight_steps * steps_norm + weight_rhr * rhr_inv_norm) * 100
```

## Error Handling
- Never crash on missing metrics
- Use "--" for unavailable data in UI
- Log errors to in-memory buffer (max 20 entries)
- Implement try-catch around metric fetches

## Commit Standards
- Reference PRD sections: "Implement persistence per PRD Section 7.4"
- Include test validation: "Validates Example B (score 88)"
- Use conventional commits: "feat:", "fix:", "test:", "docs:"

## PR Requirements
- All CI checks must pass
- Include test results in PR description
- Reference Issue number: "Fixes #N"
- List PRD acceptance criteria met

## Common Pitfalls to Avoid
1. Don't create duplicate .gitignore entries
2. Don't remove existing security measures
3. Don't modify formula without PRD update
4. Don't skip test vector validation
5. Don't ignore throttling requirements

## Questions?
Review the PRD first, then check existing implementations in `source/` directory for patterns to follow
