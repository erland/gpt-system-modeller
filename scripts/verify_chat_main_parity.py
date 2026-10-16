#!/usr/bin/env python3
"""Guard against loss of System Modeller's original portable Chat runtime."""
from __future__ import annotations
import argparse
import ast
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--version", default="0.0.0-ci")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    legacy_builder = root / "scripts" / "package_chat.py"
    tree = ast.parse(legacy_builder.read_text(encoding="utf-8"))
    selected = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("INCLUDE_"):
                    selected[target.id] = ast.literal_eval(node.value)
    required = {
        "metamodel/common.yaml", "metamodel/id-prefixes.yaml",
        "schemas/common.schema.json", "instructions/chat-runtime.md",
        "instructions/source-analysis.md", "SYSTEM-MODELLER-CHAT.md",
    }
    for name in selected.get("INCLUDE_SCRIPTS", set()):
        required.add("scripts/" + name)
    for name in selected.get("INCLUDE_DOCS", set()):
        if (root / "docs" / name).is_file():
            required.add("docs/" + name)
    for directory in selected.get("INCLUDE_DIRS", set()):
        for p in (root / directory).rglob("*"):
            if p.is_file():
                required.add(p.relative_to(root).as_posix())
    required = {name for name in required if (root / name).is_file()}
    archive = root / "dist" / ("system-modeller-chat-" + args.version + ".zip")
    if not archive.exists():
        raise SystemExit(f"Missing built Chat archive: {archive}")
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        # New canonical Chat layout intentionally relocates instructions into assistant/.
        required -= {"instructions/chat-runtime.md", "instructions/source-analysis.md"}
        assert "assistant/instructions.md" in names, "Canonical instruction missing"
        missing = sorted(required - names)
        if missing:
            raise SystemExit("Lost Chat runtime resources:\n" + "\n".join(missing))
        if zf.testzip() is not None:
            raise SystemExit("Chat ZIP checksum error")
    print(f"Main Chat runtime file coverage PASS: {len(required)} resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
