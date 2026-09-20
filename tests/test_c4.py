#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print("FAIL:", message)
    return 1


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    for rel in (
        "templates/opencode-distribution.yaml",
        "scripts/package_opencode.py",
        "scripts/validate_opencode.py",
        "docs/opencode-distribution.md",
    ):
        if not (ROOT / rel).is_file():
            return fail("missing C4 artifact " + rel)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        first = td / "one.zip"
        second = td / "two.zip"
        tree = td / "tree"
        subprocess.run(
            ["python3", str(ROOT / "scripts/package_opencode.py"), "--output", str(first), "--directory", str(tree)],
            check=True, cwd=ROOT,
        )
        subprocess.run(
            ["python3", str(ROOT / "scripts/package_opencode.py"), "--output", str(second)],
            check=True, cwd=ROOT,
        )
        if digest(first) != digest(second):
            return fail("OpenCode ZIP is not deterministic")
        subprocess.run(
            ["python3", str(ROOT / "scripts/validate_opencode.py"), "--opencode", str(first)],
            check=True, cwd=ROOT,
        )

        config = json.loads((tree / "opencode.json").read_text(encoding="utf-8"))
        rules = {
            (x.get("action"), x.get("resource")): x.get("effect")
            for x in config["permissions"]
        }
        if rules.get(("system_model", "*")) != "ask":
            return fail("mutating model tool must require approval")
        if rules.get(("system_validate", "*")) != "allow":
            return fail("validation tool should be allowed")
        if rules.get(("shell", "*")) != "ask" or rules.get(("edit", "*")) != "ask":
            return fail("generic shell/edit must require approval")

        contract = json.loads((tree / ".opencode/runtime-contract.json").read_text(encoding="utf-8"))
        if contract["target_project"]["project_root_argument"] != "projectRoot":
            return fail("projectRoot contract missing")
        wrapper = (tree / ".opencode/tools/system_model.ts").read_text(encoding="utf-8")
        if "Bun.spawn" not in wrapper or "tool.schema.enum" not in wrapper:
            return fail("model wrapper is not typed/restricted")
        if "command: tool.schema.string()" in wrapper:
            return fail("model wrapper exposes an unrestricted command")

    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))
    match = re.fullmatch(r"C([1-7])", status["progress"]["completed_step"] or "")
    if not match or int(match.group(1)) < 4:
        return fail("persistent status predates C4")

    print("C4 OpenCode distribution tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
