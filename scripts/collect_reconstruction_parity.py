#!/usr/bin/env python3
"""Collect reproducible file-parity evidence, never auto-certify runtime behavior."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import yaml

RUNTIME_INSTRUCTIONS = {
    "chat": "assistant/instructions.md",
    "claude": "project/instructions.md",
    "opencode": "AGENTS.md",
    "plugin": "skills/assistant/SKILL.md",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect(root: Path) -> dict:
    root = root.resolve()
    cfg = yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8"))
    recovery = cfg.get("reconstruction")
    if not isinstance(recovery, dict) or recovery.get("release_ready") is not False:
        raise ValueError("Expected a blocked reconstructed project")
    draft = json.loads((root / "reconstructed-canonical/project-draft.json").read_text(encoding="utf-8"))
    source = root / "src/instructions/system.md"
    if not source.is_file():
        raise ValueError("Missing canonical instruction")
    canonical = source.read_bytes()
    original = root / draft["instruction"]
    recovered_equal = original.is_file() and original.read_bytes() == canonical
    results = {}
    for runtime, instruction_path in RUNTIME_INSTRUCTIONS.items():
        target = root / "build" / runtime / instruction_path
        if not target.is_file():
            results[runtime] = {"status": "not_tested", "reason": "No matching built instruction to inspect"}
        else:
            results[runtime] = {
                "status": "matching_bytes" if target.read_bytes() == canonical else "mismatch",
                "instruction_path": target.relative_to(root).as_posix(),
                "sha256": sha(target.read_bytes()),
            }
    knowledge = []
    for name in draft.get("knowledge_candidates", []):
        path = root / name
        knowledge.append({"source": name, "present": path.is_file(),
                          "sha256": sha(path.read_bytes()) if path.is_file() else None})
    unresolved = {
        "tool_candidates": draft.get("tool_candidates", []),
        "integration_candidates": draft.get("integration_candidates", []),
        "knowledge_files": [item["source"] for item in knowledge if not item["present"]],
    }
    return {
        "result": "evidence_collected",
        "source_instruction": draft.get("source_instruction"),
        "canonical_sha256": sha(canonical),
        "recovered_instruction_matches": recovered_equal,
        "runtimes": results,
        "knowledge": knowledge,
        "unresolved_dependencies": unresolved,
        "automated_runtime_parity_verified": False,
        "release_ready": False,
        "limitations": [
            "Matching instruction bytes are not evidence of identical runtime behavior.",
            "Tool installation, actual execution, Knowledge completeness and runtime adaptation need separate checks.",
            "Plugin SKILL.md may intentionally contain adapter content instead of byte-identical canonical instructions.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    try:
        report = inspect(Path(args.project_root))
    except (ValueError, OSError, KeyError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"Parity evidence failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["recovered_instruction_matches"] or any(
        v["status"] == "mismatch" for v in report["runtimes"].values()
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
