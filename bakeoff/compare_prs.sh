#!/usr/bin/env bash
set -euo pipefail

# Usage: ./bakeoff/compare_prs.sh <base> <branchA> <branchB>
# Prints diff stats, cloc-like size, and file lists for each branch vs base.

if [ $# -ne 3 ]; then
  echo "Usage: $0 <base> <branchA> <branchB>" >&2
  exit 1
fi

BASE=$1
A=$2
B=$3

compare() {
  local base=$1; local br=$2
  echo "=== Compare: ${br} vs ${base} ==="
  git --no-pager diff --stat ${base}...${br}
  echo
  echo "Files changed:"
  git --no-pager diff --name-only ${base}...${br}
  echo
}

compare "$BASE" "$A"
compare "$BASE" "$B"

echo "Tip: run tests per branch with: git checkout <branch> && <your test runner>"
