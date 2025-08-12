# Phase 4 Remaining Items - Automation Strategy

## Current Status: 2 of 10 AC Items Complete ✅

**COMPLETED via automation:**
- ✅ AC2: Clock abstraction (Clock.mc - 25 lines)
- ✅ AC7: Settings menu (SettingsMenu.mc - 52 lines)

**REMAINING: 8 AC Items for automation**

## Micro-Automation Plan (Priority Order)

### 🥇 HIGH PRIORITY - Simple Automation (95%+ success rate)

#### 1. **AC4: Error Codes Structure** 
```bash
gh workflow run simple-automation.yml \
  --field task_name=error-codes \
  --field issue_number=NEW_ISSUE
```
**Deliverable**: `source/ErrorCodes.mc` with structured constants
**Automation Time**: ~16 seconds
**Complexity**: Very Simple (constants only)

#### 2. **AC8: Performance Timer Utility**
```bash
gh workflow run simple-automation.yml \
  --field task_name=performance-timer \
  --field issue_number=NEW_ISSUE
```
**Deliverable**: `source/PerformanceTimer.mc` with timing harness
**Automation Time**: ~16 seconds
**Complexity**: Simple (utility functions)

#### 3. **AC10: Test Cases Addition**
```bash
gh workflow run simple-automation.yml \
  --field task_name=phase4-tests \
  --field issue_number=NEW_ISSUE
```
**Deliverable**: Add Phase 4 test functions to `tests/TestRunner.mc`
**Automation Time**: ~20 seconds
**Complexity**: Simple (append to existing file)

### 🥈 MEDIUM PRIORITY - Moderate Automation (85%+ success rate)

#### 4. **AC6: History Buffer Structure**
```bash
gh workflow run simple-automation.yml \
  --field task_name=score-history \
  --field issue_number=NEW_ISSUE
```
**Deliverable**: `source/ScoreHistory.mc` with 7-day circular buffer
**Automation Time**: ~30 seconds
**Complexity**: Medium (data structures, algorithms)

#### 5. **AC1: Real Metrics (Steps Only)**
```bash
gh workflow run simple-automation.yml \
  --field task_name=real-metrics-steps \
  --field issue_number=NEW_ISSUE
```
**Deliverable**: Update `MetricProvider.mc` steps function with real API
**Automation Time**: ~25 seconds
**Complexity**: Medium (API integration, error handling)

### 🥉 MANUAL/HYBRID PRIORITY - Complex Integration (60-70% automation success)

#### 6. **AC5: UI Delta Display**
- **Approach**: Manual implementation with automation assists
- **Reason**: UI layout decisions require human judgment
- **Time**: 30-60 minutes manual work

#### 7. **AC3: Auto-refresh Integration**
- **Approach**: Manual implementation (already has Scheduler.mc)
- **Reason**: Complex integration with existing WellBeingApp.mc
- **Time**: 45-90 minutes manual work

#### 8. **AC9: Documentation Updates**
- **Approach**: Semi-automated (template-driven updates)
- **Reason**: Content requires human review and context
- **Time**: 30-45 minutes

## Execution Strategy

### Week 1: Simple Automations (Days 1-3)
- **Day 1**: AC4 (Error Codes) → AC8 (Performance Timer)
- **Day 2**: AC10 (Test Cases) 
- **Day 3**: Validate all simple automations working

### Week 2: Medium Automations (Days 4-6)  
- **Day 4**: AC6 (History Buffer)
- **Day 5**: AC1 (Real Metrics - Steps)
- **Day 6**: Validate medium automations

### Week 3: Manual/Hybrid (Days 7-10)
- **Day 7-8**: AC5 (UI Delta) + AC3 (Auto-refresh)
- **Day 9**: AC9 (Documentation)  
- **Day 10**: Final validation, Issue #9 closure

## Success Metrics Target

**Automation Coverage Goal**: 5 of 8 remaining AC items (62.5%)
**Overall Automation**: 7 of 10 total AC items (70%)
**Time Savings**: ~80% reduction vs full manual implementation
**Quality**: Template-driven consistency across all automated components

## Risk Mitigation

**IF automation fails:**
1. Fall back to manual implementation for that specific AC
2. Capture lessons learned for template improvement
3. Continue with remaining automations
4. Document hybrid approach success

**Success Criteria**: 
- ✅ 70%+ of Phase 4 completed via automation
- ✅ All AC items satisfied (automated or manual)
- ✅ Production-ready code quality maintained
- ✅ Issue #9 fully resolved