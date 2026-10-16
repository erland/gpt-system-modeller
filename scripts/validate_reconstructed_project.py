#!/usr/bin/env python3
"""Run existing GPT project lint and schema checks without building distributions."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import yaml
import jsonschema

from lint_gpt_project import lint

SCHEMAS = {
    "capabilities": "capability-contract.schema.json",
    "artifacts": "artifact-contract.schema.json",
    "workspace_state": "workspace-state-contract.schema.json",
    "tools": "tool-contract.schema.json",
}


def validate(root: Path) -> dict:
    root = root.resolve()
    cfg = yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8"))
    if not isinstance(cfg, dict) or not isinstance(cfg.get("reconstruction"), dict):
        raise ValueError("Expected reconstructed project")
    status = yaml.safe_load((root / "project-status.yaml").read_text(encoding="utf-8"))
    errors = []
    checked = []
    for name, filename in SCHEMAS.items():
        value = cfg.get(name)
        schema_path = root / "schemas" / filename
        if not isinstance(value, dict) or not schema_path.is_file():
            errors.append(f"Missing canonical contract or schema: {name}")
            continue
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(value)
            checked.append(name)
        except (jsonschema.ValidationError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid {name}: {exc}")
    try:
        schema = json.loads((root / "schemas/project-status.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(status)
        checked.append("project_status")
    except (OSError, jsonschema.ValidationError, json.JSONDecodeError) as exc:
        errors.append(f"Project status schema validation: {exc}")
    lint_result = lint(root)
    if lint_result["summary"]["errors"]:
        errors.append("Ordinary project lint has errors")
    active = [name for name, runtime in cfg.get("runtime", {}).items()
              if isinstance(runtime, dict) and runtime.get("enabled")]
    if active:
        errors.append("Runtimes must remain disabled: " + ", ".join(active))
    if status.get("state", {}).get("overall") != "blocked":
        errors.append("Reconstruction status must remain blocked")
    if cfg["reconstruction"].get("release_ready") is not False:
        errors.append("Release must remain blocked")
    return {
        "result": "blocked" if errors else "validated_pending_runtime_review",
        "schema_checks": checked,
        "lint": lint_result,
        "errors": errors,
        "release_ready": False,
        "runtimes_enabled": active,
        "next_step": "Verify canonical completeness, dependency mappings and runtime parity before enabling builds.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project-root", required=True)
    args = p.parse_args()
    try:
        report = validate(Path(args.project_root))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
