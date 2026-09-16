#!/usr/bin/env python3
"""Materialize deterministic one-Interaction sequence diagrams for architecture reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

import report_profile
import view as view_engine


def _name(element: dict[str, Any] | None, fallback: str = "") -> str:
    if not element:
        return fallback
    return str(element.get("name") or element.get("id") or fallback)


def interaction_rows(project: Path) -> list[dict[str, Any]]:
    elements, _ = view_engine.load_project(project)
    scenarios = {eid: e for eid, e in elements.items() if e.get("type") == "Scenario"}
    rows: list[dict[str, Any]] = []
    for interaction in elements.values():
        if interaction.get("type") != "Interaction" or not interaction.get("id"):
            continue
        scenario_id = interaction.get("scenario") or ""
        scenario = scenarios.get(scenario_id)
        rows.append({
            "interaction": interaction,
            "scenario": scenario,
            "scenario_id": scenario_id,
            "scenario_name": _name(scenario, scenario_id),
            "interaction_name": _name(interaction, interaction["id"]),
        })
    rows.sort(key=lambda r: (
        str(r["scenario_name"]).casefold(),
        str(r["scenario_id"]),
        str(r["interaction_name"]).casefold(),
        str(r["interaction"]["id"]),
    ))
    return rows


def materialize(project: Path) -> list[dict[str, Any]]:
    profile = report_profile.load()
    one_per = bool(((profile.get("diagrams") or {}).get("sequence") or {}).get("one_interaction_per_diagram", False))
    if not one_per:
        result = view_engine.materialize(project, view_engine.default_definition("sequence"))
        if not (result.get("sequences") or []):
            return []
        return [{"title": "Sekvensöversikt", "interaction_id": None, "scenario_id": None, "result": result}]

    diagrams: list[dict[str, Any]] = []
    for row in interaction_rows(project):
        interaction = row["interaction"]
        definition = view_engine.default_definition("sequence")
        definition["filters"] = {"interaction_id": interaction["id"]}
        result = view_engine.materialize(project, definition)
        if not (result.get("sequences") or []):
            continue
        scenario_name = row["scenario_name"]
        interaction_name = row["interaction_name"]
        title = f"{scenario_name} – {interaction_name}" if scenario_name else interaction_name
        diagrams.append({
            "title": title,
            "interaction_id": interaction["id"],
            "scenario_id": row["scenario_id"] or None,
            "result": result,
        })
    return diagrams


def summary(project: Path) -> dict[str, Any]:
    diagrams = materialize(project)
    return {
        "diagram_count": len(diagrams),
        "diagrams": [
            {
                "title": d["title"],
                "interaction_id": d["interaction_id"],
                "scenario_id": d["scenario_id"],
                "participant_count": len({p.get("ref") for s in d["result"].get("sequences") or [] for p in s.get("participants") or [] if p.get("ref")}),
                "message_count": sum(len(s.get("messages") or []) for s in d["result"].get("sequences") or []),
            }
            for d in diagrams
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Materialize one deterministic sequence diagram per Interaction.")
    ap.add_argument("project", type=Path)
    ap.add_argument("--format", choices=["yaml", "json"], default="yaml")
    ns = ap.parse_args()
    try:
        data = summary(ns.project)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    if ns.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
