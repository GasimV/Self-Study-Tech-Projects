#!/usr/bin/env bash
set -euo pipefail

if pgrep -a python > /dev/null 2>&1; then
    echo "Running Python processes:"
    pgrep -a python
else
    echo "No Python process running."
fi
