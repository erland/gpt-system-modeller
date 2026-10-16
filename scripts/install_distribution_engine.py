#!/usr/bin/env python3
"""Install the canonical runtime distribution engine in a generated GPT project.

Does not rewrite project configuration or invent runtime-specific settings.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ENGINE_FILES = (
    "scripts/build_distributions.py",
    "scripts/lib/project_model.py",
    "scripts/lib/canonical_skill_sources.py",
    "scripts/lib/engine_package.py",
    "scripts/lib/project_resource_audit.py",
    "scripts/validate_distributions.py",
    "scripts/validate_portable_skills.py",
)
REQUIRED_BUILDERS = {"chat": "chat", "plugin": "plugin", "claude_project": "claude", "claude_skills": "claude_skills", "opencode": "opencode"}
REQUIRED_TARGETS = set(REQUIRED_BUILDERS)


def install(source: Path, project: Path) -> list[str]:
    if source.resolve() == project.resolve():
        raise ValueError("Source and destination must be different")
    if not (project / "gpt-project.yaml").is_file():
        raise ValueError("Destination requires an existing gpt-project.yaml")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required") from exc
    cfg = yaml.safe_load((project / "gpt-project.yaml").read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError("Project configuration must be a YAML mapping")
    build_system = cfg.get("build_system")
    if not isinstance(build_system, dict):
        raise ValueError("build_system must be a YAML mapping")
    targets = build_system.get("runtime_targets")
    if not isinstance(targets, dict):
        raise ValueError(
            "build_system.runtime_targets must be a mapping, not a list; "
            "generate complete target objects from the canonical project contract"
        )
    missing = REQUIRED_TARGETS - set(targets)
    if missing:
        raise ValueError("Missing platform-specific runtime targets: " + ", ".join(sorted(missing)))
    required_fields = ("builder", "runtime_key", "runtime_id", "artifact_type", "filename_pattern")
    for target, expected in REQUIRED_BUILDERS.items():
        item = targets[target]
        if not isinstance(item, dict):
            raise ValueError(f"runtime_targets.{target} must be a mapping")
        if item.get("builder") != expected:
            raise ValueError(f"Incorrect builder for {target}: expected {expected}")
        missing_fields = [field for field in required_fields if not item.get(field)]
        if missing_fields:
            raise ValueError(f"runtime_targets.{target} missing: {', '.join(missing_fields)}")
    configured = build_system.get("targets")
    if not isinstance(configured, list) or set(configured) != REQUIRED_TARGETS | {"project"}:
        raise ValueError("New projects must select project plus all five canonical runtime targets")
    runtime = cfg.get("runtime")
    required_runtime = ("chat_zip", "plugin", "claude", "opencode", "custom_gpt")
    if not isinstance(runtime, dict):
        raise ValueError("Missing runtime configuration mapping")
    for key in required_runtime:
        if not isinstance(runtime.get(key), dict):
            raise ValueError(f"Missing runtime.{key} configuration mapping")
    if runtime.get("custom_gpt", {}).get("enabled") is not False:
        raise ValueError("Custom GPT is retired and must be disabled")
    # A generated project must not inherit Builder-only profile paths unless
    # its own reference profile definitions are present.
    profiles = cfg.get("reference_profiles")
    if (project / "project-status.yaml").is_file() and isinstance(profiles, dict) and profiles.get("root"):
        profile_root = Path(str(profiles["root"]))
        if profile_root.is_absolute() or ".." in profile_root.parts:
            raise ValueError("Unsafe reference_profiles.root")
        declared = profiles.get("profiles", [])
        if not isinstance(declared, list) or any(
            not isinstance(name, str) or not name or "/" in name or ".." in name
            for name in declared
        ):
            raise ValueError("Invalid reference_profiles.profiles")
        absent = [
            name for name in declared
            if not any((project / profile_root / (name + ext)).is_file()
                       for ext in (".yaml", ".yml", ".json"))
        ]
        if absent:
            raise ValueError(
                "Missing reference profile definitions: " + ", ".join(absent)
                + ". Remove Builder-only reference_profiles from the new "
                  "gpt-project.yaml, or provide the project's own profile files."
            )
    declared_scripts = []
    for tool in cfg.get("tools", {}).get("tools", []):
        if tool.get("type") == "script" and tool.get("script"):
            declared_scripts.append(tool["script"])
    files_to_install = tuple(dict.fromkeys((*ENGINE_FILES, *declared_scripts)))
    template = cfg.get("runtime", {}).get("chat_zip", {}).get("start_here_template")
    declared_templates = [template] if template else []
    for runtime in ("plugin", "claude", "opencode"):
        templates = cfg.get("runtime", {}).get(runtime, {}).get("templates", {})
        if isinstance(templates, dict):
            declared_templates.extend(value for value in templates.values() if isinstance(value, str))
    files_to_install = tuple(dict.fromkeys((*files_to_install, *declared_templates)))
    for relative in files_to_install:
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError("Unsafe declared script path: " + relative)
        if not (source / relative).is_file() and not (project / relative).is_file():
            raise FileNotFoundError(source / relative)
    copied = []
    for target, expected in REQUIRED_BUILDERS.items():
        if targets[target].get("builder") != expected:
            raise ValueError(f"Incorrect builder for {target}: expected {expected}")
    for relative in files_to_install:
        if not (source / relative).is_file():
            continue
        destination = project / relative
        if relative not in ENGINE_FILES and destination.is_file():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
        copied.append(relative)
    ignore_template = source / "templates/generated-project.gitignore"
    ignore_target = project / ".gitignore"
    if not ignore_target.exists() and ignore_template.is_file():
        shutil.copy2(ignore_template, ignore_target)
        copied.append(".gitignore")
    return copied


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    for name in install(args.source, args.project_root):
        print("Installed", name)


if __name__ == "__main__":
    main()
