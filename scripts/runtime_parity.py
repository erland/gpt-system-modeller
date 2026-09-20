#!/usr/bin/env python3
"""Render and validate the deterministic multi-runtime parity baseline."""
from pathlib import Path
import argparse
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "gpt-project.yaml"
DIMENSIONS = ["behavior", "capabilities", "artifacts", "workspace_state", "tools"]
RUNTIMES = ["chat", "custom_gpt", "claude", "opencode"]


def load_project():
    data = yaml.safe_load(PROJECT.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("gpt-project.yaml must be a mapping")
    return data


def baseline(project):
    declared = (project.get("build") or {}).get("parity_dimensions") or []
    if declared != DIMENSIONS:
        raise SystemExit(f"parity dimensions must be {DIMENSIONS}")
    result = {"schema_version": "1.0", "dimensions": DIMENSIONS, "runtimes": {}}
    runtimes = project.get("runtimes") or {}
    for runtime_id in RUNTIMES:
        runtime = runtimes.get(runtime_id) or {}
        parity = runtime.get("parity") or {}
        missing = [d for d in DIMENSIONS if d not in parity]
        if missing:
            raise SystemExit(f"{runtime_id}: missing parity dimensions {missing}")
        result["runtimes"][runtime_id] = {
            "enabled": bool(runtime.get("enabled")),
            "compatibility": runtime.get("compatibility"),
            "parity": {d: parity[d] for d in DIMENSIONS},
        }
    return result


def markdown(data):
    lines = [
        "# Runtime parity baseline",
        "",
        "| Runtime | Enabled | Compatibility | Behavior | Capabilities | Artifacts | Workspace/state | Tools |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for runtime_id in RUNTIMES:
        row = data["runtimes"][runtime_id]
        p = row["parity"]
        lines.append(
            f"| {runtime_id} | {'yes' if row['enabled'] else 'no'} | {row['compatibility']} | "
            f"{p['behavior']} | {p['capabilities']} | {p['artifacts']} | "
            f"{p['workspace_state']} | {p['tools']} |"
        )
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=("yaml", "markdown"), default="yaml")
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    data = baseline(load_project())
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True) if ns.format == "yaml" else markdown(data)
    if ns.output:
        ns.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
