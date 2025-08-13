#!/usr/bin/env bash
# Pre-commit guard for dashboard security
# Usage: symlink or copy into .git/hooks/pre-commit
set -euo pipefail

fail() { echo "[SECURITY BLOCK] $1" >&2; exit 1; }

# Block committing real env files
if git diff --cached --name-only | grep -E '^(.*/)?\.env(\..*)?$' > /dev/null; then
  fail "Attempt to commit .env or related env file. Remove from staging."
fi

# Block committing private directory contents
if git diff --cached --name-only | grep -E '^(private/|.+/private/)' > /dev/null; then
  fail "Attempt to commit files under private/. These must remain local only."
fi

# Simple heuristic: block large JSON exports (> 200 lines) unless under tests/
while IFS= read -r file; do
  if [[ "$file" == *.json ]] && [[ -f "$file" ]]; then
    lines=$(wc -l < "$file" | tr -d ' ')
    if (( lines > 200 )) && [[ $file != tests/* ]]; then
      fail "Large JSON file ($file, ${lines} lines) looks like raw export. Do not commit."
    fi
  fi
done < <(git diff --cached --name-only)

exit 0
