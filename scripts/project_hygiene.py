#!/usr/bin/env python3
"""Project hygiene gate for GPT Builder 1.5.x repositories."""
from __future__ import annotations

from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = (
    "dist/",
    "build/",
    "release-dist/",
    "distributions/",
    "__pycache__/",
    ".pytest_cache/",
    ".venv/",
    "venv/",
)
FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".zip")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []
    for path in tracked_files():
        if path.startswith(FORBIDDEN_PREFIXES) or path.endswith(FORBIDDEN_SUFFIXES):
            errors.append(f"generated/temporary file tracked in HEAD: {path}")

    registry = yaml.safe_load((ROOT / "runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    status = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))
    expected = set(registry.get("active_targets", []))
    actual = set((status.get("runtime_status") or {}).keys())
    if expected != actual:
        errors.append(
            "project-status runtime set differs from registry: "
            f"status={sorted(actual)} registry={sorted(expected)}"
        )

    if errors:
        print("Project hygiene BLOCKED")
        for error in errors:
            print("-", error)
        return 1

    print("Project hygiene PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
