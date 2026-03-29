#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/data/input"
DEST="$REPO_ROOT/data/backup"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
ARCHIVE="$DEST/backup_$TIMESTAMP.tar.gz"

mkdir -p "$DEST"
tar -czf "$ARCHIVE" -C "$REPO_ROOT/data" input
echo "Backup created: $ARCHIVE"
