#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    result = subprocess.run([sys.executable, str(ROOT / "scripts/check_structure.py")], cwd=ROOT)
    if result.returncode != 0:
        return result.returncode
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    principles = (ROOT / "docs/design-principles.md").read_text(encoding="utf-8")
    assertions = [
        ("YAML" in readme, "README must document YAML as canonical model format"),
        ("Modell och vy" in principles, "design principles must separate model and view"),
        ("Stabila ID" in principles, "design principles must document stable IDs"),
        ("Evidens" in principles, "design principles must document evidence"),
    ]
    failed = [msg for ok, msg in assertions if not ok]
    if failed:
        for msg in failed:
            print("FAIL:", msg)
        return 1
    print("A1 smoke tests OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
