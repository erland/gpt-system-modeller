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


def _positive_number(value: Any, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


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

    validate_pdf_presentation((report.get("presentation") or {}).get("pdf") or {})


def validate_pdf_presentation(pdf: dict[str, Any]) -> None:
    if not isinstance(pdf, dict) or not pdf:
        raise ValueError("presentation.pdf contract is required")

    page = pdf.get("page") or {}
    if page.get("size") != "A4":
        raise ValueError("PDF page size must be A4")
    if page.get("orientation") not in {"portrait", "landscape"}:
        raise ValueError("PDF orientation must be portrait or landscape")
    for key in ("margin_top_mm", "margin_right_mm", "margin_bottom_mm", "margin_left_mm"):
        _positive_number(page.get(key), f"PDF {key}")

    headings = pdf.get("headings") or {}
    for key in ("title_level", "section_level", "diagram_group_level", "detail_diagram_level"):
        value = headings.get(key)
        if not isinstance(value, int) or value < 1 or value > 6:
            raise ValueError(f"PDF heading {key} must be an integer 1..6")
    if not (
        headings["title_level"] < headings["section_level"]
        < headings["diagram_group_level"] < headings["detail_diagram_level"]
    ):
        raise ValueError("PDF heading levels must increase title -> section -> diagram group -> detail")

    diagram = pdf.get("diagrams") or {}
    width = diagram.get("max_width_percent")
    if not isinstance(width, (int, float)) or isinstance(width, bool) or not (1 <= width <= 100):
        raise ValueError("PDF diagram max_width_percent must be within 1..100")
    _positive_number(diagram.get("max_height_mm"), "PDF diagram max_height_mm")
    if diagram.get("caption_position") not in {"above", "below"}:
        raise ValueError("PDF diagram caption_position must be above or below")
    if not str(diagram.get("caption_prefix") or "").strip():
        raise ValueError("PDF diagram caption_prefix is required")

    tables = pdf.get("tables") or {}
    _positive_number(tables.get("font_size_pt"), "PDF table font_size_pt")
    text = pdf.get("text") or {}
    _positive_number(text.get("body_font_size_pt"), "PDF body_font_size_pt")
    _positive_number(text.get("line_spacing"), "PDF line_spacing")

    pagination = pdf.get("pagination") or {}
    for key in ("orphan_lines", "widow_lines"):
        value = pagination.get(key)
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"PDF pagination {key} must be a positive integer")


def pdf_presentation(report: dict[str, Any]) -> dict[str, Any]:
    pdf = ((report.get("presentation") or {}).get("pdf") or {})
    validate_pdf_presentation(pdf)
    return pdf


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
