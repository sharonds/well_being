#!/bin/bash
# Phase 3.2 Comprehensive Verification Script

echo "🚀 Phase 3.2 Production Readiness Verification"
echo "============================================="
echo ""

# Set Python path
export PYTHONPATH=.

# Counter for tests
PASSED=0
FAILED=0

# Function to run test and track results
run_test() {
    local name="$1"
    local cmd="$2"
    
    echo "🔍 Testing: $name"
    if eval "$cmd" > /dev/null 2>&1; then
        echo "  ✅ PASSED"
        ((PASSED++))
    else
        echo "  ❌ FAILED"
        ((FAILED++))
    fi
    echo ""
}

echo "1️⃣ Integrity Checks"
echo "-------------------"
run_test "Current integrity status" \
    "python3 dashboard/scripts/phase3/integrity_monitor.py dashboard/data/garmin_wellness.jsonl --days 7"

run_test "Auto-remediation dry run" \
    "python3 dashboard/scripts/phase3/integrity_auto_remediate.py dashboard/data/garmin_wellness.jsonl --dry-run"

echo "2️⃣ Band Boundary Tests"
echo "----------------------"
run_test "Band boundary unit tests" \
    "python3 dashboard/tests/test_band_boundaries.py"

echo "3️⃣ Auto-run Normalization"
echo "-------------------------"
run_test "Auto-run normalization tests" \
    "python3 dashboard/tests/phase3/test_auto_run_normalization.py"

echo "4️⃣ Configuration Module"
echo "-----------------------"
run_test "Config module validation" \
    "python3 dashboard/config.py"

echo "5️⃣ Score Engine Consistency"
echo "---------------------------"
run_test "Score engine test vectors" \
    "python3 dashboard/tests/test_vectors.py"

echo "6️⃣ Data Validation"
echo "------------------"
run_test "Schema validation" \
    "python3 dashboard/scripts/validate_daily_records.py dashboard/data/garmin_wellness.jsonl"

echo "7️⃣ Privacy Compliance"
echo "---------------------"
run_test "Privacy scan on telemetry" \
    "python3 dashboard/scripts/privacy_scan.py dashboard/data/garmin_wellness.jsonl"

echo "============================================="
echo "📊 RESULTS SUMMARY"
echo "============================================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED - PRODUCTION READY!"
    exit 0
else
    echo "⚠️ Some tests failed - review needed"
    exit 1
fi