#!/usr/bin/env python3
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print("FAIL:", message)
    return 1


def main():
    project = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))

    if project["build"]["active_targets"] != ["chat", "custom_gpt", "claude", "opencode"]:
        return fail("all four runtimes must remain active")
    for runtime_id in ("chat", "custom_gpt", "claude", "opencode"):
        runtime = project["runtimes"][runtime_id]
        if not runtime.get("enabled") or runtime.get("compatibility") != "ready":
            return fail(f"{runtime_id} is not enabled/ready")

    if status["progress"]["completed_step"] != "C7" or status["progress"]["state"] != "complete":
        return fail("Plan C persistent status is not complete")
    if status.get("next_step"):
        return fail("completed Plan C must not declare another Plan C step")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if status.get("version") != version:
        return fail("status/version mismatch")
    if not re.fullmatch(r"0\.1\.0-dev\.(\d+)", version):
        return fail("unexpected development version format")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "Chat ZIP",
        "Custom GPT",
        "Claude Project",
        "OpenCode workspace",
        "scripts/ci_build.py",
        "runtime-parity.yaml",
        "SHA256SUMS.txt",
    ):
        if phrase not in readme:
            return fail("README missing final multi-runtime guidance: " + phrase)
    if "steg A23 av 30" in readme:
        return fail("README still contains obsolete Plan A status")

    subprocess.run([sys.executable, str(ROOT / "scripts/check_structure.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_project_contract.py")], cwd=ROOT, check=True)

    warning_env = os.environ.copy()
    warning_env["PYTHONWARNINGS"] = "error::SyntaxWarning"
    subprocess.run(
        [sys.executable, "-m", "py_compile", str(ROOT / "scripts/package_custom_gpt.py")],
        cwd=ROOT, env=warning_env, check=True,
    )

    with tempfile.TemporaryDirectory() as td:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/release_check.py"), "--output-dir", td],
            cwd=ROOT, text=True, capture_output=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            return fail("final release-readiness failed")
        readiness = yaml.safe_load((Path(td) / "release-readiness.yaml").read_text(encoding="utf-8"))
        if readiness.get("status") != "READY":
            return fail("final release-readiness is not READY")
        if not all((readiness.get("local_checks") or {}).values()):
            return fail("one or more final local readiness checks failed")

    print("C7 final regression and hygiene tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
