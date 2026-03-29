#!/usr/bin/env bash
set -euo pipefail

# Export custom variables
export LAB_NAME="Linux-Lab"
export LAB_VERSION="1.0"
export LAB_USER="$(whoami)"

echo "=== Custom variables ==="
echo "LAB_NAME:    $LAB_NAME"
echo "LAB_VERSION: $LAB_VERSION"
echo "LAB_USER:    $LAB_USER"

echo ""
echo "=== Common system variables ==="
echo "HOME:    $HOME"
echo "PATH:    $PATH"
echo "SHELL:   $SHELL"
echo "USER:    $USER"
echo "HOSTNAME: $(hostname)"

echo ""
echo "=== All env vars (sorted) ==="
env | sort
