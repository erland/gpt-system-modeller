#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import yaml

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "system-modeller-opencode/"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_distribution(path: Path) -> dict[str, bytes]:
    if path.is_dir():
        return {
            p.relative_to(path).as_posix(): p.read_bytes()
            for p in sorted(path.rglob("*"))
            if p.is_file()
        }
    with ZipFile(path) as zf:
        return {
            name[len(PREFIX):]: zf.read(name)
            for name in zf.namelist()
            if name.startswith(PREFIX) and not name.endswith("/")
        }


def validate(path: Path) -> list[str]:
    files = read_distribution(path)
    errors: list[str] = []
    required = {
        "AGENTS.md",
        "opencode.json",
        ".opencode/runtime-contract.json",
        "manifest.yaml",
        "README.md",
        "VERSION",
    }
    missing = required - set(files)
    if missing:
        errors.append(f"missing required files: {sorted(missing)}")
        return errors

    manifest = yaml.safe_load(files["manifest.yaml"].decode("utf-8")) or {}
    contract = json.loads(files[".opencode/runtime-contract.json"].decode("utf-8"))
    config = json.loads(files["opencode.json"].decode("utf-8"))

    if manifest.get("distribution_type") != "opencode_workspace":
        errors.append("manifest distribution_type must be opencode_workspace")
    if contract.get("runtime") != "opencode":
        errors.append("runtime contract must identify opencode")
    if contract.get("workspace_state") != "ready":
        errors.append("OpenCode workspace_state must be ready")
    if (contract.get("target_project") or {}).get("project_root_argument") != "projectRoot":
        errors.append("runtime contract must expose projectRoot")

    tools = contract.get("tools") or []
    tool_ids = {item.get("id") for item in tools}
    expected = {
        "system_context", "system_validate", "system_model", "system_view",
        "system_report", "system_package", "system_analyze",
    }
    if tool_ids != expected:
        errors.append("runtime tool set differs from declared OpenCode contract")

    for tool in tools:
        tid = tool["id"]
        wrapper = f".opencode/tools/{tid}.ts"
        if wrapper not in files:
            errors.append(f"missing wrapper: {wrapper}")
        expected_permission = "ask" if tool.get("mutates_workspace") else "allow"
        if tool.get("permission") != expected_permission:
            errors.append(f"wrong runtime permission for {tid}")

    permissions = config.get("permissions") or []
    permission_map = {
        (item.get("action"), item.get("resource")): item.get("effect")
        for item in permissions
        if isinstance(item, dict)
    }
    if permission_map.get(("system_model", "*")) != "ask":
        errors.append("system_model must require approval")
    for tid in expected - {"system_model"}:
        if permission_map.get((tid, "*")) != "allow":
            errors.append(f"{tid} must be allowed")
    if permission_map.get(("shell", "*")) != "ask":
        errors.append("shell must require approval")
    if permission_map.get(("edit", "*")) != "ask":
        errors.append("edit must require approval")

    agents = files["AGENTS.md"].decode("utf-8")
    for marker in ("System Modeller", "INSPECT", "VALIDATE", "projectRoot", "canonical"):
        if marker.casefold() not in agents.casefold():
            errors.append(f"AGENTS.md missing marker: {marker}")

    generated = manifest.get("generated") or {}
    for rel, meta in generated.items():
        if rel not in files:
            errors.append(f"manifest references missing generated file: {rel}")
        elif digest(files[rel]) != meta.get("sha256"):
            errors.append(f"generated hash mismatch: {rel}")

    for rel, expected_hash in (manifest.get("source_hashes") or {}).items():
        source = ROOT / rel
        if not source.is_file():
            errors.append(f"source missing: {rel}")
        elif digest(source.read_bytes()) != expected_hash:
            errors.append(f"source hash mismatch: {rel}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--opencode", type=Path, required=True)
    ns = ap.parse_args()
    errors = validate(ns.opencode)
    for error in errors:
        print("ERROR", error)
    print(f"OpenCode validation: errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
