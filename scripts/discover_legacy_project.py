#!/usr/bin/env python3
"""Structure-agnostic, evidence-only discovery of older GPT projects.

This stage never infers unproven canonical contracts or activates runtimes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

SKIP = {".git", "build", "dist", "__pycache__", ".pytest_cache"}
INSTRUCTION_NAMES = {"instructions.md", "system.md", "agents.md", "skill.md", "prompt.md"}
KNOWLEDGE_PARTS = {"knowledge", "references", "assets", "docs", "documents"}
TOOL_SUFFIXES = {".py", ".js", ".ts", ".sh"}
MAX_FILES = 5000


def discover(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("Input must be an extracted project directory")
    files = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP for part in relative.parts) or not path.is_file():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Unsafe file path: {relative}")
        if len(files) >= MAX_FILES:
            raise ValueError("Too many source files")
        content = path.read_bytes()
        rel = relative.as_posix()
        kinds = []
        if path.name.lower() in INSTRUCTION_NAMES:
            kinds.append("instruction_candidate")
        if any(part.lower() in KNOWLEDGE_PARTS for part in relative.parts[:-1]):
            kinds.append("knowledge_candidate")
        if path.suffix.lower() in TOOL_SUFFIXES:
            kinds.append("script_candidate")
        if path.suffix.lower() in {".yaml", ".yml", ".json", ".toml"}:
            kinds.append("configuration_candidate")
        files.append({
            "path": rel,
            "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content),
            "candidate_roles": kinds,
        })
    candidates = {role: [f["path"] for f in files if role in f["candidate_roles"]]
                  for role in ("instruction_candidate", "knowledge_candidate",
                               "script_candidate", "configuration_candidate")}
    return {
        "schema_version": 1,
        "status": "analysis_required",
        "source_files": files,
        "candidates": candidates,
        "analysis_contract": {
            "purpose": "Classify project behavior, knowledge, dependencies and workflows based on evidence",
            "evidence_rule": "Every proposed fact must cite a source_files.path and SHA-256",
            "uncertainty_rule": "Mark unresolved source ambiguity for review; do not invent behavior",
            "output": "platform-neutral reviewed project model before runtime configuration",
        },
        "release_ready": False,
        "runtime_activated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = discover(Path(args.project_root))
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            target = Path(args.output)
            if target.exists():
                raise FileExistsError(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, ValueError) as exc:
        print(f"Generic discovery blocked: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
