#!/usr/bin/env bash
set -euo pipefail

# Pre-review gate validation for Copilot Code Review
# Ensures PR is ready for systematic review

echo "🔍 Copilot Review Pre-Gate Validation"
echo "====================================="

# Gate 1: Tests pass
echo "📋 Gate 1: Test Validation"
if ./scripts/run_tests.sh > /dev/null 2>&1; then
    echo "✅ Tests pass"
else
    echo "❌ Tests failing - fix before review"
    echo "   Run: ./scripts/run_tests.sh"
    exit 1
fi

# Gate 2: No uncommitted changes
echo ""
echo "📋 Gate 2: Working Directory Clean"
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ No uncommitted changes"
else
    echo "❌ Uncommitted changes detected"
    echo "   Run: git add . && git commit"
    exit 1
fi

# Gate 3: Logger/ErrorCodes integration check
echo ""
echo "📋 Gate 3: Observability Integration"
LOGGER_REFS=$(grep -r "Logger\.add" source/ | wc -l || echo "0")
ERROR_REFS=$(grep -r "ErrorCodes\." source/ | wc -l || echo "0")

if [ "$LOGGER_REFS" -gt 0 ] || [ "$ERROR_REFS" -gt 0 ]; then
    echo "✅ Logging references found (Logger: $LOGGER_REFS, ErrorCodes: $ERROR_REFS)"
else
    echo "⚠️  No logging found - verify if expected for this change"
fi

# Gate 4: Scope check (<300 lines for micro-issue)
echo ""
echo "📋 Gate 4: Scope Validation"
LINES_CHANGED=$(git diff --stat main | tail -1 | grep -o '[0-9]\+ insertions' | grep -o '[0-9]\+' || echo "0")
if [ "$LINES_CHANGED" -le 300 ]; then
    echo "✅ Appropriate scope ($LINES_CHANGED lines changed)"
elif [ "$LINES_CHANGED" -le 600 ]; then
    echo "⚠️  Medium changeset ($LINES_CHANGED lines) - consider targeted review"
else
    echo "❌ Large changeset ($LINES_CHANGED lines) - consider breaking down"
    echo "   Target: <300 lines for micro-issue automation"
fi

# Gate 5: Conventional commit message
echo ""
echo "📋 Gate 5: Commit Convention"
COMMIT_MSG=$(git log -1 --pretty=format:"%s")
if echo "$COMMIT_MSG" | grep -E "^(feat|fix|docs|style|refactor|test|chore):" > /dev/null; then
    echo "✅ Conventional commit format"
else
    echo "⚠️  Non-conventional commit message: $COMMIT_MSG"
    echo "   Consider: feat:, fix:, docs:, test:, refactor:, chore:"
fi

# Gate 6: Branch naming check
echo ""
echo "📋 Gate 6: Branch Naming"
CURRENT_BRANCH=$(git branch --show-current)
if echo "$CURRENT_BRANCH" | grep -E "^(micro-|auto-|feature/|fix/)" > /dev/null; then
    echo "✅ Structured branch name: $CURRENT_BRANCH"
else
    echo "⚠️  Non-standard branch name: $CURRENT_BRANCH"
    echo "   Recommended: micro-*, auto-*, feature/*, fix/*"
fi

echo ""
echo "🎯 Review Preparation Summary"
echo "=============================="

# Get changed files for context
CHANGED_FILES=$(git diff --name-only main | head -10)
echo "📁 Changed Files:"
echo "$CHANGED_FILES" | sed 's/^/   /'

# Suggest appropriate review template
echo ""
echo "📝 Recommended Review Template:"
if echo "$CHANGED_FILES" | grep -q "ScoreEngine"; then
    echo "   🔄 Formula Safety Review (ScoreEngine changes detected)"
elif echo "$CHANGED_FILES" | grep -q "test"; then
    echo "   🧪 Test Adequacy Review (test changes detected)"
elif echo "$CHANGED_FILES" | grep -q "Logger\|ErrorCodes"; then
    echo "   📊 Observability/Logging Review"
elif [ "$LINES_CHANGED" -gt 100 ]; then
    echo "   ⚡ Performance Review (larger changeset)"
else
    echo "   📋 General Micro-Issue PR Review"
fi

echo ""
echo "🚀 Ready for Copilot Review!"
echo ""
echo "Next Steps:"
echo "1. Copy appropriate prompt template from automation/guides/REVIEW_PROMPTS.md"
echo "2. Paste micro-issue success criteria into prompt"
echo "3. Request Copilot review with complete context"
echo "4. Track metrics in issue comment when complete"

# If current directory contains issue context, extract it
if [ -f ".github/ISSUE_TEMPLATE/micro-issue.md" ]; then
    echo ""
    echo "💡 Quick Issue Context Extraction:"
    echo "   gh issue view [ISSUE_NUMBER] --json body | jq -r '.body'"
fi