#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
private_overlay="$repo_dir/quantumult-x.private.conf"
output="$repo_dir/quantum-x-local.conf"

if [[ ! -f "$private_overlay" ]]; then
  echo "Missing private overlay: $private_overlay" >&2
  exit 1
fi

python3 "$repo_dir/scripts/build_quantumultx.py" \
  "$repo_dir/quantumult-x.conf" \
  "$output" \
  "$private_overlay"

echo "Built $output"
