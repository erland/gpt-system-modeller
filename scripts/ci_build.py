#!/usr/bin/env python3
"""Build and validate all System Modeller project/runtime artifacts."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "runtime-distribution-registry.yaml"
sys.path.insert(0, str(ROOT / "scripts"))

import package_chat
import package_claude
import package_custom_gpt
import package_gpt_project
import package_opencode
import runtime_parity
import validate_claude
import validate_custom_gpt
import validate_opencode
import versioning


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolved_version(explicit: str | None = None):
    return versioning.resolve(explicit=explicit)


def write_checksums(output_dir: Path, paths: list[Path]) -> Path:
    checksum_path = output_dir / "SHA256SUMS.txt"
    lines = [f"{sha256(path)}  {path.name}" for path in sorted(paths, key=lambda p: p.name)]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def build(output_dir: Path, explicit_version: str | None = None) -> dict:
    info = resolved_version(explicit_version)
    version, release = info.repository_version, info.release_version
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    project = output_dir / registry["project_artifact"]["artifact_pattern"].format(version=release)
    runtime_paths = {
        runtime_id: output_dir / registry["targets"][runtime_id]["artifact_pattern"].format(version=release)
        for runtime_id in registry["active_targets"]
    }
    chat = runtime_paths["chat"]
    custom = runtime_paths["custom_gpt"]
    claude = runtime_paths["claude"]
    opencode = runtime_paths["opencode"]

    package_gpt_project.build(project)
    package_chat.build(chat, info.distribution_version)
    package_custom_gpt.build(custom, distribution_version=info.distribution_version)
    package_claude.build(claude, distribution_version=info.distribution_version)
    package_opencode.build(opencode, distribution_version=info.distribution_version)

    findings, custom_summary = validate_custom_gpt.validate(custom, chat, info.distribution_version)
    errors = [f for f in findings if f.get("level") == "ERROR"]
    claude_errors = validate_claude.validate(claude)
    opencode_errors = validate_opencode.validate(opencode)
    if errors or claude_errors or opencode_errors:
        for finding in findings:
            if finding.get("level") == "ERROR":
                print(f"{finding['level']} {finding['code']}: {finding['message']}", file=sys.stderr)
        for message in claude_errors:
            print(f"ERROR CLAUDE: {message}", file=sys.stderr)
        for message in opencode_errors:
            print(f"ERROR OPENCODE: {message}", file=sys.stderr)
        raise RuntimeError(
            f"Runtime validation failed: custom/chat={len(errors)} claude={len(claude_errors)} opencode={len(opencode_errors)}"
        )

    parity_data = runtime_parity.baseline(runtime_parity.load_project())
    parity_path = output_dir / "runtime-parity.yaml"
    parity_path.write_text(yaml.safe_dump(parity_data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    artifacts = [{"type": "project", "path": project}] + [
        {"type": runtime_id, "path": runtime_paths[runtime_id]}
        for runtime_id in registry["active_targets"]
    ]
    checksums = write_checksums(output_dir, [item["path"] for item in artifacts] + [parity_path])

    manifest = {
        "schema_version": 2,
        "repository_version": version,
        "release_version": release,
        "distribution_version": info.distribution_version,
        "version_source": info.source,
        "release_tag": info.tag,
        "artifacts": [
            {
                "type": item["type"],
                "file": item["path"].name,
                "sha256": sha256(item["path"]),
                "bytes": item["path"].stat().st_size,
            }
            for item in artifacts
        ] + [
            {
                "type": "runtime_parity",
                "file": parity_path.name,
                "sha256": sha256(parity_path),
                "bytes": parity_path.stat().st_size,
            },
            {
                "type": "checksums",
                "file": checksums.name,
                "sha256": sha256(checksums),
                "bytes": checksums.stat().st_size,
            },
        ],
        "validation": {
            "custom_gpt_chat": custom_summary,
            "claude": {"errors": 0},
            "opencode": {"errors": 0},
        },
        "parity": parity_data,
    }
    manifest_path = output_dir / "build-manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")

    for path in (project, chat, custom, claude, opencode, parity_path, checksums, manifest_path):
        print(path)
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    ap.add_argument("--release-version", help="Override release version (X.Y.Z or vX.Y.Z)")
    ns = ap.parse_args()
    build(ns.output_dir.resolve(), ns.release_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
