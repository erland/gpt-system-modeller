#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from migrate_legacy_project import (
    apply_changes,
    build_report,
    load_cfg,
)


SUPPORTED_TARGETS = {
    "opencode": "opencode",
    "open-code": "opencode",
    "open_code": "opencode",
    "plugin": "plugin",
    "openai-plugin": "plugin",
    "openai_plugin": "plugin",
}


def normalize_target(value: str) -> str:
    key = value.strip().lower()
    if key not in SUPPORTED_TARGETS:
        raise ValueError(f"Unsupported migration target: {value}")
    return SUPPORTED_TARGETS[key]


def summarize(report: dict[str, Any], target: str, applied: bool, execute: bool) -> dict[str, Any]:
    target_result = report[target]
    compatibility = target_result["status"]

    warnings = list(report.get("warnings") or [])
    required_actions = list(target_result.get("required_actions") or [])
    changed_areas = sorted((report.get("changes") or {}).keys())

    if not execute:
        status = "ready_to_migrate" if target_result.get("can_enable_automatically") else (
            "needs_review" if compatibility == "reduced" else "blocked"
        )
        next_action = (
            "Apply safe migration and enable the requested runtime."
            if status == "ready_to_migrate"
            else (required_actions[0] if required_actions else "Resolve migration blockers.")
        )
    elif compatibility == "ready":
        status = "completed"
        next_action = "Validate and build the updated project distributions."
    elif compatibility == "reduced":
        status = "needs_review"
        next_action = required_actions[0] if required_actions else "Review reduced runtime compatibility."
    else:
        status = "blocked"
        next_action = required_actions[0] if required_actions else "Resolve migration blockers."

    return {
        "target_runtime": target,
        "status": status,
        "compatibility": compatibility,
        "applied": applied,
        "changed_areas": changed_areas,
        "warnings": warnings,
        "required_actions": required_actions,
        "next_action": next_action,
        "technical_report": report,
    }


def run(root: Path, target: str, execute: bool) -> dict[str, Any]:
    cfg = load_cfg(root)
    report = build_report(root, cfg)

    if cfg is None:
        return summarize(report, target, False, execute)

    target_result = report[target]
    if not execute:
        return summarize(report, target, False, False)

    if not target_result.get("can_enable_automatically"):
        return summarize(report, target, False, True)

    applied = apply_changes(
        root,
        cfg,
        report,
        enable_opencode=(target == "opencode"),
        enable_plugin=(target == "plugin"),
    )
    return summarize(report, target, applied, True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="User-oriented migration workflow for adding a runtime to an existing GPT Byggaren project."
    )
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--target-runtime", required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--json", action="store_true", dest="json_output")
    ap.add_argument("--result-file")
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    try:
        target = normalize_target(args.target_runtime)
    except ValueError as exc:
        print(str(exc))
        return 2

    result = run(root, target, args.execute)

    if args.result_file:
        path = Path(args.result_file)
        if not path.is_absolute():
            path = root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")

    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Target runtime: {result['target_runtime']}")
        print(f"Status: {result['status']}")
        print(f"Compatibility: {result['compatibility']}")
        if result["changed_areas"]:
            print("Changed areas: " + ", ".join(result["changed_areas"]))
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        for action in result["required_actions"]:
            print(f"ACTION: {action}")
        print(f"Next: {result['next_action']}")

    return 0 if result["status"] in {"completed", "ready_to_migrate", "needs_review"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
