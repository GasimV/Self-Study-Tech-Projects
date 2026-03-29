#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Running backup script ==="
bash "$SCRIPT_DIR/../scripts/backup.sh"

echo ""
echo "=== Backup directory contents ==="
ls -lh "$SCRIPT_DIR/../data/backup/"
