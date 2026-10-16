#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def load_config(root: Path) -> dict:
    return yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8"))


def expected_files(cfg: dict, version: str) -> list[str]:
    project_id = cfg["project"]["id"]
    files = [f"{project_id}-project-{version}.zip"]
    for target in cfg.get("build_system", {}).get("targets", []):
        if target == "project":
            continue
        target_cfg = (cfg.get("build_system", {}).get("runtime_targets") or {}).get(target)
        if not target_cfg:
            continue
        runtime_key = target_cfg["runtime_key"]
        if not cfg.get("runtime", {}).get(runtime_key, {}).get("enabled"):
            continue
        files.append(
            target_cfg["filename_pattern"]
            .replace("<project-id>", project_id)
            .replace("<version>", version)
        )
    if cfg.get("engine", {}).get("enabled") and "plugin" in cfg.get("build_system", {}).get("targets", []) and cfg.get("runtime", {}).get("plugin", {}).get("enabled"):
        files.append(f"{project_id}-engine-{version}.zip")
    files.extend(["SHA256SUMS.txt", "DELIVERY-MANIFEST.json"])
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--version", required=True)
    ap.add_argument("--print-files", action="store_true")
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    cfg = load_config(root)
    dist = root / "dist"
    expected = expected_files(cfg, args.version)

    missing = [name for name in expected if not (dist / name).is_file()]
    if missing:
        for name in missing:
            print(f"MISSING: dist/{name}")
        return 1

    manifest_path = dist / "DELIVERY-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_files = {item["file"] for item in manifest.get("artifacts", [])}
    for name in expected:
        if name == "DELIVERY-MANIFEST.json":
            continue
        if name not in manifest_files:
            print(f"MANIFEST MISSING: {name}")
            return 1

    if args.print_files:
        for name in expected:
            print(f"dist/{name}")
    else:
        print(f"Verified {len(expected)} expected distribution files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
