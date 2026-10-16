#!/usr/bin/env python3
"""Validate AI-proposed interpretations against immutable discovery evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROLES = {"instructions", "knowledge", "tool", "workflow", "configuration", "other"}
CONFIDENCE = {"high", "medium", "low"}


def validate(discovery: dict, interpretation: dict) -> dict:
    indexed = {item["path"]: item["sha256"] for item in discovery.get("source_files", [])}
    errors = []
    if discovery.get("status") != "analysis_required":
        errors.append("Expected analysis_required discovery")
    if interpretation.get("schema_version") != 1:
        errors.append("Unsupported interpretation schema_version")
    if interpretation.get("release_ready") is not False:
        errors.append("Interpretation must explicitly block release")
    if interpretation.get("runtime_activated") is not False:
        errors.append("Interpretation must not activate a runtime")
    claims = interpretation.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("At least one supported claim is required")
        claims = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"Claim {i}: expected object")
            continue
        if claim.get("role") not in ROLES:
            errors.append(f"Claim {i}: invalid role")
        if claim.get("confidence") not in CONFIDENCE:
            errors.append(f"Claim {i}: invalid confidence")
        if not isinstance(claim.get("description"), str) or not claim["description"].strip():
            errors.append(f"Claim {i}: missing description")
        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"Claim {i}: missing source evidence")
            continue
        for ref in evidence:
            if not isinstance(ref, dict) or ref.get("path") not in indexed or indexed.get(ref.get("path")) != ref.get("sha256"):
                errors.append(f"Claim {i}: unknown or modified evidence")
    unresolved = interpretation.get("unresolved")
    if not isinstance(unresolved, list):
        errors.append("Explicit unresolved list required")
    return {
        "result": "rejected" if errors else "accepted_for_review",
        "errors": errors,
        "claims_checked": len(claims),
        "canonical_contract_created": False,
        "release_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", required=True)
    parser.add_argument("--interpretation", required=True)
    args = parser.parse_args()
    try:
        discovery = json.loads(Path(args.discovery).read_text(encoding="utf-8"))
        interpretation = json.loads(Path(args.interpretation).read_text(encoding="utf-8"))
        report = validate(discovery, interpretation)
    except (OSError, ValueError) as exc:
        print(f"Analysis validation failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
