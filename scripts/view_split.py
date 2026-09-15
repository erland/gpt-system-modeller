#!/usr/bin/env python3
"""Deterministically split oversized materialized architecture views into readable parts."""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any

import diagram_complexity

SUPPORTED_VIEW_TYPES = {
    "logical_component",
    "integration",
    "deployment",
    "functional_information",
}

ANCHOR_TYPES = {
    "logical_component": ("Subsystem",),
    "functional_information": ("Responsibility",),
    "deployment": ("Environment", "DeploymentNode"),
    "integration": ("System", "ExternalSystem", "Component", "Service"),
}

PROVIDER_RELATIONS = {
    "provides_interface", "exposes", "sends", "publishes", "exchanges_information_with"
}


def _elements_by_id(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {e["id"]: e for e in result.get("elements") or [] if e.get("id")}


def _links(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in result.get("links") or [] if r.get("source") and r.get("target")]


def _adjacency(result: dict[str, Any]) -> dict[str, set[str]]:
    adj = {eid: set() for eid in _elements_by_id(result)}
    for link in _links(result):
        a, b = link["source"], link["target"]
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    return adj


def _anchor_ids(result: dict[str, Any]) -> list[str]:
    view_type = (result.get("view") or {}).get("type")
    elements = _elements_by_id(result)
    if view_type == "integration":
        providers = {
            r["source"] for r in _links(result)
            if r.get("type") in PROVIDER_RELATIONS and r.get("source") in elements
        }
        typed = [eid for eid in providers if elements[eid].get("type") in ANCHOR_TYPES[view_type]]
        if typed:
            return sorted(typed)
    for anchor_type in ANCHOR_TYPES.get(view_type, ()):
        ids = sorted(eid for eid, e in elements.items() if e.get("type") == anchor_type)
        if ids:
            return ids
    return []


def _nearest_anchor_groups(result: dict[str, Any], anchors: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    adj = _adjacency(result)
    groups = {anchor: [anchor] for anchor in anchors}
    unassigned: list[str] = []
    for eid in sorted(adj):
        if eid in groups:
            continue
        queue = deque([(eid, 0)])
        seen = {eid}
        found: list[tuple[int, str]] = []
        best_distance: int | None = None
        while queue:
            node, distance = queue.popleft()
            if best_distance is not None and distance > best_distance:
                break
            if node in groups:
                found.append((distance, node))
                best_distance = distance
                continue
            for nxt in sorted(adj.get(node, ())):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, distance + 1))
        if found:
            anchor = min(found)[1]
            groups[anchor].append(eid)
        else:
            unassigned.append(eid)
    for ids in groups.values():
        ids.sort()
    return groups, unassigned


def _internal_link_count(result: dict[str, Any], ids: set[str]) -> int:
    return sum(1 for r in _links(result) if r["source"] in ids and r["target"] in ids)


def _greedy_chunks(result: dict[str, Any], ids: list[str], policy: dict[str, Any], pinned: str | None = None) -> list[list[str]]:
    max_elements = int(policy["preferred_max_elements"])
    max_links = int(policy["preferred_max_relationships"])
    ordered = [eid for eid in sorted(set(ids)) if eid != pinned]
    chunks: list[list[str]] = []
    current = [pinned] if pinned else []
    for eid in ordered:
        candidate = current + [eid]
        if current and (len(candidate) > max_elements or _internal_link_count(result, set(candidate)) > max_links):
            chunks.append(current)
            current = ([pinned] if pinned else []) + [eid]
        else:
            current = candidate
    if current and (not pinned or len(current) > 1 or not chunks):
        chunks.append(current)
    return chunks


def _induced(result: dict[str, Any], ids: list[str], title: str, role: str, index: int) -> dict[str, Any]:
    selected = set(ids)
    elements = [deepcopy(e) for e in result.get("elements") or [] if e.get("id") in selected]
    links = [deepcopy(r) for r in result.get("links") or [] if r.get("source") in selected and r.get("target") in selected]
    out = {
        "view": deepcopy(result.get("view") or {}),
        "elements": elements,
        "links": links,
        "summary": {
            "element_count": len(elements),
            "link_count": len(links),
            "derived_link_count": sum(bool(r.get("derived")) for r in links),
        },
        "split": {"role": role, "index": index, "title": title},
    }
    return out


def split_result(result: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    measurement = diagram_complexity.measure_result(result, policy)
    view_type = measurement.get("view_type")
    if view_type not in SUPPORTED_VIEW_TYPES or not measurement["split_recommended"]:
        return {"split": False, "measurement": measurement, "parts": [result]}

    elements = _elements_by_id(result)
    anchors = _anchor_ids(result)
    detail_specs: list[tuple[str, list[str]]] = []

    if anchors:
        groups, unassigned = _nearest_anchor_groups(result, anchors)
        for anchor in anchors:
            anchor_name = elements[anchor].get("name") or anchor
            chunks = _greedy_chunks(result, groups[anchor], policy, pinned=anchor)
            for pos, chunk in enumerate(chunks, start=1):
                suffix = f" – del {pos}" if len(chunks) > 1 else ""
                detail_specs.append((f"{anchor_name}{suffix}", chunk))
        if unassigned:
            fallback = _greedy_chunks(result, unassigned, policy)
            for pos, chunk in enumerate(fallback, start=1):
                detail_specs.append((f"Övrigt – del {pos}", chunk))
    else:
        for pos, chunk in enumerate(_greedy_chunks(result, sorted(elements), policy), start=1):
            detail_specs.append((f"Del {pos}", chunk))

    # Overview uses semantic anchors when available, otherwise one stable representative per detail part.
    overview_ids = anchors if anchors else [ids[0] for _, ids in detail_specs if ids]
    overview_chunks = _greedy_chunks(result, overview_ids, policy)
    parts: list[dict[str, Any]] = []
    for pos, ids in enumerate(overview_chunks, start=1):
        title = "Översikt" if len(overview_chunks) == 1 else f"Översikt – del {pos}"
        parts.append(_induced(result, ids, title, "overview", len(parts) + 1))
    for title, ids in detail_specs:
        parts.append(_induced(result, ids, title, "detail", len(parts) + 1))

    return {
        "split": True,
        "measurement": measurement,
        "strategy": "semantic_anchors" if anchors else "stable_id_fallback",
        "anchors": anchors,
        "parts": parts,
    }
