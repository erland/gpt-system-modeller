#!/usr/bin/env python3
"""Attach schema-checked, conservative contracts to a reviewed reconstruction.

This does not enable runtimes or produce release-ready distributions.
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path
import yaml
import jsonschema

BUILDER = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "capabilities": "capability-contract.schema.json",
    "artifacts": "artifact-contract.schema.json",
    "workspace_state": "workspace-state-contract.schema.json",
    "tools": "tool-contract.schema.json",
}


def complete(root: Path) -> dict:
    root = root.resolve()
    cfg_path = root / "gpt-project.yaml"
    if not cfg_path.is_file():
        raise ValueError("Promoted gpt-project.yaml is required")
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict) or cfg.get("reconstruction", {}).get("status") != "requires_runtime_validation":
        raise ValueError("Not a reviewed reconstruction")
    if cfg["reconstruction"].get("release_ready") is not False:
        raise ValueError("Reconstructed project must remain blocked")
    if any(isinstance(v, dict) and v.get("enabled") for v in cfg.get("runtime", {}).values()):
        raise ValueError("Cannot complete contracts with active runtime targets")
    for name in SCHEMAS:
        if name in cfg:
            raise ValueError(f"Refusing to replace existing {name} contract")

    draft_path = root / "reconstructed-canonical" / "project-draft.json"
    if not draft_path.is_file():
        raise ValueError("Missing reconstruction evidence")
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if draft.get("release_ready") is not False:
        raise ValueError("Unexpected project-draft state")
    status_path = root / "project-status.yaml"
    if not status_path.is_file():
        raise ValueError("Missing authoritative project status")
    status = yaml.safe_load(status_path.read_text(encoding="utf-8"))
    if status.get("state", {}).get("overall") != "blocked":
        raise ValueError("Project status must remain blocked")

    contracts = {
        "capabilities": {
            "contract_version": 1, "recommendation_mode": "inferred_from_use_case",
            "ask_user_only_when_business_choice_is_ambiguous": True,
            "requirements": {},
        },
        "artifacts": {
            "contract_version": 1,
            "outputs": {
                "project_package": {
                    "kind": "package", "format": "zip", "requirement": "optional",
                    "persistence": "persistent",
                },
            },
        },
        "workspace_state": {
            "contract_version": 1,
            "workspace": {
                "requirement": "required", "persistence": "required",
                "portable": True, "separate_from_assistant": True,
            },
            "state": {
                "requirement": "required", "persistence": "required",
                "authority": "workspace_file", "format": "yaml",
                "path": "project-status.yaml", "conversation_fallback": False,
            },
        },
        "tools": {"contract_version": 1, "tools": []},
    }

    missing = []
    for name, filename in SCHEMAS.items():
        src = BUILDER / "schemas" / filename
        dest = root / "schemas" / filename
        if dest.exists():
            raise ValueError(f"Refusing overwrite of schema: {dest}")
        schema = json.loads(src.read_text(encoding="utf-8"))
        value = contracts[name]
        value["schema"] = f"schemas/{filename}"
        jsonschema.Draft202012Validator(schema).validate(value)
        missing.append((src, dest))
        cfg[name] = value

    # The empty capabilities/tools lists are NOT evidence of absence:
    # reconstructing host requirements and tool mapping remains mandatory.
    report = {
        "result": "contracts_scaffolded",
        "validated_schemas": sorted(SCHEMAS),
        "candidate_tools_unverified": draft.get("tool_candidates", []),
        "candidate_integrations_unverified": draft.get("integration_candidates", []),
        "knowledge_completeness_not_proven": True,
        "runtime_parity_not_verified": True,
        "release_ready": False,
    }
    cfg["reconstruction"]["status"] = "canonical_contracts_scaffolded"
    cfg["reconstruction"]["release_ready"] = False
    for src, dest in missing:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    target = root / "reconstructed-canonical" / "CONTRACT-VALIDATION.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    try:
        result = complete(Path(args.project_root))
    except (ValueError, KeyError, OSError, json.JSONDecodeError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        print(f"Contract scaffold blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
