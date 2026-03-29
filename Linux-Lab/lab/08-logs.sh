#!/usr/bin/env bash
# set -euo pipefail omitted: grep exits 1 when no match

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/../data/input/app.log"

echo "=== First 5 lines ==="
head -5 "$LOG"

echo ""
echo "=== Last 5 lines ==="
tail -5 "$LOG"

echo ""
echo "=== All ERROR lines ==="
grep "ERROR" "$LOG" || echo "(no errors found)"

echo ""
echo "=== Lines containing 'Database' ==="
grep -i "database" "$LOG" || echo "(none found)"

echo ""
echo "=== Total lines in log ==="
wc -l < "$LOG"
