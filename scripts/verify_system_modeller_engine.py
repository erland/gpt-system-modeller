#!/usr/bin/env python3
"""Smoke test deterministic Engine delivery and exact-version plugin handoff."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    version = args.version
    archive = ROOT / "dist" / f"system-modeller-engine-{version}.zip"
    plugin = ROOT / "dist" / f"system-modeller-plugin-{version}.zip"
    if not archive.is_file() or not plugin.is_file():
        raise SystemExit("Missing Engine or Plugin ZIP")
    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            names = z.namelist()
            assert len(names) == len(set(names))
            assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names)
            assert len(names) < 1000 and sum(info.file_size for info in z.infolist()) < 40_000_000
            z.extractall(destination)
        result = subprocess.run(
            [sys.executable, "-B", "scripts/selftest_system_modeller_engine.py"],
            cwd=destination, capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, (result.stdout, result.stderr)
        assert "ENGINE_OK" in result.stdout
    with zipfile.ZipFile(plugin) as z:
        names = z.namelist()
        skills = [n for n in names if n.endswith("/SKILL.md") and n.startswith("skills/")]
        assert len(skills) == 6, skills
        expected = f"https://github.com/erland/gpt-system-modeller/releases/download/v{version}/system-modeller-engine-{version}.zip"
        for name in skills:
            body = z.read(name).decode("utf-8")
            assert "Work-first execution and Engine ZIP fallback" in body, name
            assert ("no public release link" in body) if version == "0.0.0-ci" else (expected in body), name
            assert "Without a verified validator, stop" in body, name
            assert "## Executable Engine ZIP preflight" not in body, name
            assert "The Plugin does not embed the executable engine" not in body, name
            assert "No verified release download link is configured" not in body, name
            assert "For read-only explanation" in body, name
            assert "If direct execution is unavailable" in body, name
    print("ENGINE_DELIVERY_OK", version)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
