#!/usr/bin/env python3
from pathlib import Path
import json
import re

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "schemas/common.schema.json"
CONTEXT = ROOT / "schemas/context.schema.json"
FUNCTIONS = ROOT / "schemas/functions.schema.json"
META = ROOT / "metamodel/functions.yaml"
DOC = ROOT / "docs/functional-model.md"
EXAMPLE = ROOT / "examples/a06-responsibility-model.yaml"


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    for path in (COMMON, CONTEXT, FUNCTIONS, META, DOC, EXAMPLE):
        if not path.is_file():
            return fail(f"missing A6 artifact: {path.relative_to(ROOT)}")

    common = json.loads(COMMON.read_text(encoding="utf-8"))
    context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    schema = json.loads(FUNCTIONS.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    registry = Registry()
    registry = registry.with_resource(common["$id"], Resource.from_contents(common))
    registry = registry.with_resource(context["$id"], Resource.from_contents(context))
    validator = Draft202012Validator(schema, registry=registry)

    example = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            print("FAIL:", "/".join(str(x) for x in err.path), err.message)
        return 1

    invalid_docs = [
        {
            "elements": [
                {"id":"SYS-000001","type":"System","name":"S","abstraction_level":"conceptual"},
                {"id":"RSP-000001","type":"Responsibility","name":"R","abstraction_level":"logical"}
            ],
            "relationships": []
        },
        {
            "elements": [
                {"id":"SYS-000001","type":"System","name":"S","abstraction_level":"conceptual"},
                {"id":"CMP-000001","type":"Responsibility","name":"R","abstraction_level":"conceptual"}
            ],
            "relationships": []
        },
        {
            "elements": [
                {"id":"SYS-000001","type":"System","name":"S","abstraction_level":"conceptual"},
                {"id":"RSP-000001","type":"Responsibility","name":"R","abstraction_level":"conceptual"}
            ],
            "relationships": [{"id":"REL-000001","type":"groups_use_case","source":"RSP-000001","target":"UC-000001"}]
        }
    ]
    if any(validator.is_valid(doc) for doc in invalid_docs):
        return fail("functions schema accepts an intentionally invalid A6 document")

    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    r = meta.get("element_types", {}).get("Responsibility")
    if not r:
        return fail("A6 metamodel missing Responsibility")
    if r.get("id_prefix") != "RSP" or r.get("abstraction_level") != "conceptual":
        return fail("Responsibility ID prefix or abstraction level differs from A6 contract")
    if "SystemFunction" not in r.get("aliases", []):
        return fail("SystemFunction synonym missing from Responsibility definition")

    rel = meta.get("relationship_types", {}).get("has_responsibility")
    if not rel or ["System", "Responsibility"] not in rel.get("allowed_pairs", []):
        return fail("has_responsibility pair missing from A6 metamodel")
    planned = meta.get("planned_relationships", {})
    if planned.get("groups_use_case", {}).get("introduced_in") != "A7":
        return fail("A6 must defer groups_use_case enforcement to A7")
    active_later = meta.get("active_relationships_from_later_steps", {})
    if planned.get("realized_by", {}).get("introduced_in") != "A10" and active_later.get("realized_by", {}).get("introduced_in") != "A10":
        return fail("A6/A10 realization contract missing")

    doc = DOC.read_text(encoding="utf-8")
    for phrase in ("Responsibility är inte implementation", "Relation till UseCase", "Relation till Component", "Responsibility ska beskriva **vad**, inte **hur**."):
        if phrase not in doc:
            return fail(f"functional-model documentation missing: {phrase}")

    prefixes = yaml.safe_load((ROOT / "metamodel/id-prefixes.yaml").read_text(encoding="utf-8"))["registry"]["reserved"]
    if prefixes.get("RSP") != "Responsibility":
        return fail("RSP prefix is not reserved for Responsibility")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    m = re.fullmatch(r"0\.1\.0-dev\.(\d+)", version)
    if not m or int(m.group(1)) < 6:
        return fail(f"expected Plan A version >= 0.1.0-dev.6, got {version!r}")
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    sm = re.search(r"Completed: A1–A(\d+) / A30", status)
    if not sm or int(sm.group(1)) < 6:
        return fail("STATUS.md does not show A6 or later progress")

    print("A6 Responsibility/SystemFunction model tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
