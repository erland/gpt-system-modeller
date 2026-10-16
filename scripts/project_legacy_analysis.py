#!/usr/bin/env python3
"""Project evidence-backed analysis into a portable, review-only canonical draft."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from validate_legacy_interpretation import validate

def project(discovery: dict, interpretation: dict) -> dict:
    verdict = validate(discovery, interpretation)
    if verdict["errors"]:
        raise ValueError("Invalid interpretation: " + "; ".join(verdict["errors"]))
    by_role = {k: [] for k in ("instructions", "knowledge", "tool", "workflow", "configuration", "other")}
    for claim in interpretation["claims"]:
        by_role[claim["role"]].append({
            "description": claim["description"],
            "confidence": claim["confidence"],
            "evidence": claim["evidence"],
        })
    return {
        "schema_version": 1,
        "status": "review_required",
        "model_type": "platform_neutral_project_draft",
        "functional_evidence": by_role,
        "unresolved": interpretation["unresolved"],
        "canonical_core": {
            "status": "not_yet_verified",
            "reason": "A file-level reference cannot prove complete or correct runtime instructions.",
        },
        "skills": {
            "status": "not_yet_classified",
            "candidates": [],
            "reason": "Do not infer standalone skill boundaries solely from paths or filenames.",
        },
        "runtime_targets": {"chat_zip": False, "plugin": False, "claude": False, "opencode": False},
        "canonical_contract_created": False,
        "release_ready": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", required=True)
    parser.add_argument("--interpretation", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        a = json.loads(Path(args.discovery).read_text(encoding="utf-8"))
        b = json.loads(Path(args.interpretation).read_text(encoding="utf-8"))
        result = project(a, b)
        target = Path(args.output)
        if target.exists():
            raise FileExistsError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        print(f"Canonical draft rejected: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"result": "draft_created_for_review", "release_ready": False}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
