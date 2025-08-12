# Copilot Review Prompt Templates
*Curated, high-performing prompts for systematic code review*

## 🔧 Core Prompt Templates

### A. General Micro-Issue PR Review
```
Review this PR for correctness, scope creep, and missing edge cases.

**Micro-issue Success Criteria:**
[PASTE_ISSUE_SUCCESS_CRITERIA_HERE]

**Focus Areas:**
- Confirm implementation matches success criteria exactly
- Flag unnecessary complexity or scope creep
- Identify missing error handling or edge cases
- Verify no unintended side effects

**Response Format:**
- Must-fix: [Critical issues affecting functionality]
- Should-fix: [Quality improvements worth addressing]
- Nice-to-have: [Optional optimizations]
```

### B. Formula Safety Review (ScoreEngine)
```
Review this ScoreEngine change for formula safety and backward compatibility.

**Critical Requirements:**
- NO change to legacy score paths when flags disabled
- Weight redistribution must be mathematically consistent
- Phase 1 compatibility preserved (ENABLE_SLEEP=false, ENABLE_STRESS=false)

**Validation Tests:**
- Verify Example A (8000 steps, 55 RHR → 65) unchanged when flags off
- Verify Example C (3000 steps, 70 RHR → 25) unchanged when flags off
- Check weight calculations sum to 1.0 in all scenarios

**Flag Any:**
- Weight redistribution inconsistencies
- Formula changes affecting existing test cases
- Missing backward compatibility validation
```

### C. Observability/Logging Review
```
Review logging and error handling implementation.

**Requirements:**
- Each try/catch block includes Logger.add() with meaningful ErrorCodes constant
- No errors swallowed silently
- Error messages provide actionable context
- Logger calls follow pattern: Logger.add("LEVEL", ErrorCodes.CODE + ": " + details)

**Check For:**
- Missing Logger.add() in catch blocks
- Generic error messages without ErrorCodes constants
- Silent failures without logging
- Paths that could throw exceptions without try/catch

**List:**
1. All new error handling paths
2. Any silent error paths found
3. Missing ErrorCodes constants needed
```

### D. Performance Review (Garmin Watch Constraints)
```
Review for Garmin Connect IQ performance constraints (<50ms target).

**Focus on:**
- Loop complexity in score computation
- Object allocations in hot paths
- Inefficient string operations
- Recursive calls or deep nesting

**Flag:**
- Loops that could exceed 50ms on low-end devices
- Unnecessary object creation in computation paths
- String concatenation in loops
- Complex calculations without caching

**Suggest:**
- Minimal refactors to reduce complexity
- Caching opportunities for expensive operations
- Algorithm optimizations maintaining correctness
```

### E. Test Adequacy Review
```
Review test coverage for implemented behaviors.

**Current Tests:** [LIST_EXISTING_TEST_METHODS]

**Analyze:**
- Behaviors implemented but not directly tested
- Edge cases missing test coverage
- Error paths without test validation
- Integration scenarios not covered

**Propose:**
- 1-2 small additional tests if high-value gaps found
- Focus on must-have coverage only (avoid test bloat)
- Prioritize error handling and edge case tests
- Integration test opportunities

**Avoid:**
- Over-testing trivial getter/setter methods
- Redundant tests of same logic path
- Tests that duplicate existing coverage
```

### F. Security/Stability Review
```
Review for API safety and crash prevention.

**Risky Patterns to Flag:**
- Null pointer access without checks
- Device API calls without null validation
- Unchecked array/collection access
- Resource leaks or cleanup issues

**Garmin Connect IQ Specific:**
- ActivityMonitor.getInfo() can return null
- UserProfile.getProfile() may be unavailable
- Memory constraints on older devices
- Exception handling for device API failures

**Validation Required:**
- All device API responses checked for null
- Graceful degradation when APIs unavailable
- Memory usage appropriate for target devices
- No crash scenarios on API failures
```

## 🔄 Structured Review Flow

### Step 1: Pre-Review Preparation
```bash
# Run automated gates
./scripts/prepare-copilot-review.sh

# Extract micro-issue criteria
gh issue view [ISSUE_NUMBER] --json body | jq -r '.body'

# Get changed files summary
git diff --stat main
```

### Step 2: Request Review with Context
```
**Micro-Issue Context:**
- Issue #[NUMBER]: [TITLE]
- Success Criteria: [PASTE_FROM_ISSUE]
- Changed Files: [LIST_FILES]

[PASTE_APPROPRIATE_PROMPT_TEMPLATE]
```

### Step 3: Classify Findings
```markdown
## Copilot Review Classification

### Must-Fix (Block merge until resolved)
- [ ] Logic defect affecting functionality
- [ ] Missed acceptance criteria requirement
- [ ] Backward compatibility risk
- [ ] Performance regression risk
- [ ] Security vulnerability

### Should-Fix (Address before merge if feasible)
- [ ] Missing observability (logging/error codes)
- [ ] Test coverage gap for important behavior
- [ ] Code quality issue affecting maintainability

### Nice-to-Have (Consider for future improvement)
- [ ] Style/formatting suggestions
- [ ] Minor optimizations
- [ ] Documentation enhancements
```

### Step 4: Action Responses
```markdown
## Response to Copilot Findings

### Must-Fix Items
1. [Issue]: **Handled** - [Description of fix]
2. [Issue]: **Deferred** - [Reason and tracking issue created]

### Should-Fix Items  
1. [Issue]: **Handled** - [Description of fix]
2. [Issue]: **Accepted** - [Will address in follow-up]

### Nice-to-Have Items
- **Noted** for future improvement opportunities
```

### Step 5: Re-Review (if logic changes made)
```
**Follow-up Review Request:**
Applied fixes for must-fix items:
- [List changes made]

Please verify:
- Logic changes are correct
- No new issues introduced
- Original concerns addressed
```

## 📊 Review Metrics Tracking

### Daily Metrics (track in issue comments)
```markdown
## Copilot Review Metrics - [DATE]

**Review Turnaround:** [X] minutes (target: <2 min)
**Findings:**
- Must-fix: [N] items (target: declining trend)
- Should-fix: [N] items  
- Nice-to-have: [N] items

**Adoption Rate:** [X]% suggestions implemented (target: 40-80%)
**Regressions Prevented:** [N] (log significant catches)

**Quality Score:** ✅ Ready for merge / ⚠️ Needs work
```

### Weekly Summary
```markdown
## Weekly Copilot Review Summary

**Micro-Issues Reviewed:** [N]
**Average Turnaround:** [X] minutes
**Must-Fix Rate Trend:** [↓/↑/→] 
**Prevented Regressions:** [N]
**Process Improvements:** [List learnings]
```

## 🚫 Anti-Patterns to Avoid

### ❌ Don't Do This
- **Over-prompting**: One giant vague prompt with everything
- **Blind acceptance**: Adopting >80% of suggestions without judgment
- **Style focus**: Accepting cosmetic rewrites that inflate diff
- **Feature creep**: Using review to generate new features
- **Context loss**: Ignoring micro-issue scope and success criteria

### ✅ Do This Instead  
- **Targeted prompts**: Use specific templates for specific concerns
- **Selective adoption**: Focus on must-fix and high-value should-fix items
- **Scope discipline**: Keep changes minimal and focused
- **Evaluative approach**: Use review to validate, not generate
- **Context preservation**: Always reference micro-issue success criteria

## 🎯 Definition of Done Integration

### Micro-Issue Completion Checklist
Add this line to all micro-issue templates:
```
- [ ] **Copilot code review**: Zero unresolved must-fix items
```

### Medium Complexity Requirements
For complex features (AC5, AC6), require:
```
- [ ] **First pass review**: Automated + Copilot validation
- [ ] **Second pass review**: Post-fixes verification 
- [ ] **Integration review**: Cross-component interaction check
```

## 🔧 Automation Integration

### PR Template Enhancement
```markdown
## Copilot Review Readiness
- [ ] Pre-review gates passed (run `./scripts/prepare-copilot-review.sh`)
- [ ] Micro-issue success criteria: [LINK_TO_ISSUE]
- [ ] Review prompt used: [TEMPLATE_NAME]
- [ ] All must-fix items resolved

## Minimal Review Rubric
- [ ] Scope matches micro-issue only
- [ ] No legacy score regression (flags off behavior preserved)
- [ ] All new error codes documented or self-explanatory
- [ ] Tests cover happy path + 1 failure scenario  
- [ ] No unnecessary allocations in hot path
- [ ] Logger calls present for each catch block
```

### Scripts Integration
```bash
# Add to automation workflow
- name: Prepare Copilot Review Context
  run: |
    echo "## Copilot Review Context" >> $GITHUB_STEP_SUMMARY
    echo "**Issue:** #${{ github.event.inputs.issue_number }}" >> $GITHUB_STEP_SUMMARY
    echo "**Files Changed:** $(git diff --name-only main)" >> $GITHUB_STEP_SUMMARY
    echo "**Recommended Prompt:** General Micro-Issue PR Review" >> $GITHUB_STEP_SUMMARY
```

---

## 🚀 Quick Start Commands

```bash
# Prepare for review
./scripts/prepare-copilot-review.sh

# Get issue context
gh issue view [NUMBER] --json body | jq -r '.body'

# Start review with appropriate template from above

# Track metrics in issue comment
gh issue comment [NUMBER] --body "$(cat review-metrics-template.md)"
```

*This guide ensures systematic, measurable code review integration while maintaining our proven micro-issue automation success.*