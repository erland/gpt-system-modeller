#!/usr/bin/env python3
"""Perform deterministic release-readiness checks for all System Modeller artifacts."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import tempfile
import zipfile
import yaml
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ci_build
import validate_claude
import validate_custom_gpt
import validate_opencode
import versioning

FORBIDDEN_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "distributions"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_zip(path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if not names:
            errors.append(f"{path.name}: archive is empty")
        for name in names:
            parts = Path(name).parts
            if any(p in FORBIDDEN_PARTS for p in parts):
                errors.append(f"{path.name}: forbidden path {name}")
            if Path(name).suffix in FORBIDDEN_SUFFIXES or name.endswith(".DS_Store"):
                errors.append(f"{path.name}: forbidden file {name}")
    return errors


def build_and_check(output_dir: Path, explicit_version: str | None = None) -> dict:
    info = versioning.resolve(explicit=explicit_version)
    version = info.repository_version
    release = info.release_version
    output_dir.mkdir(parents=True, exist_ok=True)

    names = {
        "project": f"system-modeller-project-v{release}.zip",
        "chat": f"system-modeller-chat-v{release}.zip",
        "custom_gpt": f"system-modeller-custom-gpt-v{release}.zip",
        "claude": f"system-modeller-claude-v{release}.zip",
        "opencode": f"system-modeller-opencode-v{release}.zip",
        "runtime_parity": "runtime-parity.yaml",
        "checksums": "SHA256SUMS.txt",
        "manifest": "build-manifest.yaml",
    }

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        first = td / "first"
        second = td / "second"
        ci_build.build(first, explicit_version)
        ci_build.build(second, explicit_version)

        errors: list[str] = []
        for name in names.values():
            a, b = first / name, second / name
            if not a.is_file() or not b.is_file():
                errors.append(f"missing build output: {name}")
                continue
            if digest(a) != digest(b):
                errors.append(f"non-deterministic build output: {name}")

        findings, custom_parity = validate_custom_gpt.validate(
            first / names["custom_gpt"], first / names["chat"], info.distribution_version
        )
        errors.extend(f"{f['code']}: {f['message']}" for f in findings if f.get("level") == "ERROR")
        errors.extend(f"CLAUDE: {e}" for e in validate_claude.validate(first / names["claude"]))
        errors.extend(f"OPENCODE: {e}" for e in validate_opencode.validate(first / names["opencode"]))

        for typ in ("project", "chat", "custom_gpt", "claude", "opencode"):
            path = first / names[typ]
            if path.is_file():
                errors.extend(inspect_zip(path))

        manifest_path = first / names["manifest"]
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        if manifest.get("repository_version") != version:
            errors.append("build manifest repository_version mismatch")
        if manifest.get("release_version") != release:
            errors.append("build manifest release_version mismatch")
        if manifest.get("distribution_version") != info.distribution_version:
            errors.append("build manifest distribution_version mismatch")

        arts = {x.get("type"): x for x in manifest.get("artifacts", [])}
        for typ, name in names.items():
            if typ == "manifest":
                continue
            path = first / name
            if path.is_file() and arts.get(typ, {}).get("sha256") != digest(path):
                errors.append(f"build manifest checksum mismatch: {typ}")

        checksum_lines = (first / names["checksums"]).read_text(encoding="utf-8").splitlines()
        checksum_map = {}
        for line in checksum_lines:
            if "  " in line:
                checksum, filename = line.split("  ", 1)
                checksum_map[filename] = checksum
        for typ in ("project", "chat", "custom_gpt", "claude", "opencode", "runtime_parity"):
            name = names[typ]
            path = first / name
            if path.is_file() and checksum_map.get(name) != digest(path):
                errors.append(f"SHA256SUMS mismatch: {name}")

        for name in names.values():
            src = first / name
            if src.is_file():
                (output_dir / name).write_bytes(src.read_bytes())

        parity = yaml.safe_load((first / names["runtime_parity"]).read_text(encoding="utf-8"))
        result = {
            "schema_version": 2,
            "repository_version": version,
            "release_version": release,
            "distribution_version": info.distribution_version,
            "version_source": info.source,
            "release_tag": info.tag,
            "status": "READY" if not errors else "NOT_READY",
            "local_checks": {
                "deterministic_dual_build": not any("non-deterministic" in e for e in errors),
                "distribution_parity": not any(("parity" in e.lower() or "mismatch" in e.lower()) for e in errors),
                "zip_hygiene": not any(("forbidden" in e or "archive is empty" in e) for e in errors),
                "manifest_checksums": not any("manifest checksum mismatch" in e for e in errors),
                "sha256sums": not any("SHA256SUMS mismatch" in e for e in errors),
            },
            "github_actions_runtime_verified": False,
            "github_actions_note": "Requires one real workflow run; local checks cannot prove GitHub-hosted runner behavior.",
            "parity": parity,
            "custom_gpt_chat_parity": custom_parity,
            "artifacts": [
                {"type": typ, "file": name, "sha256": digest(output_dir / name) if (output_dir / name).is_file() else None}
                for typ, name in names.items()
                if typ != "manifest"
            ],
            "errors": errors,
        }
        report = output_dir / "release-readiness.yaml"
        report.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, default=ROOT / "release-dist")
    ap.add_argument("--release-version", help="Override release version (X.Y.Z or vX.Y.Z)")
    ns = ap.parse_args()
    result = build_and_check(ns.output_dir.resolve(), ns.release_version)
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0 if result["status"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
