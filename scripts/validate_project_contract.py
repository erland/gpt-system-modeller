#!/usr/bin/env python3
"""Lint the canonical GPT project contract and persistent project status."""
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "gpt-project.yaml"
STATUS = ROOT / "project-status.yaml"
RUNTIMES = {"chat", "custom_gpt", "claude", "opencode"}
TOOL_MODES = {"read_only", "mutating", "derived_output"}


def fail(message: str) -> int:
    print(f"Project contract FAILED: {message}")
    return 1


def load(path: Path):
    if not path.is_file():
        raise ValueError(f"missing {path.name}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping")
    return data


def main() -> int:
    try:
        project = load(PROJECT)
        status = load(STATUS)
    except (ValueError, yaml.YAMLError) as exc:
        return fail(str(exc))

    if project.get("schema_version") != "1.0" or status.get("schema_version") != "1.0":
        return fail("schema_version must be 1.0")

    metadata = project.get("project") or {}
    if metadata.get("id") != "system-modeller":
        return fail("project.id must be system-modeller")
    instruction = metadata.get("canonical_instruction")
    if not instruction or not (ROOT / instruction).is_file():
        return fail("canonical instruction must reference an existing file")
    if metadata.get("version_source") != "VERSION":
        return fail("VERSION must remain the development version source")

    contracts = project.get("contracts") or {}
    capabilities = contracts.get("capabilities") or []
    capability_ids = [item.get("id") for item in capabilities if isinstance(item, dict)]
    if len(capability_ids) != len(set(capability_ids)) or not capability_ids:
        return fail("capability IDs must be non-empty and unique")

    workspace = contracts.get("workspace") or {}
    expected_sequence = ["INSPECT", "VALIDATE", "PLAN", "CHANGE", "VALIDATE", "DERIVE", "PACKAGE"]
    if workspace.get("runtime_sequence") != expected_sequence:
        return fail("runtime sequence does not match the canonical Plan B flow")

    tool_ids = set()
    for tool in contracts.get("tools") or []:
        if not isinstance(tool, dict) or not tool.get("id"):
            return fail("every tool must have an id")
        if tool["id"] in tool_ids:
            return fail(f"duplicate tool id {tool['id']}")
        tool_ids.add(tool["id"])
        if tool.get("mode") not in TOOL_MODES:
            return fail(f"invalid mode for tool {tool['id']}")
        if tool.get("capability") not in capability_ids:
            return fail(f"tool {tool['id']} references unknown capability")
        path = tool.get("path")
        if not path or not (ROOT / path).is_file():
            return fail(f"tool {tool['id']} references missing path")
        if tool.get("mode") == "mutating" and tool.get("approval_required") is not True:
            return fail(f"mutating tool {tool['id']} must require approval")

    runtimes = project.get("runtimes") or {}
    if set(runtimes) != RUNTIMES:
        return fail("runtime registry must contain chat, custom_gpt, claude and opencode")
    active = set((project.get("build") or {}).get("active_targets") or [])
    for runtime_id, runtime in runtimes.items():
        enabled = runtime.get("enabled") is True
        if enabled != (runtime_id in active):
            return fail(f"runtime {runtime_id} enabled state must match active_targets")
        pattern = runtime.get("artifact_pattern", "")
        if "{version}" not in pattern:
            return fail(f"runtime {runtime_id} artifact pattern must contain {{version}}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if status.get("version") != version:
        return fail("project-status version must match VERSION")
    if status.get("project") != metadata.get("id"):
        return fail("project-status project must match project.id")
    step = ((status.get("progress") or {}).get("completed_step") or "")
    if not re.fullmatch(r"C[1-7]", step):
        return fail("completed_step must be C1..C7")
    next_step = (status.get("next_step") or {}).get("id")
    if step != "C7" and not re.fullmatch(r"C[2-7]", next_step or ""):
        return fail("in-progress status must declare the next C step")

    print(f"Project contract OK – {metadata['id']} {version}, completed {step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
