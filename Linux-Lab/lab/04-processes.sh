#!/usr/bin/env bash
# set -euo pipefail omitted: pgrep exits 1 when no match

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Bash processes ==="
ps aux | grep '[b]ash'

echo ""
echo "=== Python processes ==="
if pgrep -a python > /dev/null 2>&1; then
    pgrep -a python
else
    echo "No Python process running."
fi

echo ""
echo "=== Current process info ==="
echo "PID: $$"
echo "Parent PID: $PPID"
