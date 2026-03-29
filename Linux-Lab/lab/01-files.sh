#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$SCRIPT_DIR/../data/output"

mkdir -p "$OUT"

# Copy a file
cp "$SCRIPT_DIR/../data/input/sample.txt" "$OUT/sample_copy.txt"
echo "Copied sample.txt -> output/sample_copy.txt"

# Move/rename it
mv "$OUT/sample_copy.txt" "$OUT/sample_renamed.txt"
echo "Renamed sample_copy.txt -> sample_renamed.txt"

# Create a new file
echo "Hello from 01-files.sh" > "$OUT/hello.txt"
echo "Created hello.txt"

# List output directory
echo ""
echo "Contents of data/output/:"
ls -lh "$OUT"
