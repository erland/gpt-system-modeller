name: CI

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    env:
      PYTHONDONTWRITEBYTECODE: "1"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install pyyaml jsonschema pytest
      - name: Lint
        run: python scripts/lint_gpt_project.py --project-root .
      - name: Test
        run: python -m pytest -q -p no:cacheprovider
      - name: Validate instruction adherence
        if: ${{ hashFiles('scripts/validate_instruction_adherence.py') != '' }}
        run: python scripts/validate_instruction_adherence.py --project-root .
      - name: Build distributions
        run: python scripts/build_distributions.py --project-root . --version 0.0.0-ci --targets project,chat,custom-gpt
      - name: Validate distributions
        run: python scripts/validate_distributions.py --project-root .
