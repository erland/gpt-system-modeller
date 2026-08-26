#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/check_structure.py
for test_file in tests/test_*.py; do
  bash scripts/run_test_isolated.sh "$test_file"
done
