#!/usr/bin/env python3
"""Load and validate the canonical System Modeller architecture report profile."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "metamodel" / "report-profiles" / "standard.yaml"

REQUIRED_SECTION_IDS = [
    "purpose",
    "system_context",
    "functional",
    "use_cases",
    "information",
    "logical",
    "integration",
    "scenarios",
    "deployment",
    "decisions",
    "uncertainties",
    "evidence",
]


def load(path: Path | None = None) -> dict[str, Any]:
    profile_path = (path or DEFAULT_PROFILE).resolve()
    data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    report = data.get("architecture_report") or {}
    validate(report)
    return report


def validate(report: dict[str, Any]) -> None:
    if report.get("profile") != "standard":
        raise ValueError("architecture report profile must be 'standard' in B5")
    if report.get("user_selectable") is not False:
        raise ValueError("B5 standard profile must remain internal and not user-selectable")

    sections = report.get("sections") or []
    ids = [s.get("id") for s in sections if isinstance(s, dict)]
    if ids != REQUIRED_SECTION_IDS:
        raise ValueError(f"architecture report sections must be {REQUIRED_SECTION_IDS}, got {ids}")
    if any(not str(s.get("title") or "").strip() for s in sections):
        raise ValueError("every architecture report section must have a title")

    diagrams = report.get("diagrams") or {}
    required_budgets = (
        "preferred_max_elements",
        "hard_max_elements",
        "preferred_max_relationships",
        "hard_max_relationships",
    )
    for key in required_budgets:
        value = diagrams.get(key)
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"diagram budget {key} must be a positive integer")
    if diagrams["preferred_max_elements"] > diagrams["hard_max_elements"]:
        raise ValueError("preferred element budget cannot exceed hard budget")
    if diagrams["preferred_max_relationships"] > diagrams["hard_max_relationships"]:
        raise ValueError("preferred relationship budget cannot exceed hard budget")


def section_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {section["id"]: section for section in report["sections"]}


def section_titles(report: dict[str, Any]) -> list[str]:
    return [section["title"] for section in report["sections"]]


def primary_view_by_title(report: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for section in report["sections"]:
        views = section.get("views") or []
        if views:
            result[section["title"]] = views[0]
    return result
