"""Evidence-based Engine and Plugin recovery assessment for legacy GPT projects.

Do not manufacture selftests or claim runtime parity from package structure.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

SOURCE_EXCLUSIONS = {"dist", "build", ".git", "__pycache__", "reconstructed-canonical"}
BUILD_SCRIPTS = {"build_distributions.py", "install_distribution_engine.py", "validate_distributions.py", "lint_gpt_project.py", "migrate_legacy_copy.py", "migrate_legacy_project.py"}


def inspect_engine_migration(root: Path, cfg: dict | None) -> dict[str, Any]:
    if not isinstance(cfg, dict):
        return {"engine_required": "undetermined", "engine_status": "blocked",
                "plugin_repair_status": "source_contract_missing",
                "runtime_parity_status": "unverified", "release_ready": False,
                "required_actions": ["Recover and review canonical project contract before enabling Plugin or Engine."]}
    runtime = cfg.get("runtime") or {}
    plugin = runtime.get("plugin") or runtime.get("openai_plugin") or {}
    plugin_present = isinstance(plugin, dict) and bool(plugin)
    declared = cfg.get("engine") or {}
    candidates = []
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root)
        if set(rel.parts) & SOURCE_EXCLUSIONS or p.name in BUILD_SCRIPTS:
            continue
        candidates.append(rel.as_posix())
    explicit = declared.get("enabled") is True
    resources = declared.get("resources") or []
    selftest = declared.get("selftest")
    configured = explicit and isinstance(resources, list) and bool(resources) and isinstance(selftest, str) and bool(selftest)
    verified_paths = configured and (root / selftest).is_file() and all(
        isinstance(v, str) and (root / v).exists() and not Path(v).is_absolute()
        and ".." not in Path(v).parts for v in resources
    )
    if explicit and verified_paths:
        engine_status = "configured_pending_integrity_and_execution"
    elif explicit:
        engine_status = "incomplete_configuration"
    elif candidates:
        engine_status = "review_required"
    else:
        engine_status = "not_indicated"
    if not plugin_present:
        plugin_status = "plugin_not_configured"
    elif "openai_plugin" in runtime and "plugin" not in runtime:
        plugin_status = "legacy_plugin_requires_mapping"
    else:
        plugin_status = "needs_rebuild_and_host_verification"
    actions = []
    if candidates and not verified_paths:
        actions.append("Classify candidate Python scripts as Plugin runtime requirements, tests, or build-only tools.")
        actions.append("If executable Plugin scripts are required, declare engine.resources and a real engine.selftest.")
    if explicit and not verified_paths:
        actions.append("Correct engine resources/selftest paths; do not ship an unverified Engine ZIP.")
    if plugin_present:
        actions.append("Rebuild Plugin using the current canonical distribution builder; inspect Skills and resources.")
        actions.append("Validate all five distributions and test the Plugin in its actual host.")
    actions.append("Install/verify the current canonical builder only after reviewing the copied project schema and preserving project-specific files.")
    return {
        "engine_required": True if explicit else ("needs_review" if candidates else False),
        "engine_status": engine_status,
        "engine_candidates": candidates,
        "engine_configuration_present": explicit,
        "engine_selftest_verified": False,
        "plugin_repair_status": plugin_status,
        "runtime_parity_status": "unverified",
        "automatic_plugin_repair": False,
        "automatic_engine_activation": False,
        "release_ready": False,
        "required_actions": actions,
    }
