#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/check_structure.py
python3 scripts/validate_project_contract.py
python3 scripts/validate_instruction_adherence.py --project-root .
# The 1.5 distribution-only checks are archived as historical tests; never run as 1.6 gates.
python3 -m pytest -q tests --ignore=tests/test_runtime_resource_layout.py
# A/B/C scripts are standalone programs, not pytest test functions.
# Legacy incompatibilities and timeouts are blocking, never silent skips.
# Standalone A/B/C tests are enforced by the matrix jobs in .github/workflows/ci.yml.
# Do not run them twice or accept historical exclusions without replacement tests.
