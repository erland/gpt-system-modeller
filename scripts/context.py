#!/usr/bin/env python3
"""Generate a compact deterministic working context for a System Modeller project."""
from __future__ import annotations
import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml
import model
import validate

CANONICAL_FOLDERS = ("model", "interactions", "implementation", "sources")


def load_manifest(project: Path) -> dict[str, Any]:
    path = project / "project.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def norm_origin(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    return [x for x in (value or []) if isinstance(x, str)]


def norm_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    return [x for x in (value or []) if isinstance(x, str)]


def inventory(project: Path):
    elements = []
    relationships = []
    files: dict[str, dict[str, Any]] = {}
    element_file: dict[str, str] = {}

    for path, section, item in model.iter_records(project):
        rel = path.relative_to(project).as_posix()
        stats = files.setdefault(rel, {"elements": 0, "relationships": 0, "types": Counter()})
        if section == "elements":
            elements.append(item)
            stats["elements"] += 1
            stats["types"][item.get("type", "Unknown")] += 1
            if item.get("id"):
                element_file[item["id"]] = rel
        else:
            relationships.append(item)
            stats["relationships"] += 1

    file_rows = []
    for rel in sorted(files):
        stats = files[rel]
        file_rows.append({
            "path": rel,
            "elements": stats["elements"],
            "relationships": stats["relationships"],
            "types": dict(sorted(stats["types"].items())),
        })
    return elements, relationships, file_rows, element_file


def validation_summary(project: Path, limit: int) -> dict[str, Any]:
    findings = validate.validate(project)
    counts = Counter(f.severity for f in findings)
    relevant = [asdict(f) for f in findings if f.severity != "INFO"][:limit]
    return {
        "status": "invalid" if counts["ERROR"] else "valid",
        "errors": counts["ERROR"],
        "warnings": counts["WARNING"],
        "findings": relevant,
        "truncated": max(0, len([f for f in findings if f.severity != "INFO"]) - len(relevant)),
    }


def uncertainty_summary(elements, relationships, limit: int) -> dict[str, Any]:
    rows = []
    counts = Counter()
    for item, kind in [(x, "element") for x in elements] + [(x, "relationship") for x in relationships]:
        origins = norm_origin(item.get("origin"))
        evidence = norm_refs(item.get("evidence"))
        reasons = []
        if "unresolved" in origins:
            reasons.append("unresolved")
        if "inferred" in origins:
            reasons.append("inferred")
        if not evidence:
            reasons.append("no_evidence")
        if not reasons:
            continue
        for reason in reasons:
            counts[reason] += 1
        rows.append({
            "id": item.get("id"),
            "kind": kind,
            "type": item.get("type"),
            "name": item.get("name") or item.get("type"),
            "reasons": reasons,
        })
    rows.sort(key=lambda x: (x.get("kind") or "", x.get("type") or "", x.get("id") or ""))
    return {
        "counts": dict(sorted(counts.items())),
        "items": rows[:limit],
        "truncated": max(0, len(rows) - min(limit, len(rows))),
    }


def duplicate_candidates(elements, limit: int) -> list[dict[str, Any]]:
    groups = defaultdict(list)
    for e in elements:
        name = str(e.get("name") or "").strip().casefold()
        typ = e.get("type") or "Unknown"
        if name:
            groups[(typ, name)].append(e)
    rows = []
    for (typ, name), items in sorted(groups.items()):
        if len(items) > 1:
            rows.append({
                "type": typ,
                "normalized_name": name,
                "ids": sorted(x.get("id") for x in items if x.get("id")),
            })
    return rows[:limit]


def focus_rows(elements, element_file, terms: list[str], limit: int) -> list[dict[str, Any]]:
    if not terms:
        return []
    needles = [x.casefold() for x in terms]
    rows = []
    for e in elements:
        hay = " ".join(str(e.get(k) or "") for k in ("id", "type", "name", "description")).casefold()
        if all(n in hay for n in needles):
            rows.append({
                "id": e.get("id"),
                "type": e.get("type"),
                "name": e.get("name"),
                "file": element_file.get(e.get("id")),
                "origin": norm_origin(e.get("origin")),
                "evidence": norm_refs(e.get("evidence")),
            })
    rows.sort(key=lambda x: (x.get("type") or "", x.get("name") or "", x.get("id") or ""))
    return rows[:limit]


def build_context(project: Path, focus: list[str] | None = None, limit: int = 20) -> dict[str, Any]:
    project = project.resolve()
    manifest = load_manifest(project)
    elements, relationships, files, element_file = inventory(project)
    type_counts = Counter(e.get("type", "Unknown") for e in elements)
    rel_counts = Counter(r.get("type", "Unknown") for r in relationships)
    proj = manifest.get("project") if isinstance(manifest.get("project"), dict) else {}

    return {
        "context_format": "system-modeller-working-context-v1",
        "project": {
            "id": proj.get("id"),
            "name": proj.get("name"),
            "description": proj.get("description"),
            "schema_version": proj.get("schema_version"),
            "model_version": proj.get("model_version"),
            "language": proj.get("language"),
        },
        "summary": {
            "element_count": len(elements),
            "relationship_count": len(relationships),
            "element_types": dict(sorted(type_counts.items())),
            "relationship_types": dict(sorted(rel_counts.items())),
        },
        "validation": validation_summary(project, limit),
        "canonical_files": files,
        "uncertainty": uncertainty_summary(elements, relationships, limit),
        "duplicate_name_candidates": duplicate_candidates(elements, limit),
        "focus": {
            "terms": focus or [],
            "matches": focus_rows(elements, element_file, focus or [], limit),
        },
        "runtime_contract": {
            "next_operations": ["INSPECT", "VALIDATE", "PLAN", "CHANGE", "VALIDATE", "DERIVE", "PACKAGE"],
            "canonical_source": "project.yaml + canonical YAML shards",
            "derived_artifacts_are_not_source": True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate compact deterministic LLM working context")
    ap.add_argument("project", type=Path)
    ap.add_argument("--focus", action="append", default=[], help="Narrow relevant elements; repeatable")
    ap.add_argument("--limit", type=int, default=20, help="Maximum findings/items per compact section")
    ap.add_argument("--format", choices=("yaml", "json"), default="yaml")
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    if ns.limit < 1:
        print("ERROR: --limit must be >= 1")
        return 2
    try:
        data = build_context(ns.project, ns.focus, ns.limit)
    except Exception as e:
        print(f"ERROR: {e}")
        return 2
    text = (json.dumps(data, ensure_ascii=False, indent=2) + "\n") if ns.format == "json" else yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if data["validation"]["status"] == "invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
