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
USE_CASES = ROOT / "schemas/use-cases.schema.json"
META = ROOT / "metamodel/use-cases.yaml"
DOC = ROOT / "docs/use-case-model.md"
EXAMPLE = ROOT / "examples/a07-use-case-model.yaml"


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    for path in (COMMON, CONTEXT, FUNCTIONS, USE_CASES, META, DOC, EXAMPLE):
        if not path.is_file():
            return fail(f"missing A7 artifact: {path.relative_to(ROOT)}")

    schemas = [json.loads(p.read_text(encoding="utf-8")) for p in (COMMON, CONTEXT, FUNCTIONS, USE_CASES)]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    registry = Registry()
    for schema in schemas[:-1]:
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    validator = Draft202012Validator(schemas[-1], registry=registry)

    example = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            print("FAIL:", "/".join(str(x) for x in err.path), err.message)
        return 1

    invalid = {
        "elements": [
            {"id":"SYS-000001","type":"System","name":"S","abstraction_level":"conceptual"},
            {"id":"UC-000001","type":"UseCase","name":"U","abstraction_level":"conceptual",
             "primary_actor":"ACT-000001","responsibility":"RSP-000001"}
        ],
        "relationships": []
    }
    if validator.is_valid(invalid):
        return fail("UseCase without outcome was accepted")

    wrong_actor = {
        "elements": [
            {"id":"SYS-000001","type":"System","name":"S","abstraction_level":"conceptual"},
            {"id":"UC-000001","type":"UseCase","name":"U","abstraction_level":"conceptual",
             "primary_actor":"SYS-000001","responsibility":"RSP-000001","outcome":"Done"}
        ],
        "relationships": []
    }
    if validator.is_valid(wrong_actor):
        return fail("UseCase accepted non-ACT primary_actor")

    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    uc = meta.get("element_types", {}).get("UseCase")
    if not uc or uc.get("id_prefix") != "UC" or uc.get("abstraction_level") != "conceptual":
        return fail("UseCase metamodel contract missing or incorrect")
    if set(uc.get("required_fields", [])) != {"primary_actor", "responsibility", "outcome"}:
        return fail("UseCase required fields differ from A7 contract")

    rels = meta.get("relationship_types", {})
    expected = {
        "performs": ["Actor", "UseCase"],
        "groups_use_case": ["Responsibility", "UseCase"],
        "includes": ["UseCase", "UseCase"],
        "extends": ["UseCase", "UseCase"],
        "specializes": ["UseCase", "UseCase"]
    }
    for name, pair in expected.items():
        if pair not in rels.get(name, {}).get("allowed_pairs", []):
            return fail(f"missing A7 relationship contract: {name} {pair}")

    doc = DOC.read_text(encoding="utf-8")
    for phrase in ("Endpoint = UseCase", "Relation till Actor", "Relation till Responsibility", "Include och extend"):
        if phrase not in doc:
            return fail(f"use-case documentation missing: {phrase}")

    prefixes = yaml.safe_load((ROOT / "metamodel/id-prefixes.yaml").read_text(encoding="utf-8"))["registry"]["reserved"]
    if prefixes.get("UC") != "UseCase":
        return fail("UC prefix is not reserved for UseCase")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    m = re.fullmatch(r"0\.1\.0-dev\.(\d+)", version)
    if not m or int(m.group(1)) < 7:
        return fail(f"expected Plan A version >= 0.1.0-dev.7, got {version!r}")
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    sm = re.search(r"Completed: A1–A(\d+) / A30", status)
    if not sm or int(sm.group(1)) < 7:
        return fail("STATUS.md not advanced to A7 or later")

    print("A7 UseCase model tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
