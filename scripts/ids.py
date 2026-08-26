#!/usr/bin/env python3
"""Stable ID allocation for System Modeller projects."""
from __future__ import annotations
import argparse
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "metamodel" / "id-prefixes.yaml"


def load_registry() -> tuple[dict[str, str], int]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    reserved = data.get("registry", {}).get("reserved", {})
    explicit = data.get("prefixes", {})
    mapping = {v: k for k, v in reserved.items()}
    mapping.update(explicit)
    width = int(data.get("registry", {}).get("numeric_width", 6))
    return mapping, width


def yaml_files(project: Path):
    for folder in ("model", "interactions", "implementation", "sources"):
        base = project / folder
        if base.is_dir():
            yield from sorted(base.rglob("*.yaml"))
            yield from sorted(base.rglob("*.yml"))


def collect_ids(project: Path) -> set[str]:
    ids: set[str] = set()
    for path in yaml_files(project):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if isinstance(data, dict):
            for key in ("elements", "relationships", "interactions", "sources", "references", "evidence", "observations"):
                items = data.get(key, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and isinstance(item.get("id"), str):
                            ids.add(item["id"])
    return ids


def next_id(project: Path, type_name: str) -> str:
    mapping, width = load_registry()
    if type_name not in mapping:
        raise ValueError(f"Unknown model type for ID allocation: {type_name}")
    prefix = mapping[type_name]
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    highest = 0
    for existing in collect_ids(project):
        m = pattern.fullmatch(existing)
        if m:
            highest = max(highest, int(m.group(1)))
    return f"{prefix}-{highest + 1:0{width}d}"


def main() -> int:
    p = argparse.ArgumentParser(description="Allocate the next stable ID in a System Modeller project")
    p.add_argument("project", type=Path)
    p.add_argument("--type", required=True, dest="type_name")
    args = p.parse_args()
    print(next_id(args.project.resolve(), args.type_name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
