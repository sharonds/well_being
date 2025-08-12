# Automation Templates Library
*Copy-paste templates for instant automation*

## 🏗️ Workflow Templates

### Basic Single-File Automation
```yaml
name: Simple Task Automation
on:
  workflow_dispatch:
    inputs:
      task_name:
        description: 'Task identifier'
        required: true
        type: string
      issue_number:
        description: 'Issue number'
        required: true
        type: string

jobs:
  automate-task:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Create feature branch
        run: |
          git config --global user.name "GitHub Actions Automation"
          git config --global user.email "actions@github.com"
          git checkout -b auto-${{ github.event.inputs.task_name }}-${{ github.run_number }}

      - name: Implement task
        run: |
          # Your implementation here
          echo "Implementation for ${{ github.event.inputs.task_name }}"

      - name: Commit and push
        run: |
          git add .
          git commit -m "feat: Automated implementation of ${{ github.event.inputs.task_name }}"
          git push origin auto-${{ github.event.inputs.task_name }}-${{ github.run_number }}

      - name: Create PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr create \
            --title "Automated: ${{ github.event.inputs.task_name }}" \
            --body "Automated implementation via GitHub Actions" \
            --assignee ${{ github.actor }}
```

### Multi-Choice Task Automation
```yaml
name: Multi-Task Automation
on:
  workflow_dispatch:
    inputs:
      task_type:
        description: 'Type of task to automate'
        required: true
        type: choice
        options:
          - component
          - test
          - documentation
          - configuration
      task_name:
        description: 'Specific task name'
        required: true
        type: string

jobs:
  automate-by-type:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Create Component
        if: github.event.inputs.task_type == 'component'
        run: |
          # Component creation logic

      - name: Create Test
        if: github.event.inputs.task_type == 'test'
        run: |
          # Test creation logic

      - name: Update Documentation  
        if: github.event.inputs.task_type == 'documentation'
        run: |
          # Documentation update logic

      - name: Update Configuration
        if: github.event.inputs.task_type == 'configuration'
        run: |
          # Configuration update logic
```

## 📝 Issue Templates

### Simple Automation Issue
```markdown
---
name: Simple Automation Task
about: Create an issue for single-file automation
title: 'Automate: [TASK_NAME]'
labels: automation, enhancement
assignees: ''
---

## Task Description
Brief description of what needs to be automated.

## Deliverable
- [ ] Create/update `path/to/file.ext`
- [ ] Implement [specific functionality]

## Success Criteria
- [ ] File exists and is valid
- [ ] [Specific requirement 1]
- [ ] [Specific requirement 2]

## Automation Details
```bash
gh workflow run simple-automation.yml \
  --field task_name=[task-name] \
  --field issue_number={{ issue.number }}
```

**Expected automation time**: 5-10 minutes
**Complexity**: Simple (single file, clear template)
```

### Complex Task Breakdown
```markdown
---
name: Complex Task Automation
about: Break down complex tasks into automatable micro-issues  
title: 'Complex: [FEATURE_NAME]'
labels: automation, epic
assignees: ''
---

## Feature Overview
Description of the complex feature or task.

## Micro-Issue Breakdown
- [ ] #[N] - [Micro-issue 1]: [Single file/component]
- [ ] #[N] - [Micro-issue 2]: [Another single file/component]  
- [ ] #[N] - [Micro-issue 3]: [Integration/testing]

## Automation Strategy
Each micro-issue should be automatable using simple-automation workflow.

## Success Criteria  
- [ ] All micro-issues completed successfully
- [ ] Integration works correctly
- [ ] No regressions introduced

## Estimated Timeline
- Automation time: [X] minutes per micro-issue
- Total micro-issues: [N]
- Manual integration: [X] minutes
```

### Bug Fix Automation
```markdown
---
name: Automated Bug Fix
about: Automate straightforward bug fixes
title: 'Bug: [BUG_DESCRIPTION]'
labels: automation, bug
assignees: ''
---

## Bug Description
What's broken and how it manifests.

## Root Cause
Specific issue identified (file, line, logic).

## Automation Plan
- [ ] Update `[file.ext]` with fix
- [ ] Add test case to prevent regression
- [ ] Validate fix works

## Automation Command
```bash
gh workflow run bug-fix-automation.yml \
  --field bug_type=[type] \
  --field issue_number={{ issue.number }}
```

**Complexity**: Simple (if single-file fix)
```

## 🎯 PR Templates

### Automated PR Description
```markdown
## Automated Implementation: [TASK_NAME]

🤖 **This PR was generated automatically via GitHub Actions**

### Changes Made
- Created/Updated: `[files changed]`
- Implementation: [brief description]

### Automation Details
- **Workflow**: `.github/workflows/[workflow-name].yml`
- **Task**: `[task_name]`
- **Issue**: Closes #[issue_number]
- **Runtime**: [X] seconds

### Validation Checklist
- [ ] File(s) created successfully
- [ ] Implementation matches requirements
- [ ] No syntax errors
- [ ] Follows existing patterns

### Human Review Needed
- [ ] Logic correctness
- [ ] Integration with existing code
- [ ] Edge case handling
- [ ] Performance implications

### Next Steps
- [ ] Code review and approval
- [ ] Manual testing if needed
- [ ] Merge when ready

---
*Generated by GitHub Actions automation on [timestamp]*
```

### Bug Fix PR Template
```markdown
## Automated Bug Fix: [BUG_DESCRIPTION]

### Problem
[Brief description of the bug]

### Solution
[What was changed to fix it]

### Files Changed
- `[file.ext]`: [description of changes]

### Testing
- [ ] Automated tests pass
- [ ] Manual verification needed: [describe]

### Risk Assessment
- **Risk Level**: [Low/Medium/High]
- **Backward Compatibility**: [Yes/No]
- **Performance Impact**: [None/Minimal/Needs Review]

### Automation Details
- **Workflow**: [workflow name]  
- **Generated**: [timestamp]
- **Issue**: Fixes #[issue_number]
```

## 📋 Code Templates

### Monkey C Class Template
```monkeyc
using Toybox.System as Sys;

// [Class description and purpose]
// Generated by automation on [timestamp]
class [ClassName] {
    // Private variables
    private var _[variableName] = null;
    
    // Constructor
    public function initialize() {
        // Initialization logic
    }
    
    // Public methods
    public function [methodName]([parameters]) {
        try {
            // Method implementation
            return [result];
        } catch(e) {
            Logger.add("ERROR", "[ERROR_CODE]: " + e.getErrorMessage());
            return null;
        }
    }
    
    // Private helper methods
    private function _[helperMethod]([parameters]) {
        // Helper implementation
    }
}
```

### Test Case Template
```monkeyc
// Test: [TestName] - [Description]
// Generated by automation
public static function test[TestName]() {
    try {
        // Arrange
        var input = [test_input];
        var expected = [expected_result];
        
        // Act  
        var actual = [ClassUnderTest].[methodUnderTest](input);
        
        // Assert
        var passed = (actual == expected);
        Sys.println("Test[TestName]: " + (passed ? "PASS" : "FAIL"));
        
        if (!passed) {
            Sys.println("  Expected: " + expected);
            Sys.println("  Actual: " + actual);
        }
        
        return passed;
    } catch(e) {
        Sys.println("Test[TestName]: ERROR - " + e.getErrorMessage());
        return false;
    }
}
```

### Constants Template
```monkeyc
// [Constants description]
// Generated by automation
class [ConstantsClassName] {
    // [Category] Constants
    public const [CONSTANT_NAME] = "[value]";
    public const [CONSTANT_NAME_2] = [numeric_value];
    
    // Error Codes
    public const ERROR_[ERROR_TYPE] = "ERROR_[ERROR_TYPE]";
    
    // Configuration Values
    public const CONFIG_[SETTING_NAME] = [value];
    
    // Default Values
    public const DEFAULT_[PROPERTY_NAME] = [default_value];
}
```

## 🔄 Workflow Triggers

### Manual Dispatch
```yaml
on:
  workflow_dispatch:
    inputs:
      task_name:
        description: 'Name of the task'
        required: true
        default: 'example-task'
        type: string
```

### Issue Comment Trigger
```yaml
on:
  issue_comment:
    types: [created]

jobs:
  check-trigger:
    if: contains(github.event.comment.body, '/automate')
    runs-on: ubuntu-latest
    steps:
      - name: Extract task from comment
        id: extract
        run: |
          COMMENT="${{ github.event.comment.body }}"
          TASK=$(echo "$COMMENT" | grep -o '/automate [^ ]*' | cut -d' ' -f2)
          echo "task=$TASK" >> $GITHUB_OUTPUT
```

### Pull Request Trigger
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'source/**/*.mc'

jobs:
  auto-test:
    runs-on: ubuntu-latest
    steps:
      - name: Run automated tests
        run: |
          # Test automation logic
```

## 📊 Monitoring Templates

### Success Metrics Collection
```yaml
- name: Collect Automation Metrics
  run: |
    echo "AUTOMATION_SUCCESS=true" >> $GITHUB_ENV
    echo "AUTOMATION_DURATION=${{ steps.timer.outputs.duration }}" >> $GITHUB_ENV
    echo "FILES_CHANGED=$(git diff --name-only | wc -l)" >> $GITHUB_ENV

- name: Report Metrics
  if: always()
  run: |
    gh issue comment ${{ github.event.inputs.issue_number }} \
      --body "📊 **Automation Metrics**
      - Success: ${{ env.AUTOMATION_SUCCESS }}
      - Duration: ${{ env.AUTOMATION_DURATION }}s
      - Files Changed: ${{ env.FILES_CHANGED }}
      - Workflow: ${{ github.workflow }}"
```

## 🚨 Error Handling Templates

### Retry Logic
```yaml
- name: Implement with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 5
    max_attempts: 3
    command: |
      # Your automation command here
```

### Rollback on Failure
```yaml
- name: Rollback on failure
  if: failure()
  run: |
    git checkout -- .
    git clean -fd
    echo "❌ Automation failed, changes rolled back"
```

### Notification on Failure
```yaml
- name: Notify on failure
  if: failure()
  run: |
    gh issue comment ${{ github.event.inputs.issue_number }} \
      --body "❌ **Automation Failed**
      
      The automation workflow encountered an error. Please check the [workflow run](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}) for details.
      
      Consider:
      - Manual implementation
      - Simplified automation approach
      - Breaking into smaller micro-issues"
```

---

## 📚 Usage Instructions

1. **Copy template** that matches your needs
2. **Customize** placeholders in `[brackets]`
3. **Test** with a simple example first
4. **Scale** to more complex scenarios
5. **Contribute** improvements back to this library

**Remember**: Start with the simplest template that works, then enhance incrementally.

*These templates are battle-tested and ready for production use.*