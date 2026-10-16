#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from lib.project_model import (
    normalize_artifact_contract,
    normalize_capability_contract,
    normalize_tool_contract,
    normalize_workspace_state_contract,
)


NEW_CONTRACT_KEYS = ("capabilities", "artifacts", "workspace_state", "tools")
BUILDER_ROOT = Path(__file__).resolve().parents[1]
OPENCODE_ASSETS = (
    "schemas/opencode-runtime.schema.json",
    "src/runtime-policy/opencode-runtime-policy.md",
    "docs/opencode-runtime.md",
    "templates/README.opencode.md.tpl",
)

PLUGIN_ASSETS = (
    "schemas/plugin-runtime.schema.json",
    "schemas/skill-contract.schema.json",
    "src/runtime-policy/plugin-runtime-policy.md",
    "docs/plugin-runtime.md",
    "templates/README.plugin.md.tpl",
)


def load_cfg(root: Path) -> dict[str, Any] | None:
    path = root / "gpt-project.yaml"
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("gpt-project.yaml must contain a mapping")
    return data


def classify_legacy(cfg: dict[str, Any] | None) -> str:
    if cfg is None:
        return "L0"

    modern = 0
    caps = cfg.get("capabilities")
    if isinstance(caps, dict) and isinstance(caps.get("requirements"), dict):
        modern += 1
    if isinstance(cfg.get("artifacts"), dict) and isinstance(cfg["artifacts"].get("outputs"), dict):
        modern += 1
    if isinstance(cfg.get("workspace_state"), dict) and cfg["workspace_state"].get("contract_version") == 1:
        modern += 1
    if isinstance(cfg.get("tools"), dict) and cfg["tools"].get("contract_version") == 1:
        modern += 1

    parity = cfg.get("runtime_parity") or {}
    generic_parity = isinstance(parity.get("registered_runtimes"), list) and isinstance(parity.get("reference"), dict)

    if modern == 4 and generic_parity:
        return "L3"
    if modern > 0:
        return "L2"
    return "L1"


def decision(area: str, action: str, confidence: str, **extra: Any) -> dict[str, Any]:
    result = {
        "area": area,
        "action": action,
        "confidence": confidence,
    }
    result.update(extra)
    return result


def _legacy_unknown_capabilities(cfg: dict[str, Any]) -> list[str]:
    caps = cfg.get("capabilities")
    if not isinstance(caps, dict) or "requirements" in caps:
        return []
    known = {
        "web", "data_analysis", "file_handling", "image_generation",
        "structured_knowledge", "recommendation_mode",
        "ask_user_only_when_business_choice_is_ambiguous",
    }
    return sorted(k for k in caps.keys() if k not in known)


def _domain_artifact_candidates(cfg: dict[str, Any]) -> list[str]:
    artifacts = cfg.get("artifacts")
    if not isinstance(artifacts, dict) or "outputs" in artifacts:
        return []
    known = {
        "project_zip", "chat_zip", "custom_gpt_zip", "claude_zip", "opencode_zip",
        "validation_report", "parity_report", "checksums",
    }
    return sorted(k for k in artifacts.keys() if k not in known)


def _script_candidates(root: Path, cfg: dict[str, Any]) -> list[str]:
    if isinstance(cfg.get("tools"), dict) or (
        isinstance(cfg.get("tooling"), dict) and isinstance(cfg["tooling"].get("tools"), list)
    ):
        return []
    scripts_root = root / "scripts"
    if not scripts_root.exists():
        return []
    return sorted(
        p.relative_to(root).as_posix()
        for p in scripts_root.rglob("*")
        if p.is_file() and p.suffix in {".py", ".js", ".ts", ".sh"}
    )


def assess_opencode(root: Path, cfg: dict[str, Any] | None, changes: dict[str, Any], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    if cfg is None:
        return {
            "status": "blocked",
            "reasons": ["Missing gpt-project.yaml."],
            "can_enable_automatically": False,
            "required_actions": ["Identify canonical project structure before enabling OpenCode."],
        }

    reasons: list[str] = []
    actions: list[str] = []

    instructions = cfg.get("instructions") or {}
    canonical = instructions.get("canonical")
    if not canonical or not (root / canonical).exists():
        reasons.append("Canonical instruction is missing or unresolved.")
        actions.append("Identify a canonical instruction file.")

    workspace = changes.get("workspace_state") or cfg.get("workspace_state") or normalize_workspace_state_contract(cfg)
    state = (workspace or {}).get("state", {})
    authority = state.get("authority")
    requirement = state.get("requirement")
    if requirement == "required" and authority == "conversation":
        reasons.append("Required state is conversation-only.")
        actions.append("Introduce a structured workspace state file before full OpenCode enablement.")

    tool_manual = any(
        d.get("area") == "tools" and d.get("confidence") == "manual_review"
        for d in decisions
    )
    if tool_manual:
        reasons.append("Potential runtime scripts require manual tool inventory.")
        actions.append("Classify required runtime scripts into an explicit tool contract.")

    tools = changes.get("tools") or cfg.get("tools") or normalize_tool_contract(cfg)
    required_tools = [t for t in (tools.get("tools") or []) if t.get("requirement") == "required"]
    unresolved_required = [
        t.get("id", "unknown")
        for t in required_tools
        if t.get("type") not in {"script", "local_command", "mcp", "api_action"}
    ]
    if unresolved_required:
        reasons.append("Required tools have unsupported or unknown types: " + ", ".join(unresolved_required))
        actions.append("Map required tools to supported OpenCode integrations.")

    manual_areas = {
        d.get("area")
        for d in decisions
        if d.get("confidence") == "manual_review"
    }
    blocking_manual = manual_areas & {"project_contract", "workspace_state"}
    if blocking_manual:
        reasons.append("Manual review is required for OpenCode-critical areas: " + ", ".join(sorted(blocking_manual)))

    if not canonical or not (root / canonical).exists() or blocking_manual:
        status = "blocked"
        can_enable = False
    elif tool_manual or (requirement == "required" and authority == "conversation") or unresolved_required:
        status = "reduced"
        can_enable = False
    else:
        status = "ready"
        can_enable = True

    return {
        "status": status,
        "reasons": reasons,
        "can_enable_automatically": can_enable,
        "required_actions": actions,
    }


def assess_plugin(root: Path, cfg: dict[str, Any] | None, changes: dict[str, Any], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    if cfg is None:
        return {
            "status": "blocked",
            "reasons": ["Missing gpt-project.yaml."],
            "can_enable_automatically": False,
            "required_actions": ["Identify canonical project structure before enabling Plugin."],
        }

    reasons: list[str] = []
    actions: list[str] = []

    instructions = cfg.get("instructions") or {}
    canonical = instructions.get("canonical")
    if not canonical or not (root / canonical).exists():
        reasons.append("Canonical instruction is missing or unresolved.")
        actions.append("Identify a canonical instruction file.")

    tool_manual = any(
        d.get("area") == "tools" and d.get("confidence") == "manual_review"
        for d in decisions
    )
    if tool_manual:
        reasons.append("Potential runtime scripts require manual tool inventory.")
        actions.append("Classify scripts before treating them as Plugin runtime resources.")

    workspace = changes.get("workspace_state") or cfg.get("workspace_state") or normalize_workspace_state_contract(cfg)
    state = (workspace or {}).get("state", {})
    if state.get("requirement") == "required":
        reasons.append("Required persistent state depends on the host runtime in Plugin v1.")
        actions.append("Verify that the intended plugin host provides the required persistent state.")

    tools = changes.get("tools") or cfg.get("tools") or normalize_tool_contract(cfg)
    required_exec_tools = [
        t for t in (tools.get("tools") or [])
        if t.get("requirement") == "required"
        and t.get("type") in {"script", "local_command", "mcp", "api_action"}
    ]
    if required_exec_tools:
        reasons.append("Required executable tools are not automatically realized by Plugin v1.")
        actions.append("Provide a supported host integration or keep Plugin suitability reduced.")

    if not canonical or not (root / canonical).exists():
        status = "blocked"
        can_enable = False
    elif tool_manual or required_exec_tools or state.get("requirement") == "required":
        status = "reduced"
        can_enable = False
    else:
        status = "ready"
        can_enable = True

    return {
        "status": status,
        "reasons": reasons,
        "can_enable_automatically": can_enable,
        "required_actions": actions,
    }


def plugin_runtime_config() -> dict[str, Any]:
    return {
        "enabled": True,
        "role": "peer_distribution",
        "mode": "openai_plugin",
        "schema": "schemas/plugin-runtime.schema.json",
        "policy": "src/runtime-policy/plugin-runtime-policy.md",
        "model": "docs/plugin-runtime.md",
        "layout": {
            "manifest_file": "plugin.json",
            "skills": "skills",
            "references": "references",
            "assets": "assets",
            "scripts": "scripts",
        },
        "templates": {
            "readme": "templates/README.plugin.md.tpl",
        },
        "validation": {
            "require_manifest": True,
            "require_skill": True,
            "require_skill_frontmatter": True,
        },
    }


def opencode_runtime_config() -> dict[str, Any]:
    return {
        "enabled": True,
        "role": "peer_distribution",
        "mode": "opencode_workspace",
        "schema": "schemas/opencode-runtime.schema.json",
        "policy": "src/runtime-policy/opencode-runtime-policy.md",
        "model": "docs/opencode-runtime.md",
        "layout": {
            "instructions": "AGENTS.md",
            "config": "opencode.json",
            "tools": ".opencode/tools",
            "runtime_scripts": "scripts",
            "runtime_contract": ".opencode/runtime-contract.json",
            "knowledge": "knowledge",
        },
        "templates": {
            "readme": "templates/README.opencode.md.tpl",
        },
        "validation": {
            "require_agents_md": True,
            "require_runtime_contract": True,
        },
    }


def build_report(root: Path, cfg: dict[str, Any] | None) -> dict[str, Any]:
    source_class = classify_legacy(cfg)
    if cfg is None:
        return {
            "migration": {
                "source_class": source_class,
                "target_contract_version": 1,
                "status": "manual_review",
            },
            "decisions": [
                decision(
                    "project_contract",
                    "inventory",
                    "manual_review",
                    reason="gpt-project.yaml is missing; canonical sources must be identified before migration.",
                )
            ],
            "warnings": ["No gpt-project.yaml found. No automatic changes are allowed."],
            "changes": {},
            "opencode": assess_opencode(root, cfg, {}, []),
            "plugin": assess_plugin(root, cfg, {}, []),
        }

    decisions: list[dict[str, Any]] = []
    warnings: list[str] = []
    changes: dict[str, Any] = {}

    caps = cfg.get("capabilities")
    if isinstance(caps, dict) and isinstance(caps.get("requirements"), dict):
        decisions.append(decision("capabilities", "preserve", "not_applicable"))
    else:
        unknown = _legacy_unknown_capabilities(cfg)
        if unknown:
            decisions.append(decision(
                "capabilities",
                "review_unknown",
                "manual_review",
                evidence=unknown,
            ))
            warnings.append("Unknown legacy capabilities were not migrated automatically: " + ", ".join(unknown))
        else:
            changes["capabilities"] = normalize_capability_contract(cfg)
            confidence = "auto_with_warning" if isinstance(caps, dict) and "file_handling" in caps else "safe_auto"
            decisions.append(decision("capabilities", "normalize", confidence))
            if confidence == "auto_with_warning":
                warnings.append("Legacy file_handling was mapped to both filesystem.read and filesystem.write.")

    artifacts = cfg.get("artifacts")
    if isinstance(artifacts, dict) and isinstance(artifacts.get("outputs"), dict):
        decisions.append(decision("artifacts", "preserve", "not_applicable"))
    else:
        domain = _domain_artifact_candidates(cfg)
        if domain:
            decisions.append(decision("artifacts", "review_domain_outputs", "manual_review", evidence=domain))
            warnings.append("Domain-specific legacy artifacts require manual review: " + ", ".join(domain))
        else:
            normalized_artifacts = normalize_artifact_contract(cfg)
            if normalized_artifacts.get("outputs"):
                changes["artifacts"] = normalized_artifacts
                decisions.append(decision("artifacts", "normalize", "safe_auto"))
            else:
                decisions.append(decision("artifacts", "no_legacy_artifacts", "not_applicable"))

    if isinstance(cfg.get("workspace_state"), dict):
        decisions.append(decision("workspace_state", "preserve", "not_applicable"))
    else:
        ws = normalize_workspace_state_contract(cfg)
        changes["workspace_state"] = ws
        confidence = "safe_auto"
        state = ws.get("state", {})
        if state.get("authority") == "conversation":
            confidence = "auto_with_warning"
            warnings.append("Workspace/state was inferred without a structured workspace_file authority.")
        decisions.append(decision("workspace_state", "derive", confidence))

    if isinstance(cfg.get("tools"), dict):
        decisions.append(decision("tools", "preserve", "not_applicable"))
    else:
        legacy_tooling = isinstance(cfg.get("tooling"), dict) and isinstance(cfg["tooling"].get("tools"), list)
        scripts = _script_candidates(root, cfg)
        if legacy_tooling:
            changes["tools"] = normalize_tool_contract(cfg)
            decisions.append(decision("tools", "normalize_explicit_tools", "safe_auto"))
        elif scripts:
            decisions.append(decision("tools", "inventory_scripts", "manual_review", evidence=scripts))
            warnings.append(
                f"{len(scripts)} script candidate(s) were found but were not promoted to runtime tools automatically."
            )
        else:
            changes["tools"] = normalize_tool_contract(cfg)
            decisions.append(decision("tools", "create_empty_contract", "safe_auto"))

    status = "no_changes"
    if source_class == "L3" and not changes:
        status = "no_changes"
    elif any(d["confidence"] == "manual_review" for d in decisions):
        status = "ready_with_manual_review"
    elif warnings:
        status = "ready_with_warnings"
    elif changes:
        status = "ready"
    else:
        status = "no_changes"

    return {
        "migration": {
            "source_class": source_class,
            "target_contract_version": 1,
            "status": status,
        },
        "decisions": decisions,
        "warnings": warnings,
        "changes": changes,
        "opencode": assess_opencode(root, cfg, changes, decisions),
        "plugin": assess_plugin(root, cfg, changes, decisions),
    }


def _install_assets(root: Path, assets: tuple[str, ...], label: str) -> list[str]:
    copied: list[str] = []
    for rel in assets:
        src = BUILDER_ROOT / rel
        if not src.exists():
            raise FileNotFoundError(f"GPT Byggaren {label} adapter asset is missing: {rel}")
        dst = root / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)
    return copied


def install_plugin_assets(root: Path) -> list[str]:
    return _install_assets(root, PLUGIN_ASSETS, "Plugin")


def install_opencode_assets(root: Path) -> list[str]:
    return _install_assets(root, OPENCODE_ASSETS, "OpenCode")


def apply_changes(
    root: Path,
    cfg: dict[str, Any],
    report: dict[str, Any],
    enable_opencode: bool = False,
    enable_plugin: bool = False,
) -> bool:
    changes = report.get("changes") or {}
    updated = copy.deepcopy(cfg)
    changed = False
    for key in NEW_CONTRACT_KEYS:
        if key not in changes:
            continue
        current = updated.get(key)
        if key == "capabilities" and isinstance(current, dict) and isinstance(current.get("requirements"), dict):
            continue
        if key == "artifacts" and isinstance(current, dict) and isinstance(current.get("outputs"), dict):
            continue
        if key in {"workspace_state", "tools"} and isinstance(current, dict) and current.get("contract_version") == 1:
            continue

        value = copy.deepcopy(changes[key])
        if key == "capabilities":
            value.setdefault("schema", "schemas/capability-contract.schema.json")
        elif key == "artifacts":
            value.setdefault("schema", "schemas/artifact-contract.schema.json")
        elif key == "workspace_state":
            value.setdefault("schema", "schemas/workspace-state-contract.schema.json")
        elif key == "tools":
            value.setdefault("schema", "schemas/tool-contract.schema.json")

        updated[key] = value
        changed = True

    if enable_opencode and report.get("opencode", {}).get("can_enable_automatically"):
        runtime = updated.setdefault("runtime", {})
        if "opencode" not in runtime:
            runtime["opencode"] = opencode_runtime_config()
            changed = True
        if install_opencode_assets(root):
            changed = True

    if enable_plugin and report.get("plugin", {}).get("can_enable_automatically"):
        runtime = updated.setdefault("runtime", {})
        if "plugin" not in runtime:
            runtime["plugin"] = plugin_runtime_config()
            changed = True
        if install_plugin_assets(root):
            changed = True

    if not changed:
        return False

    (root / "gpt-project.yaml").write_text(
        yaml.safe_dump(updated, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze and migrate legacy GPT Byggaren projects.")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--enable-opencode", action="store_true")
    ap.add_argument("--enable-plugin", action="store_true")
    ap.add_argument("--json", action="store_true", dest="json_output")
    ap.add_argument("--report-file")
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    cfg = load_cfg(root)
    report = build_report(root, cfg)

    applied = False
    if args.apply:
        if cfg is None:
            report["apply"] = {"result": "blocked", "reason": "Missing gpt-project.yaml"}
        else:
            blocked_targets = []
            if args.enable_opencode and not report.get("opencode", {}).get("can_enable_automatically"):
                blocked_targets.append("OpenCode")
            if args.enable_plugin and not report.get("plugin", {}).get("can_enable_automatically"):
                blocked_targets.append("Plugin")
            if blocked_targets:
                report["apply"] = {
                    "result": "blocked",
                    "reason": "Compatibility is not ready for automatic enablement: " + ", ".join(blocked_targets),
                }
            else:
                applied = apply_changes(
                    root,
                    cfg,
                    report,
                    enable_opencode=args.enable_opencode,
                    enable_plugin=args.enable_plugin,
                )
                report["apply"] = {"result": "changed" if applied else "no_changes"}

    if args.report_file:
        path = Path(args.report_file)
        if not path.is_absolute():
            path = root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")

    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Legacy class: {report['migration']['source_class']}")
        print(f"Migration status: {report['migration']['status']}")
        for item in report["decisions"]:
            print(f"- {item['area']}: {item['action']} [{item['confidence']}]")
        for warning in report["warnings"]:
            print(f"WARNING: {warning}")
        print(f"OpenCode: {report['opencode']['status']}")
        print(f"Plugin: {report['plugin']['status']}")
        if args.apply:
            print(f"Apply: {'changed' if applied else report.get('apply', {}).get('result', 'no_changes')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
