#!/usr/bin/env python3
"""Package GPT Byggaren's offline executable engine as a portable engine archive.

The format is reusable for other GPT projects; this file contains the
GPT Byggaren-specific inventory, not a second distribution builder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ID = "gpt-byggaren"
ARCHIVE_NAME = f"{ENGINE_ID}-engine.zip"
PREFIXES = ("scripts", "templates", "schemas", "src")
REQUIRED = (
    "gpt-project.yaml",
    "scripts/build_distributions.py",
    "scripts/install_distribution_engine.py",
    "scripts/lib/project_model.py",
    "scripts/validate_distributions.py",
    "scripts/validate_portable_skills.py",
    "scripts/selftest_distribution_engine.py",
)
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def inventory(root: Path = ROOT) -> list[Path]:
    paths = [root / "gpt-project.yaml"]
    for prefix in PREFIXES:
        paths.extend(p for p in (root / prefix).rglob("*") if p.is_file())
    paths = sorted(set(p for p in paths if not any(
        part in EXCLUDED_DIRS for part in p.relative_to(root).parts
    ) and p.suffix not in EXCLUDED_SUFFIXES))
    absent = [name for name in REQUIRED if root / name not in paths]
    if absent:
        raise FileNotFoundError(f"Missing engine resource(s): {absent}")
    return paths


def package(root: Path = ROOT, version: str = "0.0.0-dev",
            output: Path | None = None) -> Path:
    output = output or root / "dist" / f"{ENGINE_ID}-engine-{version}.zip"
    files = inventory(root)
    manifest = {
        "schema_version": 1,
        "engine_id": ENGINE_ID,
        "version": version,
        "entrypoint": "scripts/selftest_distribution_engine.py",
        "required_files": list(REQUIRED),
        "python_dependencies": ["PyYAML", "jsonschema"],
        "files": {
            p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, path.read_bytes())
        info = zipfile.ZipInfo("engine-package.json", (2020, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="0.0.0-dev")
    args = parser.parse_args()
    print(package(version=args.version))
