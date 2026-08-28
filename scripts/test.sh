#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/check_structure.py
python3 scripts/validate_instruction_adherence.py --project-root .
for test_file in tests/test_*.py; do
  bash scripts/run_test_isolated.sh "$test_file"
done
