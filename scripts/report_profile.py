#!/usr/bin/env python3
"""Load and validate System Modeller architecture report profiles."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "metamodel" / "report-profiles"
CATALOG = PROFILE_DIR / "catalog.yaml"
DEFAULT_PROFILE = PROFILE_DIR / "standard.yaml"

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


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = (path or CATALOG).resolve()
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    catalog = data.get("report_profiles") or {}
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("version") != 1:
        raise ValueError("report profile catalog version must be 1")
    if catalog.get("user_selectable") is not False:
        raise ValueError("B11 report profile catalog must not expose user selection")

    profiles = catalog.get("profiles") or []
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("report profile catalog must contain profiles")
    ids = [p.get("id") for p in profiles if isinstance(p, dict)]
    if ids != ["overview", "standard", "detailed"]:
        raise ValueError("B11 profile order must be overview, standard, detailed")
    if len(ids) != len(set(ids)):
        raise ValueError("report profile ids must be unique")

    default = catalog.get("default_profile")
    by_id = {p["id"]: p for p in profiles}
    if default not in by_id:
        raise ValueError("default report profile must exist in catalog")
    default_entry = by_id[default]
    if default_entry.get("implemented") is not True or default_entry.get("status") != "stable":
        raise ValueError("default report profile must be implemented and stable")

    implemented = [p for p in profiles if p.get("implemented") is True]
    if [p.get("id") for p in implemented] != ["standard"]:
        raise ValueError("B11 must keep standard as the only implemented profile")
    if any(p.get("user_selectable") is not False for p in profiles):
        raise ValueError("B11 profiles must remain non-user-selectable")
    if default_entry.get("file") != "standard.yaml":
        raise ValueError("standard profile must resolve to standard.yaml")


def profile_entries(catalog: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    cat = catalog or load_catalog()
    return {p["id"]: p for p in cat["profiles"]}


def available_profiles(catalog: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    cat = catalog or load_catalog()
    return [dict(p) for p in cat["profiles"]]


def resolve_profile_path(profile: str | None = None, catalog: dict[str, Any] | None = None) -> Path:
    cat = catalog or load_catalog()
    profile_id = profile or cat["default_profile"]
    entry = profile_entries(cat).get(profile_id)
    if not entry:
        raise ValueError(f"unknown report profile: {profile_id}")
    if entry.get("implemented") is not True:
        raise ValueError(f"report profile '{profile_id}' is planned but not implemented")
    filename = str(entry.get("file") or "").strip()
    if not filename:
        raise ValueError(f"implemented report profile '{profile_id}' has no file")
    return (PROFILE_DIR / filename).resolve()


def load(path: Path | None = None, profile: str | None = None) -> dict[str, Any]:
    if path is not None and profile is not None:
        raise ValueError("use either an explicit profile path or a named profile, not both")
    if path is None:
        catalog = load_catalog()
        expected_profile = profile or catalog["default_profile"]
        profile_path = resolve_profile_path(expected_profile, catalog)
    else:
        profile_path = path.resolve()
        expected_profile = None
    data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    report = data.get("architecture_report") or {}
    validate(report, expected_profile=expected_profile)
    return report


def _positive_number(value: Any, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


def validate(report: dict[str, Any], expected_profile: str | None = None) -> None:
    profile = str(report.get("profile") or "").strip()
    if not profile:
        raise ValueError("architecture report profile id is required")
    if expected_profile and profile != expected_profile:
        raise ValueError(f"architecture report profile must be '{expected_profile}', got '{profile}'")
    if report.get("user_selectable") is not False:
        raise ValueError("report profiles must remain internal and not user-selectable in B11")

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
