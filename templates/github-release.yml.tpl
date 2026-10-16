name: Build release distributions

on:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  build-release:
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
      - name: Derive version from release tag
        id: version
        shell: bash
        run: |
          set -euo pipefail
          TAG="${{ github.event.release.tag_name }}"
          if [[ ! "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
            echo "Unsupported release tag: $TAG"
            exit 1
          fi
          echo "version=${TAG#v}" >> "$GITHUB_OUTPUT"
      - name: Test
        run: python -m pytest -q -p no:cacheprovider
      - name: Build distributions
        run: python scripts/build_distributions.py --project-root . --version "${{ steps.version.outputs.version }}" --targets project,chat,custom-gpt
      - name: Validate distributions
        run: python scripts/validate_distributions.py --project-root .
      - name: Upload release artifacts
        env:
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: |
          set -euo pipefail
          gh release upload "${{ github.event.release.tag_name }}" dist/*.zip dist/SHA256SUMS.txt dist/DELIVERY-MANIFEST.json --clobber
