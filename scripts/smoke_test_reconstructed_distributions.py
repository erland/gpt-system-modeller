#!/usr/bin/env python3
"""Inspect produced runtime ZIPs offline; never authorize release or build."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import yaml

INSTRUCTIONS = {
    "chat": "assistant/instructions.md",
    "claude": "project/instructions.md",
    "opencode": "AGENTS.md",
}
REQUIRED = {
    "chat": ("START-HERE.md", "VERSION", "MANIFEST.json"),
    "claude": ("README.md", "VERSION", "MANIFEST.json", "project/runtime-contract.json"),
    "opencode": ("README.md", "VERSION", "MANIFEST.json", "opencode.json", ".opencode/runtime-contract.json"),
    "plugin": ("plugin.json", "README.md", "VERSION", "MANIFEST.json", "runtime-contract.json"),
}


def evaluate(project: Path, packages: dict[str, Path]) -> dict:
    project = project.resolve()
    cfg = yaml.safe_load((project / "gpt-project.yaml").read_text(encoding="utf-8"))
    if not isinstance(cfg.get("reconstruction"), dict):
        raise ValueError("Expected reconstructed project")
    canonical = (project / cfg["instructions"]["canonical"]).read_bytes()
    results = {}
    for runtime, location in packages.items():
        if runtime not in REQUIRED:
            raise ValueError(f"Unsupported runtime: {runtime}")
        issues = []
        with zipfile.ZipFile(location) as bundle:
            names = bundle.namelist()
            if len(names) != len(set(names)):
                issues.append("Duplicate ZIP entry")
            if any(name.startswith("/") or ".." in Path(name).parts or "\\" in name for name in names):
                issues.append("Unsafe ZIP path")
            for required in REQUIRED[runtime]:
                if required not in names:
                    issues.append(f"Missing runtime artifact: {required}")
            if runtime == "plugin" and not any(n.startswith("skills/") and n.endswith("/SKILL.md") for n in names):
                issues.append("Missing plugin skill")
            if runtime == "plugin" and any(Path(n).name == "mcp.json" for n in names):
                issues.append("Forbidden mcp.json inside plugin")
            instruction = INSTRUCTIONS.get(runtime)
            if instruction and instruction in names and bundle.read(instruction) != canonical:
                issues.append("Canonical instruction mismatch")
            if instruction and instruction not in names:
                issues.append(f"Missing instruction: {instruction}")
            if "MANIFEST.json" in names:
                try:
                    manifest = json.loads(bundle.read("MANIFEST.json"))
                    for item in manifest.get("files", []):
                        entry = item.get("path")
                        if entry not in names or hashlib.sha256(bundle.read(entry)).hexdigest() != item.get("sha256"):
                            issues.append(f"Manifest checksum mismatch: {entry}")
                except (ValueError, TypeError, KeyError):
                    issues.append("Invalid runtime manifest")
            # Plugin instructions are adapter-specific; textual byte identity is not sufficient.
            if runtime == "plugin":
                issues.append("Plugin instruction semantics and execution require manual parity review")
        results[runtime] = {"archive": str(location), "checks_passed": not issues, "issues": issues}
    return {
        "result": "offline_checks_passed" if all(not v["issues"] for v in results.values()) else "review_required",
        "runtimes": results,
        "functional_parity_verified": False,
        "release_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    for runtime in REQUIRED:
        parser.add_argument("--" + runtime + "-zip")
    args = parser.parse_args()
    packages = {runtime: Path(getattr(args, runtime + "_zip")) for runtime in REQUIRED
                if getattr(args, runtime + "_zip")}
    if not packages:
        parser.error("Provide at least one runtime ZIP")
    try:
        result = evaluate(Path(args.project_root), packages)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, yaml.YAMLError) as exc:
        print(f"Runtime smoke test error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "offline_checks_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
