---
name: Micro-Issue with Copilot Review
about: Single-file automation task with integrated code review process
title: 'Micro: [COMPONENT_NAME] - [BRIEF_DESCRIPTION]'
labels: automation, micro-issue
assignees: ''
---

## 🎯 Deliverable
- [ ] Create/update single file: `[path/to/file.ext]`
- [ ] Implement [specific functionality]

## 📋 Success Criteria
- [ ] File exists and compiles without errors
- [ ] [Specific requirement 1]
- [ ] [Specific requirement 2]  
- [ ] [Specific requirement 3]
- [ ] Follows existing code patterns and conventions
- [ ] Includes appropriate error handling with Logger.add() + ErrorCodes
- [ ] **Copilot code review**: Zero unresolved must-fix items

## 🤖 Automation Details
```bash
# Step 1: Create and run automation
gh workflow run simple-automation.yml \
  --field task_name=[task-name] \
  --field issue_number={{ issue.number }}

# Step 2: Prepare for Copilot review
./scripts/prepare-copilot-review.sh

# Step 3: Use appropriate review template
# See: automation/guides/REVIEW_PROMPTS.md
```

## 📊 Expected Automation Time
- **Complexity**: Simple (single file, clear template)
- **Automation Runtime**: 5-10 minutes
- **Review Time**: 2-5 minutes
- **Total Cycle**: <15 minutes

## 🔍 Review Requirements
- [ ] **Pre-review gates passed** (automated validation)
- [ ] **Appropriate prompt template used** (see REVIEW_PROMPTS.md)
- [ ] **Must-fix items resolved** before merge
- [ ] **Metrics tracked** in issue comments

## 📈 Success Metrics Template
```markdown
## Copilot Review Metrics
**Review Turnaround:** [X] minutes
**Findings:** Must-fix: [N] | Should-fix: [N] | Nice-to-have: [N]
**Adoption Rate:** [X]% of suggestions implemented
**Quality Score:** ✅ Ready for merge
```

## 🎓 Definition of Done
- [ ] Automation completed successfully
- [ ] All success criteria validated
- [ ] Copilot review completed with zero unresolved must-fix items
- [ ] PR merged with conventional commit message
- [ ] Issue closed with metrics summary

---
**Part of**: [Reference parent issue if applicable]
**Estimated Impact**: [Time saved, quality improvement, etc.]