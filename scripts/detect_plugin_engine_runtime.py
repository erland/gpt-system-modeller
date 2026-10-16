#!/usr/bin/env python3
"""Deterministic capability preflight; never executes or reconstructs engine code."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = (
    "gpt-project.yaml",
    "scripts/build_distributions.py",
    "scripts/install_distribution_engine.py",
    "scripts/selftest_distribution_engine.py",
    "scripts/validate_distributions.py",
    "scripts/lib/project_model.py",
)


def detect(engine_root: Path, fallback_zip: Path | None = None) -> dict:
    root = engine_root.resolve()
    present = [str(p) for p in REQUIRED if (root / p).is_file()]
    missing = [p for p in REQUIRED if p not in present]
    if not missing:
        return {"mode": "direct", "engine_root": str(root), "missing": [],
                "reason": "Installed canonical engine files accessible; self-test still required"}
    if fallback_zip is not None and fallback_zip.is_file():
        return {"mode": "zip_fallback", "engine_root": str(root),
                "fallback_zip": str(fallback_zip.resolve()), "missing": missing,
                "reason": "Installed engine unavailable; original Engine ZIP is accessible"}
    return {"mode": "blocked", "engine_root": str(root), "missing": missing,
            "reason": "Neither installed engine nor original Engine ZIP accessible"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--fallback-zip", type=Path)
    args = parser.parse_args()
    report = detect(args.engine_root, args.fallback_zip)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["mode"] != "blocked" else 2


if __name__ == "__main__":
    sys.exit(main())
