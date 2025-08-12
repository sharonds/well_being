# Automation Workflow Guide

## Automation Options Available

### Option 1: GitHub Copilot Coding Agent (Pro/Business/Enterprise)
- **Requirements**: GitHub Copilot Pro, Business, or Enterprise plan
- **Availability**: All GitHub repositories (except managed user accounts or explicitly disabled)
- **Status**: ⚠️ May be available but not enabled for this repository
- **Documentation**: https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent

#### How to Enable GitHub Copilot Agent:
1. **Check Plan**: Verify GitHub Copilot Pro/Business/Enterprise subscription
2. **Repository Settings**: Enable Copilot features in repository settings
3. **Assignment Method**: Assign Copilot user directly to issues (not @mentions)
4. **Alternative**: Use VS Code with GitHub Copilot extension for similar functionality

### Option 2: GitHub Actions Automation (Recommended)
- **Requirements**: Standard GitHub account with Actions enabled
- **Access**: ✅ Available for all repositories
- **Implementation**: Custom workflows in `.github/workflows/`

## When to Use GitHub Actions Automation

### Ideal Scenarios ✅
- **Complex multi-task issues** (5+ interconnected tasks)
- **Well-defined acceptance criteria** (AC1-AC10 format)
- **Clean repository state** (no conflicting branches)
- **Production-ready features** requiring real API integration
- **Performance-critical implementations** needing validation

### Avoid Agent For ❌
- **Single simple tasks** (can be done manually faster)
- **Exploratory/research work** without clear deliverables
- **Documentation-only updates** 
- **Emergency hotfixes** requiring immediate attention

## GitHub Actions Automation Implementation (Phase 4)

### Phase 4 Automation Workflow
**File**: `.github/workflows/phase4-automation.yml`
**Status**: ✅ Active and deployed

#### Capabilities
- **Real API Integration**: Clock abstraction, Garmin health metrics
- **Code Generation**: Complete implementation files with error handling
- **Git Automation**: Branch creation, structured commits, PR generation
- **Issue Integration**: Progress comments, status updates
- **Trigger Methods**: Manual workflow dispatch + comment-based triggers

#### Usage Examples
```bash
# Manual trigger
gh workflow run phase4-automation.yml --field issue_number=9

# Comment trigger (add to Issue #9)
automate-phase-4
```

### Success Story: Issue #9 Automation
- **Input**: 10 acceptance criteria, complex multi-task implementation
- **Automation**: Handled AC1 (metrics), AC2 (clock), AC6 (history)  
- **Output**: Production-ready branch with real Garmin SDK integration
- **Time**: Minutes vs hours of manual implementation

## Legacy: GitHub Copilot Agent Process (For Reference)

### 1. Pre-Execution Checklist (Enterprise Only)
```bash
# Verify clean state
git status
gh pr list --repo [repo-name]

# Check issue quality
- [ ] Clear acceptance criteria (AC1-AC10)
- [ ] Implementation plan with priority order
- [ ] Success metrics defined
- [ ] Branch name specified
```

### 2. Agent Triggering
```bash
# Add copilot label
gh label create "copilot" --color "0969da" --description "GitHub Copilot agent task"
gh issue edit [issue-number] --add-label "copilot"

# Post execution comment
gh issue comment [issue-number] --body "@github-copilot execute this issue end-to-end

**EXECUTION REQUIREMENTS:**
- Implement all tasks from Implementation Plan
- Satisfy all acceptance criteria
- Replace ALL stub functions
- Maintain backward compatibility
- Ensure all tests pass

**BRANCH:** Create [branch-name] for this work"
```

### 3. Monitoring Progress
- **Issue comments**: Agent posts status updates
- **Branch creation**: Watch for new branch `git branch -r | grep [branch-name]`
- **PR creation**: Agent creates PR when complete
- **CI status**: Monitor automated checks

### 4. Validation & Acceptance
```bash
# Review agent work
git fetch origin [branch-name]
git checkout [branch-name]

# Run tests
./scripts/test_all.sh

# Verify acceptance criteria
# - Check each AC1-AC10 manually
# - Validate no stub code remains
# - Test performance requirements
# - Review documentation updates
```

## Common Issues & Solutions

### Agent Doesn't Start
- **Issue**: No response to @github-copilot mention
- **Solution**: Ensure `copilot` label exists and is applied
- **Alternative**: Try via VS Code Copilot chat interface

### Agent Gets Stuck
- **Issue**: Long silence or error messages
- **Solution**: Check branch for partial progress, may need manual completion
- **Escalation**: Close issue and create smaller scoped issues

### Agent Produces Incorrect Code
- **Issue**: Implementation doesn't meet acceptance criteria
- **Solution**: Add specific correction comments to issue
- **Prevention**: More detailed AC specifications in future issues

## Best Practices

### Issue Creation
1. **Comprehensive AC list** - Every requirement as separate AC
2. **Priority ordering** - Implementation sequence specified
3. **Success metrics** - Measurable validation criteria
4. **Context links** - Reference PRD sections, existing patterns

### Agent Interaction
1. **Single comprehensive request** - Avoid multiple small comments
2. **Clear branch naming** - Descriptive, not generic
3. **Patience** - Large issues may take 30-60 minutes
4. **Monitoring** - Check progress but don't interrupt

### Post-Completion
1. **Thorough review** - Manual AC validation required
2. **Test everything** - Don't trust CI alone for complex changes
3. **Documentation** - Update process docs with lessons learned
4. **Cleanup** - Delete obsolete branches after merge

## Integration with Existing Process

### Updated Workflow
1. **Manual planning** → Create comprehensive issue
2. **Agent execution** → Trigger with @github-copilot
3. **Human validation** → Review all acceptance criteria
4. **Merge & deploy** → Standard CI/CD process

### Documentation Updates Needed
- Update LESSONS_LEARNED.md with agent-specific learnings
- Extend copilot-instructions.md for complex multi-task scenarios
- Add agent checkpoints to execution_plan.md

## Success Metrics

### Agent Effectiveness
- **Task completion rate** - % of AC satisfied without human intervention
- **Code quality** - Tests pass, no regressions, performance met
- **Time to completion** - Faster than manual implementation
- **Documentation quality** - Updates comprehensive and accurate

### Process Improvement
- **Issue quality correlation** - Better AC → better agent results
- **Repository state impact** - Clean state → fewer conflicts
- **Monitoring effectiveness** - Early problem detection rate