#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print("FAIL:", message)
    return 1


def main():
    runtime = (ROOT / "instructions" / "chat-runtime.md").read_text(encoding="utf-8")
    for phrase in (
        "Denna instruktion är plattformsneutral",
        "Påstå aldrig att ett verktyg har körts",
        "Om validering inte kan utföras",
        "Systemprojekt kontra runtime-distribution",
    ):
        if phrase not in runtime:
            return fail(f"platform-neutral runtime rule missing: {phrase}")
    if "runtime-instruktion för Chat-ZIP" in runtime:
        return fail("canonical runtime instruction is still Chat-specific")

    project = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
    dims = project["build"]["parity_dimensions"]
    if dims != ["behavior", "capabilities", "artifacts", "workspace_state", "tools"]:
        return fail("unexpected parity dimensions")
    for runtime_id in ("chat", "custom_gpt", "claude", "opencode"):
        parity = project["runtimes"][runtime_id].get("parity") or {}
        if set(parity) != set(dims):
            return fail(f"{runtime_id} parity baseline incomplete")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "runtime_parity.py"), "--format", "yaml"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        return fail(result.stdout + result.stderr)
    rendered = yaml.safe_load(result.stdout)
    if list(rendered["runtimes"]) != ["chat", "custom_gpt", "claude", "opencode"]:
        return fail("parity render order changed")
    if rendered["runtimes"]["claude"]["enabled"] or rendered["runtimes"]["opencode"]["enabled"]:
        return fail("C2 must not activate Claude or OpenCode")

    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))
    if status["progress"]["completed_step"] != "C2" or status["next_step"]["id"] != "C3":
        return fail("persistent status not advanced to C2")

    print("C2 runtime parity tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
