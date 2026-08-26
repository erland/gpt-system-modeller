#!/usr/bin/env python3
"""Validate the repository contract introduced through Plan A step A4."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md", "VERSION", "CHANGELOG.md", "STATUS.md", ".gitignore",
    "docs/design-principles.md", "docs/mvp-scope.md", "docs/modeling-principles.md",
    "docs/model-format.md", "metamodel/common.yaml", "metamodel/id-prefixes.yaml",
    "schemas/common.schema.json", "scripts/package.py", "scripts/test.sh",
]
REQUIRED_DIRS = [
    "instructions", "metamodel", "schemas", "scripts", "templates",
    "examples", "tests", "docs",
]

def main() -> int:
    missing = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            missing.append(rel)
    for rel in REQUIRED_DIRS:
        if not (ROOT / rel).is_dir():
            missing.append(rel + "/")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else ""
    if not version:
        missing.append("VERSION(non-empty)")
    if missing:
        print("A4 structure check FAILED")
        for item in missing:
            print(f"- missing: {item}")
        return 1
    print(f"A4 structure check OK – version {version}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
