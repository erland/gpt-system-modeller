#!/usr/bin/env python3
"""Expose the canonical PDF presentation contract from the standard report profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import yaml

import report_profile


def build_contract(profile_path: Path | None = None) -> dict[str, Any]:
    report = report_profile.load(profile_path)
    return {
        "format": "system-modeller-pdf-presentation-v1",
        "profile": report["profile"],
        "sections": [
            {"id": section["id"], "title": section["title"]}
            for section in report["sections"]
        ],
        "presentation": report_profile.pdf_presentation(report),
        "diagram_policy": {
            "split_large_views": bool(report["diagrams"].get("split_large_views")),
            "preferred_max_elements": report["diagrams"]["preferred_max_elements"],
            "hard_max_elements": report["diagrams"]["hard_max_elements"],
            "preferred_max_relationships": report["diagrams"]["preferred_max_relationships"],
            "hard_max_relationships": report["diagrams"]["hard_max_relationships"],
            "one_interaction_per_sequence_diagram": bool(
                (report["diagrams"].get("sequence") or {}).get("one_interaction_per_diagram")
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Print the canonical System Modeller PDF presentation contract.")
    ap.add_argument("--profile", type=Path)
    ap.add_argument("--format", choices=["yaml", "json"], default="yaml")
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    try:
        contract = build_contract(ns.profile)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    if ns.format == "json":
        text = json.dumps(contract, ensure_ascii=False, indent=2) + "\n"
    else:
        text = yaml.safe_dump(contract, allow_unicode=True, sort_keys=False)
    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
