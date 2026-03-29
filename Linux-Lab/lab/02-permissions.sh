#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$SCRIPT_DIR/../scripts"

echo "=== Before ==="
ls -l "$SCRIPTS"

# Make all scripts executable
chmod +x "$SCRIPTS"/*.sh
echo ""
echo "=== After chmod +x ==="
ls -l "$SCRIPTS"

# Demonstrate chmod modes
echo ""
echo "chmod 600 (owner read/write only):"
chmod 600 "$SCRIPTS/common.sh"
ls -l "$SCRIPTS/common.sh"

echo ""
echo "chmod 755 (owner rwx, others rx) — restoring:"
chmod 755 "$SCRIPTS/common.sh"
ls -l "$SCRIPTS/common.sh"
