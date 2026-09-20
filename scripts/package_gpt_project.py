#!/usr/bin/env python3
"""Build a deterministic source project package for System Modeller."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
FIXED_DATE = (2020, 1, 1, 0, 0, 0)
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "dist", "distributions", "release-dist"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def included_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES or path.name == ".DS_Store":
            continue
        yield path, rel


def build(out: Path) -> Path:
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for path, rel in included_files():
            info = ZipInfo(f"system-modeller-project/{rel.as_posix()}", FIXED_DATE)
            info.compress_type = ZIP_DEFLATED
            mode = 0o755 if rel.parts and rel.parts[0] == "scripts" and path.suffix in {".py", ".sh"} else 0o644
            info.external_attr = mode << 16
            zf.writestr(info, path.read_bytes())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ns = ap.parse_args()
    print(build(ns.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
