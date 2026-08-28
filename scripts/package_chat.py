#!/usr/bin/env python3
"""Build the System Modeller portable Chat-ZIP runtime."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import versioning

FIXED_DATE = (2020, 1, 1, 0, 0, 0)

# Root files useful to the portable runtime. Development/status/release material is excluded.
INCLUDE_ROOT = {
    "README.md",
    "VERSION",
    "SYSTEM-MODELLER-CHAT.md",
}

# Canonical runtime behavior.
INCLUDE_INSTRUCTIONS = {
    "chat-runtime.md",
    "source-analysis.md",
}

# Runtime scripts only. CI, release, test harness and distribution builders do not belong
# in the portable Chat runtime.
INCLUDE_SCRIPTS = {
    "analyze.py",
    "ids.py",
    "model.py",
    "package_project.py",
    "report.py",
    "validate.py",
    "view.py",
}

# Documentation that defines or explains the modeling/runtime semantics.
INCLUDE_DOCS = {
    "architecture-decisions-and-constraints.md",
    "architecture-description.md",
    "context-model.md",
    "data-stores.md",
    "deployment-context.md",
    "deployment-relations.md",
    "design-principles.md",
    "functional-model.md",
    "information-model.md",
    "information-usage.md",
    "interactions.md",
    "interfaces-and-apis.md",
    "logical-architecture.md",
    "messages-and-events.md",
    "model-format.md",
    "model-operations.md",
    "modeling-principles.md",
    "origin-declared-observed-inferred.md",
    "provenance-and-evidence.md",
    "runtime-units.md",
    "scenarios.md",
    "source-analysis.md",
    "system-project-format.md",
    "use-case-model.md",
    "validation.md",
    "views.md",
}

# Whole canonical runtime directories whose content is directly useful at runtime.
INCLUDE_DIRS = {"metamodel", "schemas", "templates", "examples"}

EXCLUDED_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".venv", "venv",
    "distributions", "tests",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def included_files():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if any(x in EXCLUDED_DIRS for x in rel.parts):
            continue
        if p.suffix in EXCLUDED_SUFFIXES or p.name == ".DS_Store":
            continue

        if len(rel.parts) == 1:
            if rel.name not in INCLUDE_ROOT:
                continue
        elif rel.parts[0] == "instructions":
            if rel.name not in INCLUDE_INSTRUCTIONS:
                continue
        elif rel.parts[0] == "scripts":
            if rel.name not in INCLUDE_SCRIPTS:
                continue
        elif rel.parts[0] == "docs":
            if rel.name not in INCLUDE_DOCS:
                continue
        elif rel.parts[0] not in INCLUDE_DIRS:
            continue

        yield p, rel


def build(out: Path, distribution_version: str | None = None):
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for p, rel in included_files():
            info = ZipInfo(f"system-modeller/{rel.as_posix()}", FIXED_DATE)
            info.compress_type = ZIP_DEFLATED
            mode = 0o755 if rel.parts and rel.parts[0] == "scripts" and p.suffix in {".py", ".sh"} else 0o644
            data = (
                (distribution_version + "\n").encode("utf-8")
                if rel.as_posix() == "VERSION" and distribution_version
                else p.read_bytes()
            )
            info.external_attr = mode << 16
            zf.writestr(info, data)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--release-version")
    ns = ap.parse_args()
    info = versioning.resolve(explicit=ns.release_version)
    out = ns.output or ROOT / "distributions" / f"system-modeller-chat-v{info.release_version}.zip"
    print(build(out, info.distribution_version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
