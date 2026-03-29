#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$SCRIPT_DIR/../data/output"

echo "=== Files before cleanup ==="
ls -lh "$OUT" 2>/dev/null || echo "(directory is empty or missing)"

echo ""
echo "=== Removing generated files from data/output/ ==="
find "$OUT" -type f ! -name '.gitkeep' -delete
echo "Done."

echo ""
echo "=== Files after cleanup ==="
ls -lh "$OUT" 2>/dev/null || echo "(directory is empty)"
