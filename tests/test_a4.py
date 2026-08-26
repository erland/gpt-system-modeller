#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = ROOT / "schemas/common.schema.json"
META_FILE = ROOT / "metamodel/common.yaml"
PREFIX_FILE = ROOT / "metamodel/id-prefixes.yaml"
EXAMPLE_FILE = ROOT / "examples/a04-common-model.yaml"
DOC_FILE = ROOT / "docs/model-format.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    for path in (SCHEMA_FILE, META_FILE, PREFIX_FILE, EXAMPLE_FILE, DOC_FILE):
        if not path.is_file():
            return fail(f"missing A4 artifact: {path.relative_to(ROOT)}")

    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    defs = schema.get("$defs", {})
    for required_def in ("stableId", "abstractionLevel", "modelElement", "relationship"):
        if required_def not in defs:
            return fail(f"common schema missing $defs/{required_def}")

    example = yaml.safe_load(EXAMPLE_FILE.read_text(encoding="utf-8"))
    element_validator = Draft202012Validator({
        "$schema": schema["$schema"],
        "$defs": defs,
        "$ref": "#/$defs/modelElement",
    })
    relationship_validator = Draft202012Validator({
        "$schema": schema["$schema"],
        "$defs": defs,
        "$ref": "#/$defs/relationship",
    })
    errors = []
    for idx, element in enumerate(example.get("elements", [])):
        for err in element_validator.iter_errors(element):
            errors.append(f"elements[{idx}]: {err.message}")
    for idx, rel in enumerate(example.get("relationships", [])):
        for err in relationship_validator.iter_errors(rel):
            errors.append(f"relationships[{idx}]: {err.message}")
    if errors:
        for err in errors:
            print("FAIL:", err)
        return 1

    bad_elements = [
        {"id": "cmp-1", "type": "Component", "name": "X", "abstraction_level": "logical"},
        {"id": "CMP-000001", "type": "component", "name": "X", "abstraction_level": "logical"},
        {"id": "CMP-000001", "type": "Component", "name": "X", "abstraction_level": "wrong"},
    ]
    if any(element_validator.is_valid(x) for x in bad_elements):
        return fail("common element schema accepts an intentionally invalid element")

    bad_relationships = [
        {"id": "REL-1", "type": "uses", "source": "CMP-000001", "target": "CMP-000002"},
        {"id": "REL-000001", "type": "Uses", "source": "CMP-000001", "target": "CMP-000002"},
        {"id": "REL-000001", "type": "uses", "source": "bad", "target": "CMP-000002"},
    ]
    if any(relationship_validator.is_valid(x) for x in bad_relationships):
        return fail("relationship schema accepts an intentionally invalid relationship")

    prefixes = yaml.safe_load(PREFIX_FILE.read_text(encoding="utf-8"))["registry"]["reserved"]
    if prefixes.get("REL") != "Relationship" or prefixes.get("SYS") != "System" or prefixes.get("UC") != "UseCase":
        return fail("ID prefix registry lacks expected core reservations")
    id_re = re.compile(r"^[A-Z][A-Z0-9]{0,9}-[0-9]{6}$")
    for prefix in prefixes:
        if not id_re.match(f"{prefix}-000001"):
            return fail(f"reserved prefix does not fit stable ID pattern: {prefix}")

    meta = yaml.safe_load(META_FILE.read_text(encoding="utf-8"))
    levels = meta.get("abstraction_levels", [])
    if levels != ["conceptual", "logical", "runtime", "implementation"]:
        return fail("metamodel/common.yaml abstraction levels differ from A3")
    required_fields = set(meta["common_element_fields"]["required"])
    if required_fields != {"id", "type", "name", "abstraction_level"}:
        return fail("unexpected A4 required common fields")

    doc = DOC_FILE.read_text(encoding="utf-8")
    for phrase in ("Relationer är förstaklassobjekt", "Stabil ID-strategi", "Extensionsprincip", "JSON Schema"):
        if phrase not in doc:
            return fail(f"model-format documentation missing section: {phrase}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version.startswith("0.1.0-dev."):
        return fail(f"expected Plan A development version, got {version!r}")
    # A4 remains a regression test after later steps; do not require STATUS to stay at A4.

    print("A4 common model/schema tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
