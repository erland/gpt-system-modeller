#!/usr/bin/env python3
"""Validate the System Modeller Custom GPT distribution and Chat parity (A33)."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import sys
from zipfile import ZipFile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import versioning
SPEC = ROOT / "templates" / "custom-gpt-distribution.yaml"
CUSTOM_ROOT = "system-modeller-custom-gpt/"
CHAT_ROOT = "system-modeller/"
MAX_INSTRUCTION_CHARS = 8000
FORBIDDEN_PARTS = {"tests", "scripts", "distributions", "__pycache__", ".pytest_cache"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_zip_map(path: Path, root: str) -> dict[str, bytes]:
    with ZipFile(path) as zf:
        files = {}
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            if not name.startswith(root):
                raise ValueError(f"unexpected ZIP root entry: {name}")
            files[name[len(root):]] = zf.read(name)
    return files


def read_dir_map(path: Path) -> dict[str, bytes]:
    return {
        p.relative_to(path).as_posix(): p.read_bytes()
        for p in sorted(path.rglob("*")) if p.is_file()
    }


def read_distribution(path: Path, root: str) -> dict[str, bytes]:
    if path.is_dir():
        return read_dir_map(path)
    return read_zip_map(path, root)


def text(files: dict[str, bytes], rel: str) -> str:
    if rel not in files:
        raise KeyError(rel)
    return files[rel].decode("utf-8")


def canonical_shared_files(spec: dict) -> list[Path]:
    result: list[Path] = []
    for rel in spec.get("parity_contract", {}).get("shared_model_sources", []):
        p = ROOT / rel
        if p.is_file():
            result.append(p)
        elif p.is_dir():
            result.extend(sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts))
        else:
            raise FileNotFoundError(rel)
    return sorted(set(result), key=lambda p: p.relative_to(ROOT).as_posix())


def validate(custom: Path, chat: Path | None, expected_version: str | None = None) -> tuple[list[dict], dict]:
    findings: list[dict] = []
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    version = expected_version or versioning.resolve().distribution_version

    def add(level: str, code: str, message: str):
        findings.append({"level": level, "code": code, "message": message})

    try:
        cfiles = read_distribution(custom, CUSTOM_ROOT)
    except Exception as exc:
        return [{"level": "ERROR", "code": "CUSTOM_READ", "message": str(exc)}], {}

    required = ["instructions.md", "manifest.yaml"] + [
        f"knowledge/{item['output']}" for item in spec.get("knowledge", [])
    ]
    for rel in required:
        if rel not in cfiles:
            add("ERROR", "CUSTOM_MISSING", f"Missing required Custom GPT file: {rel}")

    for rel in cfiles:
        parts = set(Path(rel).parts)
        if parts & FORBIDDEN_PARTS or rel.endswith((".pyc", ".pyo")):
            add("ERROR", "CUSTOM_FORBIDDEN", f"Forbidden development content: {rel}")

    manifest = {}
    if "manifest.yaml" in cfiles:
        try:
            manifest = yaml.safe_load(text(cfiles, "manifest.yaml")) or {}
        except Exception as exc:
            add("ERROR", "MANIFEST_PARSE", str(exc))

    if manifest.get("version") != version:
        add("ERROR", "VERSION_MISMATCH", f"Custom manifest version {manifest.get('version')!r} != VERSION {version!r}")
    if manifest.get("distribution_type") != "custom_gpt":
        add("ERROR", "DIST_TYPE", "manifest distribution_type must be custom_gpt")

    if "instructions.md" in cfiles:
        inst = text(cfiles, "instructions.md")
        if len(inst) > MAX_INSTRUCTION_CHARS:
            add("ERROR", "INSTRUCTIONS_TOO_LONG", f"instructions.md has {len(inst)} chars; max is {MAX_INSTRUCTION_CHARS}")
        for needle in ["System Modeller", "YAML", "Källanalys", "evidens", "origin", "valider", "vy", "rapport"]:
            if needle.casefold() not in inst.casefold():
                add("ERROR", "INSTRUCTIONS_TOPIC", f"instructions.md lacks required topic marker: {needle}")

    generated = manifest.get("generated", {}) if isinstance(manifest, dict) else {}
    for rel, meta in generated.items():
        if rel not in cfiles:
            add("ERROR", "GENERATED_MISSING", f"Manifest references missing generated file: {rel}")
            continue
        expected = meta.get("sha256") if isinstance(meta, dict) else None
        if expected and digest(cfiles[rel]) != expected:
            add("ERROR", "GENERATED_HASH", f"Generated file hash mismatch: {rel}")

    source_hashes = manifest.get("source_hashes", {}) if isinstance(manifest, dict) else {}
    for rel, expected in source_hashes.items():
        p = ROOT / rel
        if not p.is_file():
            add("ERROR", "SOURCE_MISSING", f"Manifest canonical source no longer exists: {rel}")
        elif digest(p.read_bytes()) != expected:
            add("ERROR", "SOURCE_HASH", f"Canonical source hash mismatch: {rel}")

    shared = canonical_shared_files(spec)
    for p in shared:
        rel = p.relative_to(ROOT).as_posix()
        expected = digest(p.read_bytes())
        if source_hashes.get(rel) != expected:
            add("ERROR", "PARITY_SOURCE_HASH", f"Custom manifest does not trace shared source exactly: {rel}")

    # Knowledge presence/content contract.
    for item in spec.get("knowledge", []):
        rel = f"knowledge/{item['output']}"
        if rel in cfiles and len(cfiles[rel]) < 200:
            add("ERROR", "KNOWLEDGE_EMPTY", f"Knowledge file unexpectedly small: {rel}")

    chat_version = None
    if chat is not None:
        try:
            hfiles = read_distribution(chat, CHAT_ROOT)
        except Exception as exc:
            add("ERROR", "CHAT_READ", str(exc))
            hfiles = {}
        if "VERSION" not in hfiles:
            add("ERROR", "CHAT_VERSION_MISSING", "Chat distribution lacks VERSION")
        else:
            chat_version = hfiles["VERSION"].decode("utf-8").strip()
            if chat_version != version:
                add("ERROR", "CHAT_VERSION_MISMATCH", f"Chat VERSION {chat_version!r} != repository VERSION {version!r}")
        for p in shared:
            rel = p.relative_to(ROOT).as_posix()
            if rel not in hfiles:
                add("ERROR", "CHAT_PARITY_MISSING", f"Chat distribution lacks shared model source: {rel}")
            elif hfiles[rel] != p.read_bytes():
                add("ERROR", "CHAT_PARITY_HASH", f"Chat shared source differs from repository: {rel}")

    # Capability parity is defined by the declarative contract and source coverage.
    capabilities = spec.get("parity_contract", {}).get("shared_capabilities", [])
    if len(capabilities) < 8:
        add("ERROR", "CAPABILITY_CONTRACT", "Shared capability contract is incomplete")

    summary = {
        "repository_version": version,
        "custom_version": manifest.get("version") if isinstance(manifest, dict) else None,
        "chat_version": chat_version,
        "instruction_chars": len(text(cfiles, "instructions.md")) if "instructions.md" in cfiles else None,
        "knowledge_files": len([x for x in cfiles if x.startswith("knowledge/")]),
        "shared_sources": len(shared),
        "shared_capabilities": capabilities,
        "errors": sum(1 for f in findings if f["level"] == "ERROR"),
        "warnings": sum(1 for f in findings if f["level"] == "WARNING"),
    }
    return findings, summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--custom", type=Path, required=True, help="Custom GPT ZIP or materialized directory")
    ap.add_argument("--chat", type=Path, help="Chat ZIP or materialized directory for parity validation")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    ap.add_argument("--expected-version", help="Expected distribution version; tag-derived in release CI")
    ns = ap.parse_args()
    expected = versioning.normalize_distribution_version(ns.expected_version) if ns.expected_version else versioning.resolve().distribution_version
    findings, summary = validate(ns.custom, ns.chat, expected)
    if ns.json:
        print(json.dumps({"summary": summary, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"{f['level']} {f['code']}: {f['message']}")
        print(
            f"Custom GPT validation: errors={summary.get('errors', 0)} "
            f"warnings={summary.get('warnings', 0)} "
            f"instructions={summary.get('instruction_chars')} chars "
            f"knowledge={summary.get('knowledge_files')} shared_sources={summary.get('shared_sources')}"
        )
    return 1 if any(f["level"] == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
