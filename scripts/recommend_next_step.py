#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.project_model import load_project_status, get_registered_next_step, get_blockers


def recommend(root: Path) -> dict:
    status = load_project_status(root)

    blockers = get_blockers(status)
    validation = status.get("validation", {})
    hygiene = status.get("project_hygiene", {})
    next_step = get_registered_next_step(status)

    if blockers:
        return {"recommended": {
            "type": "corrective",
            "step_id": "C-AUTO",
            "title": "Åtgärda blockerande projektfel",
            "priority": "critical",
            "reason": "Projektstatus innehåller blockerande problem.",
            "evidence": [str(x) for x in blockers],
        }}

    if validation.get("last_result") in {"failed", "blocked", "fail"}:
        return {"recommended": {
            "type": "validation",
            "step_id": "V-AUTO",
            "title": "Åtgärda misslyckad validering",
            "priority": "critical",
            "reason": "Senaste valideringen är inte godkänd.",
            "evidence": [f"validation.last_result={validation.get('last_result')}"],
        }}

    if hygiene.get("last_result") in {"failed", "blocked", "fail"}:
        return {"recommended": {
            "type": "hygiene",
            "step_id": "H-AUTO",
            "title": "Åtgärda project hygiene",
            "priority": "high",
            "reason": "Project hygiene är inte godkänd.",
            "evidence": [f"project_hygiene.last_result={hygiene.get('last_result')}"],
        }}

    if next_step:
        return {"recommended": {
            "type": "planned",
            "step_id": next_step.get("recommended"),
            "title": next_step.get("title", "Nästa planerade steg"),
            "priority": "normal",
            "reason": next_step.get("reason", "Nästa relevanta plansteg."),
            "evidence": ["project-status.yaml:next_step"],
        }}

    return {"recommended": {
        "type": "release",
        "step_id": "R-AUTO",
        "title": "Bedöm release readiness",
        "priority": "normal",
        "reason": "Inga blockerare eller registrerade plansteg återstår.",
        "evidence": ["No next_step and no blockers"],
    }}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = recommend(Path(args.project_root).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        rec = result["recommended"]
        print(f"{rec['type']}: {rec['title']}")
        print(rec["reason"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
