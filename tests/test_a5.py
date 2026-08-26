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
META = ROOT / "metamodel/context.yaml"
DOC = ROOT / "docs/context-model.md"
EXAMPLE = ROOT / "examples/a05-context-model.yaml"


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    for path in (COMMON, CONTEXT, META, DOC, EXAMPLE):
        if not path.is_file():
            return fail(f"missing A5 artifact: {path.relative_to(ROOT)}")

    common = json.loads(COMMON.read_text(encoding="utf-8"))
    schema = json.loads(CONTEXT.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    registry = Registry().with_resource(common["$id"], Resource.from_contents(common))
    validator = Draft202012Validator(schema, registry=registry)
    example = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            print("FAIL:", "/".join(str(x) for x in err.path), err.message)
        return 1

    # Domain-specific schema constraints.
    invalid_docs = [
        {
            "elements": [{"id": "ACT-000001", "type": "Actor", "name": "A", "abstraction_level": "conceptual", "actor_kind": "role"}],
            "relationships": [],
        },
        {
            "elements": [
                {"id": "SYS-000001", "type": "System", "name": "S1", "abstraction_level": "conceptual"},
                {"id": "SYS-000002", "type": "System", "name": "S2", "abstraction_level": "conceptual"}
            ],
            "relationships": [],
        },
        {
            "elements": [{"id": "ACT-000001", "type": "Actor", "name": "A", "abstraction_level": "conceptual"}],
            "relationships": [],
        },
        {
            "elements": [{"id": "SYS-000001", "type": "System", "name": "S", "abstraction_level": "logical"}],
            "relationships": [],
        },
        {
            "elements": [{"id": "EXT-000001", "type": "ExternalSystem", "name": "E", "abstraction_level": "conceptual"}],
            "relationships": [{"id": "REL-000001", "type": "depends_on", "source": "EXT-000001", "target": "EXT-000001"}],
        },
    ]
    if any(validator.is_valid(doc) for doc in invalid_docs):
        return fail("context schema accepts an intentionally invalid A5 document")

    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    types = meta.get("element_types", {})
    if set(types) != {"System", "ExternalSystem", "Actor"}:
        return fail("A5 metamodel does not define exactly the expected context element types")
    if types["Actor"].get("actor_kinds") != ["person", "role", "organization", "external_technical_actor"]:
        return fail("Actor kinds differ from A5 contract")

    rels = meta.get("relationship_types", {})
    for rel in ("uses", "interacts_with", "exchanges_information_with"):
        if rel not in rels:
            return fail(f"A5 metamodel missing relationship type: {rel}")

    text = DOC.read_text(encoding="utf-8")
    for phrase in ("Systemgränsen styr klassificeringen", "Undvik dubbletter", "ExternalSystem", "Actor"):
        if phrase not in text:
            return fail(f"context-model documentation missing: {phrase}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    m = re.fullmatch(r"0\.1\.0-dev\.(\d+)", version)
    if not m or int(m.group(1)) < 5:
        return fail(f"expected Plan A version >= 0.1.0-dev.5, got {version!r}")
    # A5 remains a regression test after later steps; do not require STATUS to stay at A5.

    print("A5 context model/schema tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
