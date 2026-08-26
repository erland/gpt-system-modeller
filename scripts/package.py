#!/usr/bin/env python3
"""Build a deterministic development ZIP of the System Modeller repository."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "distributions"
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "distributions"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
FIXED_DATE = (2020, 1, 1, 0, 0, 0)

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

def main():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / f"system-modeller-{version}.zip"
    with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for path, rel in included_files():
            info = ZipInfo(f"system-modeller/{rel.as_posix()}", FIXED_DATE)
            info.compress_type = ZIP_DEFLATED
            mode = 0o755 if rel.parts and rel.parts[0] == "scripts" and path.suffix in {".py", ".sh"} else 0o644
            info.external_attr = mode << 16
            zf.writestr(info, path.read_bytes())
    print(out)

if __name__ == "__main__":
    main()
