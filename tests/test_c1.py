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
    for rel in ("gpt-project.yaml", "project-status.yaml", "scripts/validate_project_contract.py"):
        if not (ROOT / rel).is_file():
            return fail(f"missing C1 artifact {rel}")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_project_contract.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return fail(result.stdout + result.stderr)

    project = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))

    if set(project["runtimes"]) != {"chat", "custom_gpt", "claude", "opencode"}:
        return fail("runtime registry incomplete")
    if project["build"]["active_targets"] != ["chat", "custom_gpt"]:
        return fail("C1 must not activate new runtime builds")
    if status["progress"]["completed_step"] != "C1" or status["next_step"]["id"] != "C2":
        return fail("persistent status does not advance correctly")
    if status["version"] != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
        return fail("status and VERSION differ")

    mutating = [t for t in project["contracts"]["tools"] if t["mode"] == "mutating"]
    if not mutating or not all(t.get("approval_required") is True for t in mutating):
        return fail("mutating tools must explicitly require approval")

    print("C1 project contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
