#!/usr/bin/env python3
"""Promote a reviewed recovered instruction into a non-release canonical project."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import yaml


REQUIRED_REVIEWS = ("instruction_semantics", "knowledge_completeness", "tool_dependencies")


def promote(root: Path, review_file: Path) -> dict:
    root = root.resolve()
    if (root / "gpt-project.yaml").exists():
        raise ValueError("Project contract already exists; refusing overwrite")
    draft_path = root / "reconstructed-canonical" / "project-draft.json"
    if not draft_path.is_file():
        raise ValueError("Missing reconstructed project draft")
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    review = json.loads(review_file.read_text(encoding="utf-8"))
    if draft.get("status") != "review_required" or draft.get("release_ready") is not False:
        raise ValueError("Draft is not in expected review state")
    approvals = review.get("reviews") or {}
    if any(approvals.get(key) is not True for key in REQUIRED_REVIEWS):
        raise ValueError("All semantic, Knowledge, and tool reviews must be explicitly approved")
    if not isinstance(review.get("project_id"), str) or not review["project_id"].strip():
        raise ValueError("A reviewed project_id is required")
    if not isinstance(review.get("project_name"), str) or not review["project_name"].strip():
        raise ValueError("A reviewed project_name is required")
    source_rel = Path(draft["instruction"])
    if source_rel.is_absolute() or ".." in source_rel.parts:
        raise ValueError("Unsafe recovered instruction path")
    source = (root / source_rel).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError("Recovered instruction is unavailable")
    original = source.read_bytes()
    expected = review.get("instruction_sha256")
    if expected != hashlib.sha256(original).hexdigest():
        raise ValueError("Instruction digest does not match reviewed material")
    target = root / "src" / "instructions" / "system.md"
    if target.exists():
        raise ValueError("Canonical instruction already exists; refusing overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    cfg = {
        "schema_version": 1,
        "project": {"id": review["project_id"], "name": review["project_name"]},
        "instructions": {"canonical": "src/instructions/system.md"},
        "runtime": {
            "primary": "none",
            "chat_zip": {"enabled": False},
            "claude": {"enabled": False},
            "opencode": {"enabled": False},
            "plugin": {"enabled": False},
            "custom_gpt": {"enabled": False},
        },
        "reconstruction": {
            "status": "requires_runtime_validation",
            "source": draft["source_instruction"],
            "review_attestation": review_file.name,
            "release_ready": False,
        },
    }
    # Set up explicit, schema-compatible project state before writing the contract.
    plan_path = root / "docs" / "development-plan.md"
    status_path = root / "project-status.yaml"
    for path in (plan_path, status_path, root / "STATUS.md", root / "PROJECT.md", root / "README.md", root / "schemas/project-status.schema.json"):
        if path.exists():
            raise ValueError(f"Refusing to overwrite existing project artifact: {path.name}")
    cfg["development"] = {
        "plan": "docs/development-plan.md",
        "status": "project-status.yaml",
        "human_readable_status": "STATUS.md",
        "status_schema": "schemas/project-status.schema.json",
    }
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        "# Development plan: reconstructed project\\n\\n"
        "1. Verify canonical contracts, missing dependencies, and runtime parity before enabling any distribution.\\n",
        encoding="utf-8",
    )
    status = {
        "schema_version": 1,
        "project": {"id": review["project_id"], "name": review["project_name"]},
        "plan": {"path": "docs/development-plan.md", "total_steps": 1},
        "progress": {"current_step": 1, "last_completed_step": 0, "completed_steps": []},
        "state": {
            "overall": "blocked",
            "blocking_issues": [
                "Complete canonical contracts and runtime parity validation are outstanding.",
                "All distribution targets remain disabled until verified.",
            ],
            "warnings": ["Reconstructed instructions may differ from the original canonical source."],
        },
        "next_step": {
            "recommended": 1,
            "title": "Validate canonical contracts and runtime parity",
            "reason": "The reconstruction is reviewed but is not a complete, buildable project.",
        },
        "resume": {
            "supported": True,
            "required_files": [
                "gpt-project.yaml", "project-status.yaml", "docs/development-plan.md",
                "reconstructed-canonical/project-draft.json",
            ],
            "human_readable_status": "STATUS.md",
        },
    }
    status_path.write_text(yaml.safe_dump(status, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (root / "STATUS.md").write_text(
        "# Status\\n\\nBlocked: canonical contracts and runtime parity must be validated before release.\\n",
        encoding="utf-8",
    )
    (root / "PROJECT.md").write_text(
        "# Reconstructed project\\n\\nSource: " + draft["source_instruction"] +
        "\\n\\nStatus: review completed; runtime validation outstanding.\\n",
        encoding="utf-8",
    )
    # Supply the existing authoritative schema and the README required by project lint.
    schema_target = root / "schemas" / "project-status.schema.json"
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).resolve().parents[1] / "schemas" / "project-status.schema.json", schema_target)
    (root / "README.md").write_text(
        "# " + review["project_name"] + "\\n\\n"
        "Recovered GPT project; all runtimes are disabled pending validation.\\n",
        encoding="utf-8",
    )
    (root / "gpt-project.yaml").write_text(
        yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return {"result": "promoted_for_validation", "release_ready": False,
            "runtime_targets_enabled": [], "contract": "gpt-project.yaml"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--review-file", required=True)
    args = ap.parse_args()
    try:
        result = promote(Path(args.project_root), Path(args.review_file))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Promotion blocked: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
