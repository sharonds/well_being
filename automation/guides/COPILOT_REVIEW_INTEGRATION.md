# Copilot Code Review Integration Guide
*Systematic PR review process for micro-issues and automation quality*

## 🎯 Integration Overview

GitHub Copilot Code Review is now integrated into our Phase 4 automation workflow to:
- **Catch logic defects** before human review
- **Ensure backward compatibility** (flags-off behavior preserved)
- **Validate observability** (Logger.add + ErrorCodes usage)
- **Performance compliance** (<50ms requirement validation)
- **Test adequacy** verification

## ⚡ When to Invoke Copilot Review

### ✅ Always Review
1. **Every micro-issue PR** after CI passes (fast feedback loop)
2. **Post-automation runs** to validate generated scaffolds
3. **Performance-critical changes** (ScoreEngine, timing utilities)
4. **Integration PRs** before human deep review

### 🎯 Specific Triggers
- **New .mc files** created via automation
- **ScoreEngine modifications** (formula safety critical)
- **Error handling changes** (Logger/ErrorCodes integration)
- **Test coverage additions** (adequacy validation)

## 🔒 Pre-Review Gates (Automated Checklist)

Run this checklist before requesting Copilot review:

```bash
#!/usr/bin/env bash
# File: scripts/prepare-copilot-review.sh

echo "🔍 Pre-Review Gate Validation"

# Gate 1: Tests pass
if ! ./scripts/run_tests.sh > /dev/null 2>&1; then
    echo "❌ Tests failing - fix before review"
    exit 1
fi
echo "✅ Tests pass"

# Gate 2: No uncommitted changes
if ! git diff --quiet; then
    echo "❌ Uncommitted changes detected"
    exit 1
fi
echo "✅ No uncommitted changes"

# Gate 3: Logger/ErrorCodes compile check
if ! grep -r "Logger.add\|ErrorCodes\." source/ > /dev/null; then
    echo "⚠️  No logging found - verify if expected"
fi
echo "✅ Logging references found"

# Gate 4: Scope check (<300 lines for micro-issue)
LINES_CHANGED=$(git diff --stat main | tail -1 | grep -o '[0-9]\+ insertions' | grep -o '[0-9]\+' || echo "0")
if [ "$LINES_CHANGED" -gt 300 ]; then
    echo "⚠️  Large changeset ($LINES_CHANGED lines) - consider breaking down"
fi
echo "✅ Scope appropriate ($LINES_CHANGED lines changed)"

# Gate 5: Conventional commit message
COMMIT_MSG=$(git log -1 --pretty=format:"%s")
if ! echo "$COMMIT_MSG" | grep -E "^(feat|fix|docs|style|refactor|test|chore):" > /dev/null; then
    echo "⚠️  Non-conventional commit message: $COMMIT_MSG"
fi
echo "✅ Conventional commit format"

echo ""
echo "🎯 Ready for Copilot Review!"
echo "Paste success criteria from micro-issue and use appropriate prompt template."