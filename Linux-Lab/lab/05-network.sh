#!/usr/bin/env bash
set -euo pipefail

echo "=== IP Addresses ==="
ip a

echo ""
echo "=== Ping 8.8.8.8 (2 packets) ==="
ping -c 2 8.8.8.8

echo ""
echo "=== HTTP Headers: example.com ==="
curl -I https://example.com
