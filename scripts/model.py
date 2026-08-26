#!/usr/bin/env python3
"""Deterministic basic model operations for System Modeller projects."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
import yaml
from ids import next_id

TYPE_SHARDS = {
    "System": "model/context.yaml", "ExternalSystem": "model/context.yaml", "Actor": "model/context.yaml",
    "Responsibility": "model/functions.yaml", "UseCase": "model/use-cases.yaml", "InformationObject": "model/information.yaml",
    "Subsystem": "model/structure.yaml", "Component": "model/structure.yaml", "Service": "model/structure.yaml",
    "Interface": "model/integrations.yaml", "API": "model/integrations.yaml", "Message": "model/integrations.yaml", "Event": "model/integrations.yaml",
    "DataStore": "model/data-stores.yaml", "RuntimeUnit": "model/deployment.yaml", "DeploymentNode": "model/deployment.yaml", "Environment": "model/deployment.yaml",
    "ArchitectureDecision": "model/decisions.yaml", "Constraint": "model/decisions.yaml",
    "Scenario": "interactions/scenarios.yaml", "Interaction": "interactions/interactions.yaml",
    "Repository": "implementation/repositories.yaml", "Module": "implementation/modules.yaml", "Package": "implementation/packages.yaml", "Class": "implementation/classes.yaml",
    "Endpoint": "implementation/endpoints.yaml", "DatabaseTable": "implementation/database.yaml", "SourceFile": "implementation/source-files.yaml",
    "Source": "sources/sources.yaml", "SourceReference": "sources/references.yaml", "Evidence": "sources/evidence.yaml", "Observation": "sources/observations.yaml",
}


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"elements": [], "relationships": []}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    data.setdefault("elements", [])
    data.setdefault("relationships", [])
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def project_files(project: Path):
    for folder in ("model", "interactions", "implementation", "sources"):
        base = project / folder
        if base.is_dir():
            for pattern in ("*.yaml", "*.yml"):
                yield from sorted(base.rglob(pattern))


def iter_records(project: Path):
    for path in project_files(project):
        data = read_yaml(path)
        for section in ("elements", "relationships"):
            for item in data.get(section, []):
                if isinstance(item, dict):
                    yield path, section, item


def find_by_id(project: Path, object_id: str):
    for path, section, item in iter_records(project):
        if item.get("id") == object_id:
            return path, section, item
    return None


def ensure_unique(project: Path, object_id: str) -> None:
    if find_by_id(project, object_id):
        raise ValueError(f"ID already exists: {object_id}")


def shard_for(project: Path, type_name: str) -> Path:
    rel = TYPE_SHARDS.get(type_name)
    if not rel:
        raise ValueError(f"No canonical shard configured for type: {type_name}")
    return project / rel


def add_element(project: Path, obj: dict[str, Any]) -> dict[str, Any]:
    type_name = obj.get("type")
    if not isinstance(type_name, str):
        raise ValueError("Element requires type")
    if not obj.get("id"):
        obj["id"] = next_id(project, type_name)
    ensure_unique(project, obj["id"])
    path = shard_for(project, type_name)
    data = read_yaml(path)
    data["elements"].append(obj)
    write_yaml(path, data)
    return obj


def update_element(project: Path, object_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    hit = find_by_id(project, object_id)
    if not hit or hit[1] != "elements":
        raise KeyError(object_id)
    path, _, item = hit
    if "id" in patch and patch["id"] != object_id:
        raise ValueError("Stable IDs cannot be changed by update")
    old_type = item.get("type")
    new_type = patch.get("type", old_type)
    if new_type != old_type:
        raise ValueError("Changing element type in place is not supported")
    item.update(patch)
    data = read_yaml(path)
    for i, current in enumerate(data["elements"]):
        if current.get("id") == object_id:
            data["elements"][i] = item
            break
    write_yaml(path, data)
    return item


def references_to(project: Path, object_id: str) -> list[str]:
    refs = []
    for _, section, item in iter_records(project):
        if section == "relationships" and (item.get("source") == object_id or item.get("target") == object_id):
            refs.append(item.get("id", "<relationship>"))
    return refs


def delete_element(project: Path, object_id: str, force: bool = False) -> None:
    refs = references_to(project, object_id)
    if refs and not force:
        raise ValueError(f"Element {object_id} is referenced by relationships: {', '.join(refs)}")
    if force:
        for path in project_files(project):
            data = read_yaml(path)
            original = len(data["relationships"])
            data["relationships"] = [r for r in data["relationships"] if r.get("source") != object_id and r.get("target") != object_id]
            if len(data["relationships"]) != original:
                write_yaml(path, data)
    hit = find_by_id(project, object_id)
    if not hit or hit[1] != "elements":
        raise KeyError(object_id)
    path = hit[0]
    data = read_yaml(path)
    data["elements"] = [e for e in data["elements"] if e.get("id") != object_id]
    write_yaml(path, data)


def add_relationship(project: Path, obj: dict[str, Any]) -> dict[str, Any]:
    for field in ("type", "source", "target"):
        if not obj.get(field):
            raise ValueError(f"Relationship requires {field}")
    if not find_by_id(project, obj["source"]):
        raise ValueError(f"Unknown source: {obj['source']}")
    if not find_by_id(project, obj["target"]):
        raise ValueError(f"Unknown target: {obj['target']}")
    if not obj.get("id"):
        obj["id"] = next_id(project, "Relationship")
    ensure_unique(project, obj["id"])
    path = project / "model" / "relationships.yaml"
    data = read_yaml(path)
    data["relationships"].append(obj)
    write_yaml(path, data)
    return obj


def delete_relationship(project: Path, relationship_id: str) -> None:
    hit = find_by_id(project, relationship_id)
    if not hit or hit[1] != "relationships":
        raise KeyError(relationship_id)
    path = hit[0]
    data = read_yaml(path)
    data["relationships"] = [r for r in data["relationships"] if r.get("id") != relationship_id]
    write_yaml(path, data)


def parse_json_arg(value: str) -> dict[str, Any]:
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("JSON payload must be an object")
    return data


def main() -> int:
    p = argparse.ArgumentParser(description="Basic deterministic System Modeller project operations")
    p.add_argument("project", type=Path)
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("find"); f.add_argument("id")
    l = sub.add_parser("list"); l.add_argument("--type")
    a = sub.add_parser("add"); a.add_argument("--json", required=True)
    u = sub.add_parser("update"); u.add_argument("id"); u.add_argument("--json", required=True)
    d = sub.add_parser("delete"); d.add_argument("id"); d.add_argument("--force", action="store_true")
    ar = sub.add_parser("add-relation"); ar.add_argument("--json", required=True)
    dr = sub.add_parser("delete-relation"); dr.add_argument("id")
    args = p.parse_args(); project = args.project.resolve()
    try:
        if args.command == "find":
            hit = find_by_id(project, args.id)
            if not hit: return 2
            print(yaml.safe_dump(hit[2], allow_unicode=True, sort_keys=False).rstrip())
        elif args.command == "list":
            items = [item for _, section, item in iter_records(project) if section == "elements" and (not args.type or item.get("type") == args.type)]
            print(yaml.safe_dump(items, allow_unicode=True, sort_keys=False).rstrip())
        elif args.command == "add":
            print(yaml.safe_dump(add_element(project, parse_json_arg(args.json)), allow_unicode=True, sort_keys=False).rstrip())
        elif args.command == "update":
            print(yaml.safe_dump(update_element(project, args.id, parse_json_arg(args.json)), allow_unicode=True, sort_keys=False).rstrip())
        elif args.command == "delete": delete_element(project, args.id, args.force)
        elif args.command == "add-relation":
            print(yaml.safe_dump(add_relationship(project, parse_json_arg(args.json)), allow_unicode=True, sort_keys=False).rstrip())
        elif args.command == "delete-relation": delete_relationship(project, args.id)
        return 0
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
