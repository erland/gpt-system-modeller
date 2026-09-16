#!/usr/bin/env python3
"""Generate and evaluate deterministic small/medium/dense report regression cases."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import yaml

import diagram_complexity
import report
import report_profile
import sequence_diagrams
import view as view_engine
import view_split

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "report-regression" / "cases.yaml"
SPLIT_TYPES = ("functional_information", "logical_component", "integration", "deployment")


def _id(prefix: str, n: int) -> str:
    return f"{prefix}-{n:06d}"


def _element(prefix: str, n: int, typ: str, name: str, level: str) -> dict[str, Any]:
    return {"id": _id(prefix, n), "type": typ, "name": name, "abstraction_level": level, "origin": ["declared"]}


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def build_case(case: dict[str, Any], project: Path) -> None:
    project.mkdir(parents=True, exist_ok=True)
    _write(project / "project.yaml", {"project": {"name": f"Report regression {case['id']}", "description": case["description"]}})

    elements: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    rel_n = 1

    system = _element("SYS", 1, "System", "Regression System", "conceptual")
    actor = _element("ACT", 1, "Actor", "User", "conceptual")
    external = _element("EXT", 1, "ExternalSystem", "External Gateway", "conceptual")
    elements += [system, actor, external]

    components: list[dict[str, Any]] = []
    comp_n = 1
    for s in range(1, int(case["subsystems"]) + 1):
        subsystem = _element("SUB", s, "Subsystem", f"Subsystem {s}", "logical")
        elements.append(subsystem)
        for _ in range(int(case["components_per_subsystem"])):
            comp = _element("CMP", comp_n, "Component", f"Component {comp_n}", "logical")
            comp_n += 1
            components.append(comp)
            elements.append(comp)
            relationships.append({"id": _id("REL", rel_n), "type": "contains", "source": subsystem["id"], "target": comp["id"], "origin": ["declared"]})
            rel_n += 1

    info_n = 1
    for r in range(1, int(case["responsibilities"]) + 1):
        rsp = _element("RSP", r, "Responsibility", f"Responsibility {r}", "conceptual")
        uc = _element("UC", r, "UseCase", f"Use case {r}", "conceptual")
        uc["primary_actor"] = actor["id"]
        uc["responsibility"] = rsp["id"]
        uc["related_information"] = []
        elements += [rsp, uc]
        for _ in range(int(case["information_per_responsibility"])):
            info = _element("INFO", info_n, "InformationObject", f"Information {info_n}", "conceptual")
            info_n += 1
            elements.append(info)
            uc["related_information"].append(info["id"])

    for i in range(1, int(case["integrations"]) + 1):
        api = _element("API", i, "API", f"API {i}", "logical")
        provider = components[(i - 1) % len(components)]["id"]
        api["provider"] = provider
        api["consumers"] = [external["id"]]
        elements.append(api)

    environments: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    runtime_n = 1
    for e in range(1, int(case["environments"]) + 1):
        env = _element("ENV", e, "Environment", f"Environment {e}", "runtime")
        node = _element("NODE", e, "DeploymentNode", f"Node {e}", "runtime")
        environments.append(env); nodes.append(node); elements += [env, node]
        relationships.append({"id": _id("REL", rel_n), "type": "belongs_to", "source": node["id"], "target": env["id"], "origin": ["declared"]}); rel_n += 1
        for _ in range(int(case["runtimes_per_environment"])):
            run = _element("RUN", runtime_n, "RuntimeUnit", f"Runtime {runtime_n}", "runtime")
            elements.append(run)
            relationships.append({"id": _id("REL", rel_n), "type": "deployed_on", "source": run["id"], "target": node["id"], "origin": ["declared"]}); rel_n += 1
            comp = components[(runtime_n - 1) % len(components)]
            relationships.append({"id": _id("REL", rel_n), "type": "realized_as", "source": comp["id"], "target": run["id"], "origin": ["declared"]}); rel_n += 1
            runtime_n += 1

    _write(project / "model" / "regression.yaml", {"elements": elements, "relationships": relationships})

    dynamic: list[dict[str, Any]] = []
    for i in range(1, int(case["interactions"]) + 1):
        scenario = _element("SCN", i, "Scenario", f"Scenario {i}", "conceptual")
        interaction = _element("INT", i, "Interaction", f"Interaction {i}", "logical")
        interaction["scenario"] = scenario["id"]
        interaction["participants"] = [{"ref": actor["id"]}, {"ref": components[(i - 1) % len(components)]["id"]}]
        interaction["messages"] = [{"id": f"IM-{i:06d}", "order": 1, "sender": actor["id"], "receiver": components[(i - 1) % len(components)]["id"], "label": f"Request {i}", "communication_mode": "synchronous"}]
        dynamic += [scenario, interaction]
    _write(project / "interactions" / "regression.yaml", {"elements": dynamic, "relationships": []})


def evaluate_case(case: dict[str, Any], project: Path) -> dict[str, Any]:
    profile = report_profile.load()
    policy = profile["diagrams"]
    rendered = report.architecture_description(project, include_diagrams=True)
    errors: list[str] = []

    for index, title in enumerate(report_profile.section_titles(profile), start=1):
        if f"## {index}. {title}" not in rendered:
            errors.append(f"missing report section: {title}")

    split_count = 0
    view_results = []
    for view_type in SPLIT_TYPES:
        result = view_engine.materialize(project, view_engine.default_definition(view_type))
        split = view_split.split_result(result, policy)
        if split["split"]:
            split_count += 1
        detail_ids = {e["id"] for p in split["parts"] if (p.get("split") or {}).get("role") != "overview" for e in p.get("elements") or []}
        original_ids = {e["id"] for e in result.get("elements") or []}
        if split["split"] and detail_ids != original_ids:
            errors.append(f"{view_type}: split detail parts lost canonical elements")
        for part in split["parts"]:
            measurement = diagram_complexity.measure_result(part, policy)
            if measurement["classification"] != "within_preferred":
                errors.append(f"{view_type}: rendered part exceeds preferred budget")
        view_results.append({"type": view_type, "split": split["split"], "parts": len(split["parts"]), "elements": len(original_ids)})

    minimum = int(case.get("expected_min_split_views", 0))
    if split_count < minimum:
        errors.append(f"expected at least {minimum} split views, got {split_count}")

    seq = sequence_diagrams.materialize(project)
    if len(seq) != int(case["interactions"]):
        errors.append("sequence diagram count does not match Interaction count")
    for item in seq:
        sequences = item["result"].get("sequences") or []
        if len(sequences) != 1:
            errors.append(f"{item['interaction_id']}: sequence diagram is not isolated")
        if f"### {item['title']}" not in rendered:
            errors.append(f"missing sequence heading: {item['title']}")

    return {"id": case["id"], "passed": not errors, "errors": errors, "split_view_count": split_count, "sequence_diagram_count": len(seq), "view_results": view_results, "report_length": len(rendered)}


def run(cases_path: Path = DEFAULT_CASES) -> dict[str, Any]:
    data = yaml.safe_load(cases_path.read_text(encoding="utf-8")) or {}
    cases = data.get("cases") or []
    results = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for case in cases:
            project = root / str(case["id"])
            build_case(case, project)
            results.append(evaluate_case(case, project))
    return {"format": "system-modeller-report-regression-summary-v1", "passed": bool(results) and all(r["passed"] for r in results), "case_count": len(results), "results": results}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run end-to-end architecture report regression cases.")
    ap.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    ap.add_argument("--format", choices=["yaml", "json"], default="yaml")
    ns = ap.parse_args()
    try:
        result = run(ns.cases)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    if ns.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False), end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
