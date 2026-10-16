#!/usr/bin/env python3
"""Offline diagnostic for materializing and executing the canonical GPT engine.

Produces machine-readable stage results. Does not modify the supplied source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STAGES = ("source", "materialize", "integrity", "installer", "build")
REQUIRED = (
    "gpt-project.yaml",
    "scripts/build_distributions.py",
    "scripts/install_distribution_engine.py",
    "scripts/lib/project_model.py",
    "scripts/validate_distributions.py",
    "scripts/validate_portable_skills.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def diagnose(source: Path) -> dict:
    report = {"ok": False, "stages": [], "required_files": list(REQUIRED)}
    def stage(name, ok, detail, **kwargs):
        report["stages"].append({"stage": name, "ok": ok, "detail": detail, **kwargs})
        return ok

    source = source.resolve()
    missing = [p for p in REQUIRED if not (source / p).is_file()]
    if missing:
        stage("source", False, "Missing canonical source files", missing=missing)
        return report
    # Include all canonical scripts and templates, not just the minimum list.
    files = [source / "gpt-project.yaml"]
    for folder in ("scripts", "templates"):
        directory = source / folder
        if not directory.is_dir():
            stage("source", False, f"Missing directory: {folder}")
            return report
        files.extend(p for p in directory.rglob("*") if p.is_file()
                     and "__pycache__" not in p.parts and p.suffix != ".pyc")
    files = sorted(set(files))
    if not stage("source", True, f"{len(files)} source files discovered"):
        return report

    with tempfile.TemporaryDirectory(prefix="gpt-engine-selftest-") as tmp:
        workspace = Path(tmp)
        materialized = workspace / "engine"
        try:
            for path in files:
                target = materialized / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
            stage("materialize", True, f"{len(files)} files copied to isolated workspace")
        except (OSError, PermissionError) as exc:
            stage("materialize", False, f"{type(exc).__name__}: {exc}")
            return report

        try:
            mismatches = [
                str(path.relative_to(source)) for path in files
                if sha256(path) != sha256(materialized / path.relative_to(source))
            ]
            if mismatches:
                stage("integrity", False, "SHA-256 mismatch", mismatches=mismatches)
                return report
            stage("integrity", True, f"SHA-256 verified for {len(files)} files")
        except OSError as exc:
            stage("integrity", False, f"{type(exc).__name__}: {exc}")
            return report

        project = workspace / "smoke"
        project.mkdir()
        try:
            import yaml
            cfg = yaml.safe_load((materialized / "gpt-project.yaml").read_text(encoding="utf-8"))
            cfg["project"]["id"] = "engine-selftest"
            cfg["project"]["name"] = "Engine Selftest"
            # Synthetic assistants use the supported legacy single-instruction format.
            cfg["instructions"].pop("mode", None)
            cfg["instructions"].pop("core", None)
            cfg["instructions"].pop("assembly", None)
            cfg.pop("reference_profiles", None)
            # A synthetic smoke GPT must not inherit Builder-only lint/test declarations.
            cfg.pop("testing", None)
            cfg.pop("linting", None)
            cfg.get("model_robustness", {}).pop("model_compatibility", None)
            cfg["tools"]["tools"] = []
            cfg["skills"]["definitions"] = []
            cfg["runtime"]["opencode"]["skills"]["definitions"] = []
            (project / "gpt-project.yaml").write_text(
                yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8"
            )
            instruction = project / cfg["instructions"]["canonical"]
            instruction.parent.mkdir(parents=True, exist_ok=True)
            instruction.write_text("You are a smoke-test assistant.\n", encoding="utf-8")
            for relative in (cfg.get("structure", {}).get("runtime_policy", {}).get("path"),):
                if relative:
                    (project / relative).mkdir(parents=True, exist_ok=True)
        except (KeyError, ValueError, OSError, ImportError, TypeError) as exc:
            stage("installer", False, f"Unable to create schema-compatible smoke project: {exc}")
            return report

        install_cmd = [
            sys.executable, str(materialized / "scripts/install_distribution_engine.py"),
            "--source", str(materialized), "--project-root", str(project),
        ]
        try:
            installed = subprocess.run(install_cmd, capture_output=True, text=True, timeout=90)
        except (OSError, subprocess.TimeoutExpired) as exc:
            stage("installer", False, f"{type(exc).__name__}: {exc}")
            return report
        if installed.returncode:
            stage("installer", False, (installed.stderr or installed.stdout)[-2400:],
                  exit_code=installed.returncode)
            return report
        stage("installer", True, "Canonical installer completed", output=installed.stdout[-1200:])

        build_cmd = [
            sys.executable, str(project / "scripts/build_distributions.py"),
            "--project-root", str(project), "--version", "0.0.0-selftest",
            "--targets", "project,chat,plugin,claude_project,claude_skills,opencode",
        ]
        try:
            built = subprocess.run(build_cmd, capture_output=True, text=True, timeout=150)
        except (OSError, subprocess.TimeoutExpired) as exc:
            stage("build", False, f"{type(exc).__name__}: {exc}")
            return report
        archives = sorted((project / "dist").glob("*.zip"))
        if built.returncode or len(archives) != 6:
            stage("build", False,
                  (built.stderr or built.stdout)[-2400:] or
                  f"Expected six archives, got {len(archives)}",
                  exit_code=built.returncode, archive_count=len(archives))
            return report
        stage("build", True, "Canonical project and five peer distributions built",
              archive_count=len(archives))
        report["ok"] = True
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    report = diagnose(args.source)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    print(payload)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
