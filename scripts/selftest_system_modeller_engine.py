#!/usr/bin/env python3
"""Verify a materialized System Modeller Engine before any model mutation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    manifest_path = ROOT / "engine-package.json"
    if not manifest_path.is_file():
        print("ENGINE_FAIL: missing engine-package.json"); return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("engine_id") != "system-modeller":
        print("ENGINE_FAIL: wrong engine ID"); return 2
    for relative, expected in manifest.get("files", {}).items():
        rel = Path(relative)
        target = (ROOT / rel).resolve()
        if rel.is_absolute() or ".." in rel.parts or not target.is_relative_to(ROOT) or not target.is_file():
            print("ENGINE_FAIL: unsafe or missing file", relative); return 2
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            print("ENGINE_FAIL: checksum mismatch", relative); return 2
    for relative in manifest.get("required_files", []):
        if not (ROOT / relative).is_file():
            print("ENGINE_FAIL: required file missing", relative); return 2
    project = ROOT / "examples/reference-order-system/project"
    if not project.is_dir():
        print("ENGINE_FAIL: reference project missing"); return 2
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/validate.py"),
                             str(project), "--format", "json"],
                            cwd=ROOT, capture_output=True, text=True, timeout=45)
    if result.returncode or "VALIDATION_OK" not in result.stdout:
        print("ENGINE_FAIL: validator failed", result.stdout, result.stderr); return 2
    print("ENGINE_OK: manifest checksums and reference-project validation succeeded")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
