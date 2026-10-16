#!/usr/bin/env python3
"""Fail fast when a generated GPT project violates its source/delivery contract."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile
import json
import hashlib

TARGETS = ("chat", "plugin", "claude_project", "claude_skills", "opencode")
FORBIDDEN = {".git", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache"}
ENGINE = ("scripts/build_distributions.py", "scripts/lib/project_model.py",
          "scripts/validate_distributions.py", "scripts/validate_portable_skills.py")


def validate(root: Path, project_zip: Path | None = None, dist_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not (root / ".gitignore").is_file():
        errors.append("Missing .gitignore")
    else:
        patterns = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
        for name in ("dist/", "build/"):
            if name not in [line.strip() for line in patterns]:
                errors.append(f".gitignore missing {name}")
    status_file = root / "project-status.yaml"
    if status_file.is_file():
        try:
            import yaml
            status = yaml.safe_load(status_file.read_text(encoding="utf-8"))
            mode = status.get("delivery", {}).get("mode") if isinstance(status, dict) and isinstance(status.get("delivery"), dict) else None
            if isinstance(status, dict) and ("delivery" in status or "delivery_mode" in status) and mode not in ("zip", "github"):
                errors.append("Project status requires delivery.mode: zip or github")
            if isinstance(status, dict) and "delivery_mode" in status:
                errors.append("Legacy delivery_mode field is not allowed; use delivery.mode")
        except (ImportError, ValueError, TypeError, AttributeError) as exc:
            errors.append(f"Cannot inspect project-status.yaml: {exc}")
    cfg_file = root / "gpt-project.yaml"
    if not cfg_file.is_file():
        errors.append("Missing gpt-project.yaml")
    else:
        try:
            import yaml
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))
            # Newly generated modular projects must explicitly own Skill resources.
            # Legacy migration validation stays in the canonical builder's opt-in mode.
            if isinstance(cfg, dict) and (cfg.get("instructions") or {}).get("mode") == "modular_skills":
                skills_cfg = cfg.get("skills") or {}
                if skills_cfg.get("resource_policy") != "explicit":
                    errors.append("Generated modular project requires skills.resource_policy: explicit")
                definitions = skills_cfg.get("definitions") or []
                if not isinstance(definitions, list) or not definitions:
                    errors.append("Generated modular project requires Skill definitions")
                else:
                    for skill in definitions:
                        if not isinstance(skill, dict):
                            errors.append("Invalid generated Skill definition")
                            continue
                        for kind in ("references", "assets", "scripts"):
                            if not isinstance(skill.get(kind), list):
                                errors.append(f"Generated Skill {skill.get('id', '<unknown>')} requires {kind} list (use [] if unused)")
            targets = cfg.get("build_system", {}).get("runtime_targets", {}) if isinstance(cfg, dict) else {}
            if not isinstance(targets, dict) or any(key not in targets for key in TARGETS):
                errors.append("Missing canonical five runtime_targets mapping")
            profiles = cfg.get("reference_profiles")
            if isinstance(profiles, dict) and profiles.get("root"):
                profile_root = Path(str(profiles["root"]))
                if profile_root.is_absolute() or ".." in profile_root.parts:
                    errors.append("Unsafe reference_profiles.root")
                else:
                    listed = profiles.get("profiles", [])
                    if not isinstance(listed, list):
                        errors.append("Invalid reference_profiles.profiles")
                    else:
                        for name in listed:
                            if not isinstance(name, str) or not name or "/" in name or ".." in name:
                                errors.append(f"Invalid reference profile name: {name}")
                            elif not any((root / profile_root / (name + ext)).is_file()
                                         for ext in (".yaml", ".yml", ".json")):
                                errors.append(f"Missing reference profile definition: {name}")
                        if not (root / profile_root).is_dir():
                            errors.append(f"Missing reference_profiles.root: {profile_root}")
            if not isinstance(cfg.get("runtime"), dict):
                errors.append("Missing runtime mapping")
            else:
                if cfg["runtime"].get("custom_gpt", {}).get("enabled") is not False:
                    errors.append("Custom GPT must be disabled")
                enabled_targets = cfg.get("build_system", {}).get("targets", [])
                if not isinstance(enabled_targets, list) or set(enabled_targets) != set(TARGETS) | {"project"}:
                    errors.append("Expected project and all five canonical build targets")
        except (ImportError, ValueError, TypeError, AttributeError) as exc:
            errors.append(f"Cannot inspect gpt-project.yaml: {exc}")
    for relative in ENGINE:
        if not (root / relative).is_file():
            errors.append(f"Missing canonical engine file: {relative}")
    if dist_dir is not None:
        manifest = dist_dir / "DELIVERY-MANIFEST.json"
        if not manifest.is_file():
            errors.append("Missing canonical DELIVERY-MANIFEST.json")
        else:
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                entries = data.get("artifacts", [])
                if not isinstance(entries, list):
                    raise ValueError("artifacts must be a list")
                zip_entries = [item for item in entries if isinstance(item, dict)
                               and item.get("type") not in ("project_zip", "checksums")
                               and str(item.get("file", "")).endswith(".zip")]
                if len(zip_entries) != 5:
                    errors.append(f"Expected five runtime distributions, found {len(zip_entries)}")
                expected_types = {"chat_zip", "plugin_zip", "claude_project_zip", "claude_skills_zip", "opencode_zip"}
                actual_types = [item.get("type") for item in zip_entries]
                if set(actual_types) != expected_types or len(actual_types) != len(set(actual_types)):
                    errors.append("Runtime distribution types must be exactly the canonical five, once each")
                filenames = [item.get("file") for item in zip_entries if isinstance(item.get("file"), str)]
                if len(filenames) != len(set(filenames)):
                    errors.append("Duplicate runtime distribution filenames")
                for item in entries:
                    if not isinstance(item, dict) or item.get("type") == "checksums":
                        continue
                    filename = item.get("file")
                    if not isinstance(filename, str) or Path(filename).name != filename:
                        errors.append(f"Unsafe artifact filename: {filename}")
                        continue
                    artifact = dist_dir / filename
                    if not artifact.is_file():
                        errors.append(f"Missing manifest artifact: {filename}")
                        continue
                    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
                    if item.get("sha256") != digest:
                        errors.append(f"SHA256 mismatch or missing digest: {filename}")
                    if item.get("size") != artifact.stat().st_size:
                        errors.append(f"Size mismatch or missing size: {filename}")
                for item in zip_entries:
                    filename = item.get("file")
                    if not isinstance(filename, str) or Path(filename).name != filename or not (dist_dir / filename).is_file():
                        errors.append(f"Missing or unsafe distribution file: {filename}")
                    else:
                        try:
                            with zipfile.ZipFile(dist_dir / filename) as archive:
                                if ".gitignore" in archive.namelist():
                                    errors.append(f"Unexpected runtime root .gitignore: {filename}")
                                if archive.testzip() is not None:
                                    errors.append(f"Invalid runtime ZIP contents: {filename}")
                        except zipfile.BadZipFile:
                            errors.append(f"Invalid runtime ZIP: {filename}")
                project_entries = [item for item in entries if isinstance(item, dict)
                                   and item.get("type") == "project_zip"]
                if len(project_entries) != 1 or not (dist_dir / str(project_entries[0].get("file", ""))).is_file():
                    errors.append("Missing project ZIP in delivery manifest")
            except (ValueError, TypeError, AttributeError) as exc:
                errors.append(f"Invalid delivery manifest: {exc}")
    if project_zip is not None:
        if not project_zip.is_file():
            errors.append(f"Missing project ZIP: {project_zip}")
        else:
            try:
                with zipfile.ZipFile(project_zip) as archive:
                    for name in archive.namelist():
                        if FORBIDDEN.intersection(Path(name).parts):
                            errors.append(f"Forbidden generated path in project ZIP: {name}")
                            break
                    if archive.testzip() is not None:
                        errors.append("Project ZIP failed integrity check")
            except zipfile.BadZipFile:
                errors.append("Project ZIP is invalid")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--project-zip", type=Path)
    parser.add_argument("--dist-dir", type=Path)
    parser.add_argument("--version")  # reserved for release verification
    args = parser.parse_args()
    errors = validate(args.project_root, args.project_zip, args.dist_dir)
    for error in errors:
        print("ERROR:", error)
    if not errors:
        print("Generated project source and delivery contract: OK")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
