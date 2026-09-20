#!/usr/bin/env python3
from pathlib import Path
import hashlib
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
    project = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
    expected_targets = ["chat", "custom_gpt", "claude", "opencode"]
    if project["build"]["active_targets"] != expected_targets:
        return fail("all four runtimes must be active in C5")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    release = version.split("-dev.", 1)[0]

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "dist"
        subprocess.run(
            ["python3", str(ROOT / "scripts/ci_build.py"), "--output-dir", str(out)],
            cwd=ROOT, check=True,
        )
        expected = {
            "project": f"system-modeller-project-v{release}.zip",
            "chat": f"system-modeller-chat-v{release}.zip",
            "custom_gpt": f"system-modeller-custom-gpt-v{release}.zip",
            "claude": f"system-modeller-claude-v{release}.zip",
            "opencode": f"system-modeller-opencode-v{release}.zip",
            "runtime_parity": "runtime-parity.yaml",
            "checksums": "SHA256SUMS.txt",
        }
        for name in expected.values():
            if not (out / name).is_file():
                return fail("unified build missing " + name)

        manifest = yaml.safe_load((out / "build-manifest.yaml").read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 2:
            return fail("unified build manifest schema must be 2")
        artifacts = {item["type"]: item for item in manifest.get("artifacts", [])}
        for typ, name in expected.items():
            if typ not in artifacts:
                return fail("manifest missing artifact " + typ)
            if artifacts[typ]["file"] != name:
                return fail("manifest filename mismatch " + typ)
            if artifacts[typ]["sha256"] != digest(out / name):
                return fail("manifest checksum mismatch " + typ)

        lines = (out / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        sums = dict(line.split("  ", 1)[::-1] for line in lines if "  " in line)
        for typ in ("project", "chat", "custom_gpt", "claude", "opencode", "runtime_parity"):
            name = expected[typ]
            if sums.get(name) != digest(out / name):
                return fail("SHA256SUMS mismatch " + name)

        parity = yaml.safe_load((out / "runtime-parity.yaml").read_text(encoding="utf-8"))
        if not all(parity["runtimes"][rid]["enabled"] for rid in expected_targets):
            return fail("parity report must show all four runtimes enabled")

    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))
    match = re.fullmatch(r"C([1-7])", status["progress"]["completed_step"] or "")
    if not match or int(match.group(1)) < 5:
        return fail("persistent status predates C5")

    print("C5 unified build tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
