#!/usr/bin/env python3
"""Safely migrate a legacy project into a separate destination.

Accepts a project directory or ZIP. Never changes the input. Missing canonical
project files produce a review report rather than invented project metadata.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import zipfile

import yaml
from pathlib import Path

from migrate_legacy_project import apply_changes, build_report, load_cfg
from discover_legacy_project import discover

SKIP = {".git", "build", "dist", "__pycache__", ".pytest_cache"}


def _assert_separate(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Destination must be separate from the source tree")
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")


def _safe_unpack(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        entries = zf.infolist()
        if len(entries) > 5000:
            raise ValueError("Archive has too many entries")
        for entry in entries:
            name = entry.filename.replace("\\", "/")
            parts = Path(name).parts
            if not parts or name.startswith("/") or ".." in parts or ":" in parts[0]:
                raise ValueError(f"Unsafe archive entry: {name}")
            # Reject symbolic links.
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(f"Archive contains symlink: {name}")
            if entry.file_size > 100 * 1024 * 1024:
                raise ValueError(f"Archive member too large: {name}")
            target = destination.joinpath(*parts)
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError(f"Unsafe archive destination: {name}")
        for entry in entries:
            name = entry.filename.replace("\\", "/")
            parts = Path(name).parts
            if any(p in SKIP for p in parts):
                continue
            target = destination.joinpath(*parts)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(entry) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)


def _project_root(dest: Path) -> Path:
    if (dest / "gpt-project.yaml").exists():
        return dest
    candidates = list(dest.rglob("gpt-project.yaml"))
    if len(candidates) == 1:
        return candidates[0].parent
    return dest


def retire_custom_gpt(project: Path) -> dict:
    """Retire only active Builder targets; preserve legacy configuration."""
    path = project / "gpt-project.yaml"
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        return {"result": "blocked", "reason": "Invalid project contract"}
    original = copy.deepcopy(cfg)
    runtime = cfg.get("runtime")
    previous_enabled = False
    if isinstance(runtime, dict) and isinstance(runtime.get("custom_gpt"), dict):
        previous_enabled = runtime["custom_gpt"].get("enabled") is True
        runtime["custom_gpt"]["enabled"] = False
    build = cfg.get("build")
    if isinstance(build, dict) and build.get("build_custom_gpt_zip") is True:
        build["build_custom_gpt_zip"] = False
    build_system = cfg.get("build_system")
    if isinstance(build_system, dict):
        if isinstance(build_system.get("targets"), list):
            build_system["targets"] = [t for t in build_system["targets"] if t != "custom-gpt"]
        if isinstance(build_system.get("runtime_targets"), dict):
            build_system["runtime_targets"].pop("custom-gpt", None)
    parity = cfg.get("runtime_parity")
    if isinstance(parity, dict) and isinstance(parity.get("registered_runtimes"), list):
        parity["registered_runtimes"] = [r for r in parity["registered_runtimes"] if r != "chatgpt_custom"]
    for section, key in (("direct_build", "deliver"), ("release", "artifacts")):
        obj = cfg.get(section)
        if section == "release" and isinstance(obj, dict):
            obj = obj.get("github")
        if isinstance(obj, dict) and isinstance(obj.get(key), list):
            obj[key] = [t for t in obj[key] if t != "custom_gpt_zip_when_enabled"]
    if cfg != original:
        path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {
        "result": "changed" if cfg != original else "no_changes",
        "previously_enabled": previous_enabled,
        "legacy_configuration_preserved": True,
        "automatic_plugin_conversion": False,
    }


def inventory_distribution(project: Path) -> dict:
    """Identify known packaging layouts without inferring missing canonical contracts."""
    paths = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file()}
    layouts = {
        "chat_zip": ("START-HERE.md", "assistant/instructions.md"),
        "openai_plugin": ("plugin.json",),
        "custom_gpt": ("builder/instructions.md",),
        "claude_project": ("project/instructions.md",),
        "opencode": ("AGENTS.md",),
    }
    matches = []
    for kind, signatures in layouts.items():
        if all(sig in paths for sig in signatures):
            matches.append(kind)
    # A packaged plugin with a top-level directory is handled by _project_root
    # only when there is a project contract; otherwise report its location.
    if not matches:
        for kind, signatures in layouts.items():
            if any(all(f"{prefix}/{sig}" in paths for sig in signatures)
                   for prefix in {p.split("/")[0] for p in paths if "/" in p}):
                matches.append(kind)
    markers = (
        "assistant/instructions.md", "builder/instructions.md",
        "project/instructions.md", "AGENTS.md", "plugin.json",
        "START-HERE.md",
    )
    discovered = sorted(p for p in paths if p in markers or p.endswith("/SKILL.md"))
    knowledge = sorted(p for p in paths if p.startswith("knowledge/") or "/knowledge/" in p
                       or "/references/" in p or "/knowledge-package/" in p)
    return {
        "detected_formats": sorted(set(matches)),
        "classification": matches[0] if len(matches) == 1 else
            ("ambiguous" if matches else "unknown"),
        "evidence": discovered,
        "knowledge_file_count": len(knowledge),
        "reconstruction": "review_required",
        "missing": ["canonical project contract", "authoritative project status"],
    }



def inventory_recovered_dependencies(project: Path) -> dict:
    """Evidence-only inventory: files and candidate tools are never promoted to contracts."""
    knowledge_parts = {"knowledge", "references", "assets", "knowledge-package"}
    script_parts = {"scripts", "tools"}
    knowledge = []
    scripts = []
    manifests = []
    for file in sorted(p for p in project.rglob("*") if p.is_file()):
        rel = file.relative_to(project)
        if any(part in SKIP for part in rel.parts):
            continue
        if "reconstructed-canonical" in rel.parts or rel.name == "MIGRATION-REPORT.json":
            continue
        name = rel.as_posix()
        if any(part in knowledge_parts for part in rel.parts[:-1]):
            knowledge.append(name)
        if any(part in script_parts for part in rel.parts[:-1]) and file.suffix.lower() in {".py", ".js", ".ts", ".sh"}:
            scripts.append(name)
        if rel.name in {"plugin.json", "mcp.json", "runtime-contract.json", "openapi.json"}:
            manifests.append(name)
    return {
        "knowledge_files": knowledge,
        "candidate_scripts": scripts,
        "integration_manifests": manifests,
        "tools_verified": False,
        "knowledge_completeness_verified": False,
        "review_required": bool(scripts or manifests),
        "limitations": [
            "Packaged files do not prove tool availability or permissions.",
            "A distribution may omit original Knowledge and source dependencies.",
        ],
    }


def reconstruct_review_project(project: Path, inventory: dict) -> dict:
    """Recover explicit instruction text, not a guessed canonical project contract."""
    source_by_format = {
        "chat_zip": "assistant/instructions.md",
        "custom_gpt": "builder/instructions.md",
        "claude_project": "project/instructions.md",
        "opencode": "AGENTS.md",
    }
    kind = inventory["classification"]
    if kind not in source_by_format:
        return {"result": "review_required", "reason": "No single supported instruction source"}
    relative = source_by_format[kind]
    choices = [project / relative] + [
        child / relative for child in project.iterdir() if child.is_dir()
    ]
    found = [p for p in choices if p.is_file()]
    if len(found) != 1:
        return {"result": "review_required", "reason": "Instruction source missing or ambiguous"}
    original = found[0].read_bytes()
    if not original.strip():
        return {"result": "review_required", "reason": "Instruction source is empty"}
    output = project / "reconstructed-canonical"
    output.mkdir(exist_ok=True)
    copied = output / "instructions.md"
    copied.write_bytes(original)
    recovery = {
        "status": "review_required",
        "provenance": found[0].relative_to(project).as_posix(),
        "recovered_instruction": copied.relative_to(project).as_posix(),
        "canonical_contract_created": False,
        "release_ready": False,
        "limitations": [
            "Instructions may be platform-adapted or truncated.",
            "Knowledge and tool dependencies have not been proven complete.",
            "Canonical contract and project status require human review.",
        ],
    }
    (output / "RECOVERY.json").write_text(
        json.dumps(recovery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return recovery


def write_review_project_draft(project: Path, recovery: dict, dependencies: dict) -> dict:
    """Create a non-executable draft manifest, never a release-ready project."""
    if recovery.get("status") != "review_required" or not recovery.get("recovered_instruction"):
        return {"result": "not_created", "reason": "No unambiguous recovered instruction"}
    output = project / "reconstructed-canonical"
    draft = {
        "schema_version": 1,
        "status": "review_required",
        "source_instruction": recovery["provenance"],
        "instruction": recovery["recovered_instruction"],
        "knowledge_candidates": dependencies["knowledge_files"],
        "tool_candidates": dependencies["candidate_scripts"],
        "integration_candidates": dependencies["integration_manifests"],
        "verified": {
            "instruction_bytes_copied": True,
            "knowledge_complete": False,
            "tools_executable": False,
            "runtime_parity": False,
        },
        "runtime_activation": {
            "chat_zip": False,
            "claude": False,
            "opencode": False,
            "plugin": False,
            "custom_gpt": False,
        },
        "release_ready": False,
        "required_reviews": [
            "Verify original instruction semantics and completeness",
            "Review available Knowledge and missing dependencies",
            "Classify tool candidates and host capabilities",
            "Create canonical project contract after review",
        ],
    }
    target = output / "project-draft.json"
    target.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": "created_for_review", "file": target.relative_to(project).as_posix(), "release_ready": False}


def assess_existing_project(project: Path) -> dict:
    """Report compatibility gaps without altering or inventing runtime configuration."""
    cfg = load_cfg(project)
    runtime = (cfg or {}).get("runtime") or {}
    build_system = (cfg or {}).get("build_system") or {}
    issues = []
    if "openai_plugin" in runtime and "plugin" not in runtime:
        issues.append("Legacy runtime.openai_plugin needs explicit mapping to runtime.plugin")
    if not build_system.get("runtime_targets"):
        issues.append("No modern build_system.runtime_targets are declared")
    if any((runtime.get(k) or {}).get("enabled") for k in ("chat_zip", "claude", "opencode", "plugin")):
        issues.append("Previously enabled runtimes require independent parity review")
    if not (project / "src" / "instructions" / "system.md").is_file():
        issues.append("Canonical instructions missing from expected modern source path")
    return {
        "status": "review_required" if issues else "existing_contract_present",
        "project_contract_present": True,
        "issues": issues,
        "dependency_inventory": inventory_recovered_dependencies(project),
        "ready_for_modern_distribution_build": False,
        "release_ready": False,
    }


def create_legacy_plugin_migration_plan(project: Path) -> dict:
    """Make an auditable mapping proposal; never silently enable a new runtime."""
    cfg = load_cfg(project)
    legacy = ((cfg or {}).get("runtime") or {}).get("openai_plugin")
    if not isinstance(legacy, dict):
        return {"result": "not_applicable"}
    runtime = cfg.get("runtime") or {}
    entrypoint = legacy.get("entrypoint")
    entry_is_safe = (
        isinstance(entrypoint, str) and bool(entrypoint.strip())
        and not Path(entrypoint).is_absolute() and ".." not in Path(entrypoint).parts
    )
    dependencies = {
        key: legacy.get(key) for key in (
            "web_dependency", "filesystem_read", "filesystem_write",
            "code_execution", "persistent_state"
        ) if key in legacy
    }
    proposal = {
        "result": "review_required",
        "source_runtime": "runtime.openai_plugin",
        "target_runtime": "runtime.plugin",
        "proposed_config": {
            "enabled": False,
            "role": "peer_distribution",
            "mode": "openai_plugin",
            "layout": {"manifest_file": "plugin.json", "skills": "skills"},
            "validation": {
                "require_manifest": True,
                "require_skill": True,
                "require_skill_frontmatter": True,
            },
        },
        "source_entrypoint": entrypoint,
        "source_entrypoint_exists": bool(entry_is_safe and (project / entrypoint).is_file()),
        "source_entrypoint_missing": not bool(entry_is_safe and (project / entrypoint).is_file()),
        "recovery_sources": [
            ref for ref in (
                ((cfg.get("instructions") or {}).get("canonical")),
                "src/instructions/system.md",
                "knowledge/KNOWLEDGE.md",
            )
            if isinstance(ref, str) and ref.strip()
            and not Path(ref).is_absolute() and ".." not in Path(ref).parts
            and (project / ref).is_file()
        ],
        "skill_reconstruction_required": not bool(entry_is_safe and (project / entrypoint).is_file()),

        "host_capability_dependencies": dependencies,
        "requires_review": [
            "Recover missing declared SKILL.md from verified canonical instructions when absent",
            "Ensure canonical skills map to the original plugin behavior",
            "Verify optional host tools and capability fallbacks",
            "Verify Knowledge/resources, plugin template and manifest compatibility",
            "Run actual Plugin ZIP build, validation and mobile import",
        ],
        "legacy_config_preserved": True,
        "runtime_activated": False,
        "release_ready": False,
    }
    if isinstance(runtime.get("plugin"), dict):
        proposal["result"] = "existing_modern_plugin_requires_review"
    target = project / "reconstructed-canonical" / "plugin-migration-plan.json"
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        raise FileExistsError(f"Refusing overwrite of {target}")
    target.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"result": proposal["result"], "plan": target.relative_to(project).as_posix()}


def _plugin_repair_preflight(project: Path) -> dict:
    """Only repair unambiguous modern Plugin projects; never infer legacy behavior."""
    cfg = load_cfg(project)
    if not isinstance(cfg, dict):
        return {"status": "blocked", "reason": "Missing canonical project profile"}
    runtime = cfg.get("runtime") or {}
    if "openai_plugin" in runtime and "plugin" not in runtime:
        return {"status": "review_required", "reason": "Legacy Plugin runtime mapping requires review"}
    plugin = runtime.get("plugin") or {}
    if not isinstance(plugin, dict) or not plugin.get("enabled"):
        return {"status": "not_applicable", "reason": "Modern Plugin not enabled"}
    ref = (cfg.get("instructions") or {}).get("canonical")
    if not isinstance(ref, str) or not ref or Path(ref).is_absolute() or ".." in Path(ref).parts:
        return {"status": "blocked", "reason": "No safe canonical instruction path"}
    source = project / ref
    if not source.is_file() or not source.read_text(encoding="utf-8").strip():
        return {"status": "blocked", "reason": "Missing canonical instruction source"}
    skills = cfg.get("skills") or {}
    if isinstance(skills.get("definitions"), list) and skills["definitions"]:
        return {"status": "already_declared", "skill_count": len(skills["definitions"])}
    project_id = (cfg.get("project") or {}).get("id")
    if not isinstance(project_id, str) or not project_id.strip():
        return {"status": "blocked", "reason": "Missing project identifier"}
    # The canonical Plugin builder already supports an inferred single Skill.
    # Materialize that one *declaration* only when authoritative behavior exists.
    # This never substitutes guessed instructions or activates an old runtime.
    proposed = {
        "id": project_id, "name": project_id,
        "description": (cfg.get("project") or {}).get("description") or
                       f"Use {project_id} according to its canonical instructions.",
        "references": [], "assets": [], "scripts": [],
    }
    updated = copy.deepcopy(cfg)
    updated.setdefault("skills", {})["definitions"] = [proposed]
    (project / "gpt-project.yaml").write_text(
        yaml.safe_dump(updated, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    return {"status": "repaired_from_canonical", "skill_count": 1,
            "behavior_source": ref, "host_verified": False}


def _recover_declared_engine(project: Path) -> dict:
    """Activate Engine only with explicit Python runtime tools and real selftest."""
    cfg = load_cfg(project)
    if not isinstance(cfg, dict):
        return {"status": "blocked", "reason": "Missing project profile"}
    existing = cfg.get("engine") or {}
    if existing.get("enabled"):
        return {"status": "already_declared"}
    tools = (cfg.get("tools") or {}).get("tools") or []
    scripts = sorted({
        tool["script"] for tool in tools
        if isinstance(tool, dict) and tool.get("type") == "script"
        and isinstance(tool.get("script"), str) and tool["script"].endswith(".py")
        and tool.get("requirement") == "required"
    })
    if not scripts:
        return {"status": "not_required_or_not_proven"}
    for name in scripts:
        p = Path(name)
        if p.is_absolute() or ".." in p.parts or not (project / p).is_file():
            return {"status": "review_required", "reason": "Invalid or missing required script", "script": name}
    test = "scripts/selftest.py"
    if not (project / test).is_file():
        return {"status": "review_required", "reason": "Required Python scripts found, but no real scripts/selftest.py"}
    updated = copy.deepcopy(cfg)
    updated["engine"] = {
        "enabled": True, "resources": sorted({*scripts, test}),
        "selftest": test, "required_files": scripts, "python_dependencies": [],
    }
    (project / "gpt-project.yaml").write_text(
        yaml.safe_dump(updated, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    return {"status": "configured_pending_execution",
            "resources": updated["engine"]["resources"], "selftest": test,
            "executed": False}


def _verify_migration_archives(project: Path, version: str) -> dict:
    """Compare actual deliverables against declared targets and inspect Plugin."""
    from verify_distribution_outputs import expected_files
    cfg = load_cfg(project)
    dist = project / "dist"
    expected = expected_files(cfg, version)
    missing = sorted(name for name in expected if not (dist / name).is_file())
    if missing:
        return {"status": "blocked", "missing_artifacts": missing}
    plugin_cfg = (cfg.get("runtime") or {}).get("plugin") or {}
    if not plugin_cfg.get("enabled"):
        return {"status": "verified_build_only", "plugin": "disabled"}
    target = ((cfg.get("build_system") or {}).get("runtime_targets") or {}).get("plugin") or {}
    pattern = target.get("filename_pattern")
    if not isinstance(pattern, str):
        return {"status": "blocked", "reason": "Missing Plugin filename pattern"}
    filename = pattern.replace("<project-id>", cfg["project"]["id"]).replace("<version>", version)
    with zipfile.ZipFile(dist / filename) as archive:
        names = archive.namelist()
        skills = sorted(name for name in names if name.startswith("skills/") and name.endswith("/SKILL.md"))
        has_manifest = "plugin.json" in names
    if not has_manifest or not skills:
        return {"status": "blocked", "reason": "Plugin archive missing manifest or Skills"}
    engine = cfg.get("engine") or {}
    engine_filename = f"{cfg['project']['id']}-engine-{version}.zip"
    if engine.get("enabled") and not (dist / engine_filename).is_file():
        return {"status": "blocked", "reason": "Declared Engine archive is missing"}
    return {"status": "verified_build_only", "plugin": "structurally_verified",
            "plugin_skills": skills, "engine_archive": engine_filename if engine.get("enabled") else None}


def upgrade_canonical_build(project: Path, version: str) -> dict:
    """Opt-in canonical upgrade; source untouched and release never auto-approved."""
    # Do not mutate a legacy Plugin profile whose semantics are unresolved.
    cfg = load_cfg(project)
    if isinstance(cfg, dict):
        runtime = cfg.get("runtime") or {}
        if "openai_plugin" in runtime and "plugin" not in runtime:
            return {"status": "blocked", "stage": "plugin_mapping_review",
                    "reason": "Review legacy Plugin semantics before enabling modern Plugin",
                    "release_ready": False}
    source_engine = Path(__file__).resolve().parents[1]
    installer = source_engine / "scripts/install_distribution_engine.py"
    install = subprocess.run(
        [sys.executable, str(installer), "--source", str(source_engine),
         "--project-root", str(project)], capture_output=True, text=True,
    )
    if install.returncode:
        return {"status": "blocked", "stage": "canonical_engine_install",
                "detail": (install.stderr or install.stdout).strip()[-2000:],
                "runtime_parity_status": "unverified", "release_ready": False}
    engine_recovery = _recover_declared_engine(project)
    repair = _plugin_repair_preflight(project)
    if repair["status"] == "blocked":
        return {"status": "blocked", "stage": "plugin_repair",
                "plugin_repair": repair, "engine_recovery": engine_recovery, "release_ready": False}
    build = subprocess.run(
        [sys.executable, str(project / "scripts/build_distributions.py"),
         "--project-root", str(project), "--version", version],
        capture_output=True, text=True,
    )
    if build.returncode:
        return {"status": "blocked", "stage": "canonical_distribution_build",
                "detail": (build.stderr or build.stdout).strip()[-2000:],
                "plugin_repair": repair, "engine_recovery": engine_recovery,
                "runtime_parity_status": "unverified", "release_ready": False}
    archives = sorted(p.name for p in (project / "dist").glob("*.zip"))
    verified = _verify_migration_archives(project, version)
    if verified["status"] == "blocked":
        return {"status": "blocked", "stage": "artifact_verification",
                "artifacts": verified, "plugin_repair": repair, "engine_recovery": engine_recovery,
                "runtime_parity_status": "unverified", "release_ready": False}
    return {"status": "built_pending_host_acceptance", "stage": "canonical_distribution_build",
            "archives": archives, "artifacts": verified, "plugin_repair": repair,
            "engine_recovery": engine_recovery,
            "runtime_parity_status": "structural_build_only", "release_ready": False}


def migrate(source: Path, destination: Path, upgrade_build: bool = False, version: str = "0.0.0-migration", activate_modular_skills: bool = False) -> dict:
    source, destination = source.resolve(), destination.resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    if source.is_dir():
        _assert_separate(source, destination)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*SKIP))
    elif source.is_file() and zipfile.is_zipfile(source):
        if destination.exists():
            raise FileExistsError(destination)
        destination.mkdir(parents=True)
        try:
            _safe_unpack(source, destination)
        except Exception:
            shutil.rmtree(destination)
            raise
    else:
        raise ValueError("Source must be a directory or ZIP archive")

    project = _project_root(destination)
    cfg = load_cfg(project)
    report = build_report(project, cfg)
    report["safe_copy"] = {
        "source_type": "zip" if source.is_file() else "directory",
        "source_unchanged": True,
        "project_root": project.relative_to(destination).as_posix(),
        "destination": str(destination),
    }
    if cfg is None:
        report["distribution_inventory"] = inventory_distribution(project)
        report["dependency_inventory"] = inventory_recovered_dependencies(project)
        report["reconstruction"] = reconstruct_review_project(project, report["distribution_inventory"])
        report["project_draft"] = write_review_project_draft(project, report["reconstruction"], report["dependency_inventory"])
        report["apply"] = {"result": "blocked", "reason": "No gpt-project.yaml; reconstruction requires review"}
    else:
        changed = apply_changes(project, cfg, report)
        retired = retire_custom_gpt(project)
        report["custom_gpt_retirement"] = retired
        report["existing_project_assessment"] = assess_existing_project(project)
        report["legacy_plugin_plan"] = create_legacy_plugin_migration_plan(project)
        report["apply"] = {"result": "changed" if changed or retired["result"] == "changed" else "no_changes"}
    if activate_modular_skills:
        from lib.activate_modular_skills import activate
        report["modular_skill_activation"] = activate(project)
    from lib.legacy_engine_assessment import inspect_engine_migration
    report["engine_migration"] = inspect_engine_migration(project, load_cfg(project))
    if upgrade_build:
        if activate_modular_skills and report.get("modular_skill_activation", {}).get("status") not in ("already_enabled", "activated_pending_behavior_review"):
            report["canonical_build_upgrade"] = {"status": "blocked", "reason": "Modular Skill activation did not complete", "release_ready": False}
        else:
            report["canonical_build_upgrade"] = (
                upgrade_canonical_build(project, version) if load_cfg(project) is not None
                else {"status": "blocked", "reason": "Missing reviewed project profile", "release_ready": False}
            )
    if activate_modular_skills:
        from lib.verify_modular_migration import inspect
        current = load_cfg(project)
        if isinstance(current, dict):
            build = report.get("canonical_build_upgrade") or {}
            report["modular_distribution_verification"] = inspect(
                project, current, version if build.get("status") == "built_pending_host_acceptance" else None
            )
        else:
            report["modular_distribution_verification"] = {"status": "blocked", "reason": "Missing project profile", "release_ready": False}
        report["modular_release_ready"] = False
    from lib.migration_hygiene import assess_hygiene, migration_steps
    report["generic_discovery"] = discover(project)
    report["project_hygiene"] = assess_hygiene(project, engine_version=version if upgrade_build else None)
    report["migration_steps"] = migration_steps(report)
    report["next_step"] = next(
        ({"id": step["id"], "title": step["title"]}
         for step in report["migration_steps"] if step["status"] not in {"completed", "checked"}),
        {"id": "review", "title": "Granska migrationsrapport och releaseberedskap"},
    )
    (destination / "MIGRATION-REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate a legacy GPT project without modifying the source")
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--activate-modular-skills", action="store_true", help="Activate reviewed modular source ownership (requires canonical/assembly.json)")
    parser.add_argument("--upgrade-build", action="store_true", help="Opt-in canonical engine install and five-runtime build in migration copy")
    parser.add_argument("--version", default="0.0.0-migration")
    args = parser.parse_args()
    try:
        report = migrate(Path(args.source), Path(args.destination), upgrade_build=args.upgrade_build, version=args.version, activate_modular_skills=args.activate_modular_skills)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
