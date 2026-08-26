#!/usr/bin/env python3
"""Build and parity-validate System Modeller CI distribution artifacts (A34)."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import package_chat  # noqa: E402
import package_custom_gpt  # noqa: E402
import validate_custom_gpt  # noqa: E402
import versioning  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolved_version(explicit: str | None = None):
    return versioning.resolve(explicit=explicit)


def build(output_dir: Path, explicit_version: str | None = None) -> dict:
    info = resolved_version(explicit_version)
    version, release = info.repository_version, info.release_version
    output_dir.mkdir(parents=True, exist_ok=True)
    chat = output_dir / f"system-modeller-chat-v{release}.zip"
    custom = output_dir / f"system-modeller-custom-gpt-v{release}.zip"
    package_chat.build(chat, info.distribution_version)
    package_custom_gpt.build(custom, distribution_version=info.distribution_version)
    findings, summary = validate_custom_gpt.validate(custom, chat, info.distribution_version)
    errors = [f for f in findings if f.get("level") == "ERROR"]
    if errors:
        for finding in findings:
            print(f"{finding['level']} {finding['code']}: {finding['message']}", file=sys.stderr)
        raise RuntimeError(f"Custom GPT / Chat parity validation failed with {len(errors)} errors")
    manifest = {
        "schema_version": 1,
        "repository_version": version,
        "release_version": release,
        "distribution_version": info.distribution_version,
        "version_source": info.source,
        "release_tag": info.tag,
        "artifacts": [
            {"type": "chat", "file": chat.name, "sha256": sha256(chat), "bytes": chat.stat().st_size},
            {"type": "custom_gpt", "file": custom.name, "sha256": sha256(custom), "bytes": custom.stat().st_size},
        ],
        "parity": summary,
    }
    manifest_path = output_dir / "build-manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(chat)
    print(custom)
    print(manifest_path)
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
