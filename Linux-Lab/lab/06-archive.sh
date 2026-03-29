#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$SCRIPT_DIR/../data/output"
ARCHIVE="$OUT/input_archive.tar.gz"

mkdir -p "$OUT"

echo "=== Creating archive ==="
tar -czf "$ARCHIVE" -C "$SCRIPT_DIR/../data" input
echo "Created: $ARCHIVE"

echo ""
echo "=== Archive contents ==="
tar -tzf "$ARCHIVE"

echo ""
echo "=== Archive size ==="
ls -lh "$ARCHIVE"
