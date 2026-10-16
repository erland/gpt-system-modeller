#!/usr/bin/env python3
"""Isolated integration exercise using actual builders; never promote source to release-ready."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

from build_distributions import build_chat, build_claude, build_opencode, build_plugin, stable_write_zip
from smoke_test_reconstructed_distributions import evaluate

BUILDERS = {"chat": build_chat, "claude": build_claude, "opencode": build_opencode, "plugin": build_plugin}


def exercise(source: Path, targets: list[str]) -> dict:
    source = source.resolve()
    original = yaml.safe_load((source / "gpt-project.yaml").read_text(encoding="utf-8"))
    recon = original.get("reconstruction")
    if not isinstance(recon, dict) or recon.get("release_ready") is not False:
        raise ValueError("Only non-release reconstructed projects are supported")
    if len(set(targets)) != len(targets) or not targets or any(t not in BUILDERS for t in targets):
        raise ValueError("Select one or more distinct supported runtimes")
    with tempfile.TemporaryDirectory(prefix="reconstructed-e2e-") as folder:
        root = Path(folder) / "project"
        shutil.copytree(source, root, ignore=shutil.ignore_patterns(".git", "build", "dist", "__pycache__"))
        cfg = yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8"))
        cfg["reconstruction"]["release_ready"] = False
        archives = {}
        errors = {}
        for runtime in targets:
            try:
                built = BUILDERS[runtime](root, cfg, root / "build", "0.0.0-e2e")
                archive = root / "dist" / (runtime + ".zip")
                stable_write_zip(archive, built, [p for p in built.rglob("*") if p.is_file()])
                archives[runtime] = archive
            except (KeyError, ValueError, OSError, SystemExit) as exc:
                errors[runtime] = str(exc)
        evidence = evaluate(root, archives) if archives else None
        return {
            "result": "review_required" if errors or not evidence or evidence["result"] != "offline_checks_passed" else "offline_checks_passed",
            "attempted": targets,
            "built": sorted(archives),
            "build_errors": errors,
            "package_evidence": evidence,
            "release_ready": False,
            "functional_parity_verified": False,
            "isolated": True,
            "limitations": [
                "Adapters may require additional canonical configuration before they can build.",
                "An offline package check is not a live runtime behavior test.",
                "The release gate in the ordinary distribution builder remains unchanged.",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--targets", default="chat,claude,opencode,plugin")
    args = parser.parse_args()
    try:
        result = exercise(Path(args.project_root), [t.strip() for t in args.targets.split(",") if t.strip()])
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        print(f"Isolated exercise failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "offline_checks_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
