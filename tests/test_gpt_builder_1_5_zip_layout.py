#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    registry = yaml.safe_load((ROOT / "runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "dist"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/ci_build.py"), "--output-dir", str(out), "--release-version", "0.0.0-ci"],
            cwd=ROOT,
            check=True,
        )
        artifacts = [
            out / registry["targets"][runtime_id]["artifact_pattern"].format(version="0.0.0-ci")
            for runtime_id in registry["active_targets"]
        ]
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_runtime_zip_layout.py"), *map(str, artifacts)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            return 1
    print("Runtime ZIP root-layout regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
