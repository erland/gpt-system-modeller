#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print("FAIL:", message)
    return 1


def main():
    workflow = (ROOT / ".github/workflows/build-distributions.yml").read_text(encoding="utf-8")
    required = [
        "name: Build unified project and runtime artifacts",
        "scripts/validate_custom_gpt.py",
        "scripts/validate_claude.py",
        "scripts/validate_opencode.py",
        "name: system-modeller-unified-build",
        "scripts/validate_release_assets_1_5.py",
        "dist/*.zip",
        "dist/runtime-parity.yaml",
        "dist/SHA256SUMS.txt",
        "dist/build-manifest.yaml",
        "gh release upload",
        "--clobber",
    ]
    for phrase in required:
        if phrase not in workflow:
            return fail("workflow missing C6 behavior: " + phrase)

    if workflow.count("contents: write") != 1:
        return fail("write permission must remain isolated to release job")
    if "permissions:\n  contents: read" not in workflow:
        return fail("workflow default must remain read-only")

    release_upload = workflow.split("gh release upload", 1)[1]
    if "assets[@]" not in release_upload:
        return fail("GitHub Release upload must use validated registry-derived asset list")
    if "system-modeller-chat-v*.zip" in release_upload or "system-modeller-opencode-v*.zip" in release_upload:
        return fail("GitHub Release upload must not hardcode runtime wildcard assets")

    doc = (ROOT / "docs/github-actions.md").read_text(encoding="utf-8")
    for phrase in ("system-modeller-unified-build", "Claude Project ZIP", "OpenCode ZIP", "SHA256SUMS.txt", "contents: write"):
        if phrase not in doc:
            return fail("C6 documentation missing " + phrase)

    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))
    match = re.fullmatch(r"C([1-7])", status["progress"]["completed_step"] or "")
    if not match or int(match.group(1)) < 6:
        return fail("persistent status predates C6")

    print("C6 CI/release publication tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
