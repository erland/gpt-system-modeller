#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.project_model import select_reference_profile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    results = []

    for path in sorted((root / "evals" / "reference-projects").glob("*.yaml")):
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        selected = select_reference_profile(case["characteristics"])
        expected = case["expected"]["profile"]

        results.append({
            "id": case["id"],
            "title": case["title"],
            "selected_profile": selected,
            "expected_profile": expected,
            "status": "pass" if selected == expected else "fail"
        })

    passed = sum(r["status"] == "pass" for r in results)
    payload = {
        "result": "pass" if passed == len(results) else "fail",
        "passed": passed,
        "total": len(results),
        "cases": results
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Reference projects: {passed}/{len(results)} passed")

    return 0 if payload["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
