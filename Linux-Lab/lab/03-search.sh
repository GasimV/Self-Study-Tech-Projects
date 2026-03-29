#!/usr/bin/env bash
# set -euo pipefail omitted: grep exits 1 when no match found

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/../data/input/app.log"
INPUT="$SCRIPT_DIR/../data/input"

echo "=== INFO lines ==="
grep "INFO" "$LOG" || echo "(none found)"

echo ""
echo "=== ERROR lines ==="
grep "ERROR" "$LOG" || echo "(none found)"

echo ""
echo "=== WARN lines ==="
grep "WARN" "$LOG" || echo "(none found)"

echo ""
echo "=== Count of each level ==="
echo "INFO:  $(grep -c 'INFO'  "$LOG" || true)"
echo "WARN:  $(grep -c 'WARN'  "$LOG" || true)"
echo "ERROR: $(grep -c 'ERROR' "$LOG" || true)"

echo ""
echo "=== find sample.txt ==="
find "$INPUT" -name "sample.txt"
