#!/usr/bin/env python3
"""Validate that runtime ZIPs expose their runtime files directly at ZIP root."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = [name for name in zf.namelist() if name and not name.endswith("/")]
    if not names:
        return [f"{path.name}: archive is empty"]

    top = {Path(name).parts[0] for name in names if Path(name).parts}
    if len(top) == 1 and all(len(Path(name).parts) > 1 for name in names):
        root = next(iter(top))
        errors.append(f"{path.name}: all files are wrapped in unexpected top-level directory {root!r}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("artifacts", nargs="+", type=Path)
    ns = ap.parse_args()
    errors: list[str] = []
    for artifact in ns.artifacts:
        errors.extend(validate(artifact))
    if errors:
        for error in errors:
            print("ERROR", error)
        return 1
    print("OK: runtime ZIP files are rooted directly in the archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
