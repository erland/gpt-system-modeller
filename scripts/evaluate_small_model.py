#!/usr/bin/env python3
"""Validate and score System Modeller small-model regression runs.

The script does not judge free-form model text. A human or external harness records
whether each required/forbidden rubric item was satisfied. This script then validates
that evidence and computes deterministic case, dimension and overall results.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = ROOT / "evals" / "small-model" / "suite.yaml"


def load_yaml(path: Path) -> Any:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    return data


def fail(msg: str) -> None:
    raise ValueError(msg)


def validate_suite(suite_path: Path) -> dict[str, Any]:
    suite = load_yaml(suite_path)
    if suite.get("format") != "system-modeller-small-model-suite-v1":
        fail("unsupported or missing suite format")
    dimensions = suite.get("dimensions")
    cases = suite.get("cases")
    if not isinstance(dimensions, dict) or not dimensions:
        fail("suite requires dimensions")
    if not isinstance(cases, list) or not cases:
        fail("suite requires cases")

    seen: set[str] = set()
    base = suite_path.parent
    for entry in cases:
        if not isinstance(entry, dict):
            fail("suite case entry must be a mapping")
        cid = entry.get("id")
        filename = entry.get("file")
        dimension = entry.get("dimension")
        if not isinstance(cid, str) or not cid:
            fail("suite case requires id")
        if cid in seen:
            fail(f"duplicate suite case id: {cid}")
        seen.add(cid)
        if dimension not in dimensions:
            fail(f"case {cid} references unknown dimension {dimension!r}")
        if not isinstance(filename, str) or not filename:
            fail(f"case {cid} requires file")
        case_path = base / filename
        if not case_path.is_file():
            fail(f"case file missing: {filename}")
        case = load_yaml(case_path)
        if case.get("id") != cid:
            fail(f"case id mismatch for {filename}")
        expected = case.get("expected") or {}
        required = expected.get("required")
        forbidden = expected.get("forbidden")
        if not isinstance(required, list) or not required:
            fail(f"case {cid} requires non-empty expected.required")
        if not isinstance(forbidden, list):
            fail(f"case {cid} requires expected.forbidden list")
        threshold = (case.get("scoring") or {}).get("pass_threshold")
        if threshold is None or not 0 <= float(threshold) <= 1:
            fail(f"case {cid} requires pass_threshold between 0 and 1")
    return suite


def expected_case_map(suite_path: Path, suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for entry in suite["cases"]:
        result[entry["id"]] = load_yaml(suite_path.parent / entry["file"])
    return result


def validate_results(data: dict[str, Any], suite: dict[str, Any], cases: dict[str, dict[str, Any]]) -> None:
    if data.get("format") != "system-modeller-small-model-result-v1":
        fail("unsupported or missing result format")
    model = data.get("model")
    if not isinstance(model, dict) or not model.get("id") or not model.get("class"):
        fail("result requires model.id and model.class")
    classes = {x.get("id") for x in suite.get("model_classes", []) if isinstance(x, dict)}
    if model["class"] not in classes:
        fail(f"unknown model class: {model['class']}")
    results = data.get("cases")
    if not isinstance(results, dict):
        fail("result requires cases mapping")
    missing = [cid for cid in cases if cid not in results]
    extra = [cid for cid in results if cid not in cases]
    if missing:
        fail(f"missing result cases: {', '.join(missing)}")
    if extra:
        fail(f"unknown result cases: {', '.join(extra)}")

    for cid, case in cases.items():
        result = results[cid]
        if not isinstance(result, dict):
            fail(f"result case {cid} must be a mapping")
        required = result.get("required")
        forbidden = result.get("forbidden")
        expected_required = case["expected"]["required"]
        expected_forbidden = case["expected"]["forbidden"]
        if not isinstance(required, list) or len(required) != len(expected_required):
            fail(f"case {cid}: required judgments must match rubric item count")
        if not isinstance(forbidden, list) or len(forbidden) != len(expected_forbidden):
            fail(f"case {cid}: forbidden judgments must match rubric item count")
        if any(type(x) is not bool for x in required + forbidden):
            fail(f"case {cid}: judgments must be booleans")


def score_case(case: dict[str, Any], result: dict[str, Any]) -> tuple[float, bool]:
    required = result["required"]
    forbidden = result["forbidden"]
    total = len(required) + len(forbidden)
    passed_items = sum(required) + sum(1 for observed in forbidden if not observed)
    score = passed_items / total if total else 1.0
    threshold = float((case.get("scoring") or {}).get("pass_threshold", 1.0))
    return score, score >= threshold


def evaluate(suite_path: Path, result_path: Path) -> dict[str, Any]:
    suite = validate_suite(suite_path)
    cases = expected_case_map(suite_path, suite)
    data = load_yaml(result_path)
    validate_results(data, suite, cases)

    suite_entries = {x["id"]: x for x in suite["cases"]}
    by_dimension: dict[str, list[float]] = defaultdict(list)
    case_output: dict[str, Any] = {}
    critical_failures: list[str] = []

    for cid, case in cases.items():
        score, passed = score_case(case, data["cases"][cid])
        dimension = suite_entries[cid]["dimension"]
        by_dimension[dimension].append(score)
        case_output[cid] = {
            "dimension": dimension,
            "criticality": case.get("criticality", "normal"),
            "score": round(score, 4),
            "passed": passed,
        }
        if case.get("criticality") == "critical" and not passed:
            critical_failures.append(cid)

    threshold = float((suite.get("policy") or {}).get("dimension_pass_threshold", 1.0))
    dimensions: dict[str, Any] = {}
    for dimension in suite["dimensions"]:
        values = by_dimension.get(dimension, [])
        score = sum(values) / len(values) if values else 1.0
        dimensions[dimension] = {"score": round(score, 4), "passed": score >= threshold}

    all_scores = [v["score"] for v in case_output.values()]
    overall = sum(all_scores) / len(all_scores) if all_scores else 1.0
    overall_threshold = float((suite.get("policy") or {}).get("overall_pass_threshold", 1.0))
    critical_gate = not critical_failures
    canonical_mutation_allowed = critical_gate if (suite.get("policy") or {}).get("critical_case_failure_blocks_canonical_mutation", True) else True

    return {
        "format": "system-modeller-small-model-summary-v1",
        "model": data["model"],
        "cases": case_output,
        "dimensions": dimensions,
        "overall": {"score": round(overall, 4), "passed": overall >= overall_threshold and critical_gate},
        "critical_failures": critical_failures,
        "canonical_mutation_allowed": canonical_mutation_allowed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate/score the Plan B small-model regression suite")
    ap.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    ap.add_argument("--results", type=Path)
    ap.add_argument("--format", choices=("yaml", "text"), default="text")
    ns = ap.parse_args()
    try:
        suite_path = ns.suite.resolve()
        if ns.results is None:
            suite = validate_suite(suite_path)
            print(f"Small-model suite OK: {len(suite['cases'])} cases, {len(suite['dimensions'])} dimensions")
            return 0
        summary = evaluate(suite_path, ns.results.resolve())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if ns.format == "yaml":
        print(yaml.safe_dump(summary, allow_unicode=True, sort_keys=False).rstrip())
    else:
        model = summary["model"]
        print(f"Model: {model['id']} ({model['class']})")
        for name, result in summary["dimensions"].items():
            print(f"{name}: {'PASS' if result['passed'] else 'FAIL'} ({result['score']:.4f})")
        print(f"overall: {'PASS' if summary['overall']['passed'] else 'FAIL'} ({summary['overall']['score']:.4f})")
        print(f"canonical_mutation_allowed: {'yes' if summary['canonical_mutation_allowed'] else 'no'}")
        if summary["critical_failures"]:
            print("critical_failures: " + ", ".join(summary["critical_failures"]))
    return 0 if summary["overall"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
