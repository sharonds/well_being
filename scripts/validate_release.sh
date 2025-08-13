#!/bin/bash

# Release Validation Script
# Comprehensive checks before GA release

set -e

echo "🚀 Release Validation for Wellness Dashboard"
echo "==========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to run check
run_check() {
    local name="$1"
    local cmd="$2"
    
    echo -n "Checking: $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Function for warning checks
run_warning() {
    local name="$1"
    local cmd="$2"
    
    echo -n "Checking: $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}"
        ((WARNINGS++))
        return 1
    fi
}

echo "1️⃣ Code Quality Checks"
echo "----------------------"
run_check "Python syntax" "python3 -m py_compile dashboard/**/*.py"
run_check "No hardcoded secrets" "! grep -r 'password\|secret\|token' dashboard/scripts --include='*.py' | grep -v '#'"
run_check "Test files exist" "ls dashboard/tests/*.py > /dev/null 2>&1"
echo ""

echo "2️⃣ Operational Checks"
echo "--------------------"
run_check "Metrics exporter" "python3 dashboard/scripts/ops/metrics_exporter.py --format json"
run_check "Alert system" "python3 dashboard/scripts/ops/alerts.py --dry-run"
run_check "Integrity monitor" "python3 -c 'from dashboard.scripts.phase3.integrity_monitor import calculate_integrity_failure_rate'"
run_check "Config module" "python3 dashboard/config.py"
echo ""

echo "3️⃣ CI/CD Checks"
echo "---------------"
run_check "Quality gates workflow" "test -f .github/workflows/quality-gates.yml"
run_check "Daily ops workflow" "test -f .github/workflows/daily-ops.yml"
run_check "Release automation" "test -f .github/workflows/release-automation.yml"
echo ""

echo "4️⃣ Documentation Checks"
echo "----------------------"
run_check "README exists" "test -f README.md"
run_check "CHANGELOG up to date" "grep -q '3.3.0' CHANGELOG.md"
run_check "SLOs documented" "test -f docs/SLOs.md"
run_check "Runbooks created" "ls docs/runbooks/*.md > /dev/null 2>&1"
run_check "Release checklist" "test -f RELEASE_CHECKLIST.md"
echo ""

echo "5️⃣ Data Management"
echo "-----------------"
run_check "Retention policy" "python3 -c 'from dashboard.scripts.phase3.retention_policy import RetentionManager'"
run_check "Atomic writes" "python3 -c 'from dashboard.utils.file_utils import atomic_write_jsonl'"
run_check "Duplicate guard" "python3 -c 'from dashboard.scripts.duplicate_guard import check_duplicate'"
echo ""

echo "6️⃣ Current Metrics"
echo "-----------------"
if command -v jq &> /dev/null; then
    # Export current metrics
    METRICS=$(python3 dashboard/scripts/ops/metrics_exporter.py --format json 2>/dev/null || echo "{}")
    
    if [ "$METRICS" != "{}" ]; then
        INTEGRITY_RATE=$(echo "$METRICS" | jq -r '.integrity.failure_rate_14d_pct // "N/A"')
        AUTO_RUN_RATE=$(echo "$METRICS" | jq -r '.auto_run.success_rate_pct // "N/A"')
        DAYS_BEHIND=$(echo "$METRICS" | jq -r '.ingestion.days_behind // "N/A"')
        
        echo "  Integrity Failure Rate: ${INTEGRITY_RATE}%"
        echo "  Auto-run Success Rate: ${AUTO_RUN_RATE}%"
        echo "  Data Ingestion Lag: ${DAYS_BEHIND} days"
        
        # Check thresholds
        if [ "$INTEGRITY_RATE" != "N/A" ] && (( $(echo "$INTEGRITY_RATE < 1" | bc -l) )); then
            echo -e "  Integrity: ${GREEN}✅ GOOD${NC}"
            ((PASSED++))
        else
            echo -e "  Integrity: ${RED}❌ EXCEEDS THRESHOLD${NC}"
            ((FAILED++))
        fi
        
        if [ "$AUTO_RUN_RATE" != "N/A" ] && (( $(echo "$AUTO_RUN_RATE >= 90" | bc -l) )); then
            echo -e "  Auto-run: ${GREEN}✅ MEETS TARGET${NC}"
            ((PASSED++))
        else
            echo -e "  Auto-run: ${YELLOW}⚠️ BELOW TARGET${NC}"
            ((WARNINGS++))
        fi
    else
        echo -e "  ${YELLOW}⚠️ Unable to collect metrics${NC}"
        ((WARNINGS++))
    fi
else
    echo "  ⚠️ jq not installed - skipping metrics analysis"
    ((WARNINGS++))
fi
echo ""

echo "7️⃣ Test Execution"
echo "----------------"
echo "Running critical tests..."

# Run tests with timeout
if timeout 30 python3 -m pytest dashboard/tests/test_duplicate_guard_normalization.py -q 2>/dev/null; then
    echo -e "  Duplicate guard tests: ${GREEN}✅ PASSED${NC}"
    ((PASSED++))
else
    echo -e "  Duplicate guard tests: ${RED}❌ FAILED${NC}"
    ((FAILED++))
fi

if timeout 30 python3 -m pytest dashboard/tests/test_band_boundaries.py -q 2>/dev/null; then
    echo -e "  Band boundary tests: ${GREEN}✅ PASSED${NC}"
    ((PASSED++))
else
    echo -e "  Band boundary tests: ${RED}❌ FAILED${NC}"
    ((FAILED++))
fi
echo ""

echo "==========================================="
echo "📊 VALIDATION SUMMARY"
echo "==========================================="
echo -e "✅ Passed:   ${GREEN}$PASSED${NC}"
echo -e "⚠️  Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "❌ Failed:   ${RED}$FAILED${NC}"
echo ""

# Determine overall status
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 READY FOR RELEASE!${NC}"
        echo "All validation checks passed. System is ready for GA."
        exit 0
    else
        echo -e "${YELLOW}⚠️ READY WITH WARNINGS${NC}"
        echo "System can be released but review warnings first."
        exit 0
    fi
else
    echo -e "${RED}🚫 NOT READY FOR RELEASE${NC}"
    echo "Critical validation checks failed. Address issues before release."
    exit 1
fi