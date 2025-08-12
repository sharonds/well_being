# Phase 4 Micro-Issues for Automation Testing

## Strategy: Break Issue #9 into Automation-Friendly Micro-Issues

### Micro-Issue #1: Settings Menu Component ⭐ HIGHEST PRIORITY
**Scope**: Single file creation
**Deliverable**: `source/SettingsMenu.mc` with basic toggle functionality
**Automation**: ✅ Simple (single file, clear template)
**Success**: File exists, compiles, basic structure correct

### Micro-Issue #2: Performance Timer Utility
**Scope**: Single utility function
**Deliverable**: `source/PerformanceTimer.mc` with start/stop/measure functions
**Automation**: ✅ Simple (utility pattern, no dependencies)
**Success**: Functions available, timing works

### Micro-Issue #3: Error Code Constants
**Scope**: Constants definition
**Deliverable**: `source/ErrorCodes.mc` with structured error codes
**Automation**: ✅ Very Simple (just constants)
**Success**: Constants available for Logger.add() calls

### Micro-Issue #4: HRV Test Case Addition
**Scope**: Single test function
**Deliverable**: Add `testHRVIntegration()` to `tests/TestRunner.mc`
**Automation**: ✅ Simple (append to existing file)
**Success**: Test runs, passes expected behavior

### Micro-Issue #5: History Buffer Implementation
**Scope**: Single class creation
**Deliverable**: `source/ScoreHistory.mc` with circular buffer
**Automation**: ⚠️ Medium complexity (data structures)
**Success**: Class exists, basic operations work

### Micro-Issue #6: Real Metrics Integration (Steps Only)
**Scope**: Update one metric in MetricProvider
**Deliverable**: Replace steps stub with real ActivityMonitor call
**Automation**: ⚠️ Medium (API integration)
**Success**: getSteps() returns real data or null

### Micro-Issue #7: UI Delta Display Component
**Scope**: Single UI component
**Deliverable**: `source/DeltaDisplay.mc` with +/- formatting
**Automation**: ⚠️ Medium (UI logic)
**Success**: Component renders delta correctly

### Micro-Issue #8: Documentation Update - Phase 4 Status
**Scope**: Single doc section
**Deliverable**: Update PRD Phase 4 section with implementation status
**Automation**: ✅ Simple (text replacement)
**Success**: Documentation reflects current Phase 4 state

## Automation Testing Order (Build Confidence)
1. **Start with #1 (Settings)** - Highest success probability
2. **Then #2 (Performance Timer)** - Build on success
3. **Then #3 (Error Codes)** - Easy win
4. **Validate pattern works** - 3 successful automations
5. **Scale to #4, #5, #6** - More complex tasks
6. **Finish with #7, #8** - Full confidence

## Success Metrics
- **100% success rate** on micro-issues #1-#3 (simple tasks)
- **80%+ success rate** on micro-issues #4-#6 (medium tasks)
- **Automation confidence** built through incremental success
- **Issue #9 progress** via smaller, manageable chunks

## Workflow Template (Per Micro-Issue)
```yaml
# Simple workflow template
- Create single file or make single focused change
- Commit with clear message
- Push to feature branch
- Create focused PR
- Validate specific success criteria
```