#!/usr/bin/env python3
"""Measure materialized view complexity against the canonical report profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

import report_profile
import view as view_engine

ROOT = Path(__file__).resolve().parents[1]


def diagram_policy(profile: dict[str, Any]) -> dict[str, Any]:
    report = profile.get("architecture_report") or {}
    policy = report.get("diagrams") or {}
    required = (
        "preferred_max_elements",
        "hard_max_elements",
        "preferred_max_relationships",
        "hard_max_relationships",
    )
    missing = [name for name in required if name not in policy]
    if missing:
        raise ValueError(f"diagram policy missing: {', '.join(missing)}")
    return policy


def classify(element_count: int, relationship_count: int, policy: dict[str, Any]) -> str:
    if (
        element_count > int(policy["hard_max_elements"])
        or relationship_count > int(policy["hard_max_relationships"])
    ):
        return "above_hard"
    if (
        element_count > int(policy["preferred_max_elements"])
        or relationship_count > int(policy["preferred_max_relationships"])
    ):
        return "above_preferred"
    return "within_preferred"


def sequence_metrics(result: dict[str, Any]) -> dict[str, int]:
    refs: set[str] = set()
    message_count = 0
    interaction_count = 0
    for seq in result.get("sequences") or []:
        interaction_count += 1
        for participant in seq.get("participants") or []:
            ref = participant.get("ref") if isinstance(participant, dict) else None
            if ref:
                refs.add(ref)
        message_count += len(seq.get("messages") or [])
    return {
        "interaction_count": interaction_count,
        "participant_count": len(refs),
        "message_count": message_count,
    }


def measure_result(result: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    summary = result.get("summary") or {}
    elements = int(summary.get("element_count", len(result.get("elements") or [])))
    relationships = int(summary.get("link_count", len(result.get("links") or [])))
    status = classify(elements, relationships, policy)
    out: dict[str, Any] = {
        "view_type": (result.get("view") or {}).get("type"),
        "element_count": elements,
        "relationship_count": relationships,
        "classification": status,
        "preferred_budget_exceeded": status in {"above_preferred", "above_hard"},
        "hard_budget_exceeded": status == "above_hard",
        "split_recommended": bool(policy.get("split_large_views", False)) and status != "within_preferred",
        "budget": {
            "preferred_max_elements": int(policy["preferred_max_elements"]),
            "hard_max_elements": int(policy["hard_max_elements"]),
            "preferred_max_relationships": int(policy["preferred_max_relationships"]),
            "hard_max_relationships": int(policy["hard_max_relationships"]),
        },
    }
    if out["view_type"] == "sequence":
        out["sequence"] = sequence_metrics(result)
    return out


def profile_view_types(profile: dict[str, Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    report = profile.get("architecture_report") or {}
    for section in report.get("sections") or []:
        for view_type in section.get("views") or []:
            if view_type not in seen:
                seen.add(view_type)
                result.append(view_type)
    return result


def measure_project(project: Path, view_types: list[str] | None = None) -> dict[str, Any]:
    profile = report_profile.load_standard_profile()
    policy = diagram_policy(profile)
    types = view_types or profile_view_types(profile)
    views = []
    for view_type in types:
        definition = view_engine.default_definition(view_type)
        materialized = view_engine.materialize(project, definition)
        views.append(measure_result(materialized, policy))
    return {
        "profile": (profile.get("architecture_report") or {}).get("profile", "standard"),
        "views": views,
        "summary": {
            "view_count": len(views),
            "above_preferred_count": sum(v["preferred_budget_exceeded"] for v in views),
            "above_hard_count": sum(v["hard_budget_exceeded"] for v in views),
            "split_recommended_count": sum(v["split_recommended"] for v in views),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure view complexity against the standard architecture report profile.")
    ap.add_argument("project", type=Path)
    ap.add_argument("--type", action="append", dest="types", help="View type to measure; repeatable. Defaults to all profile views.")
    ap.add_argument("--format", choices=["yaml", "json"], default="yaml")
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    try:
        result = measure_project(ns.project, ns.types)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    if ns.format == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    else:
        text = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
