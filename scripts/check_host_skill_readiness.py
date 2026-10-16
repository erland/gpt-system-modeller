#!/usr/bin/env python3
"""Offline preflight for host Skills. Never claims installation or execution."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

def check(root: Path, target: str) -> dict:
    if target not in ("claude", "plugin"):
        raise ValueError("target must be claude or plugin")
    errors = []
    skills_root = root / "skills"
    skills = sorted(p for p in skills_root.iterdir() if p.is_dir()) if skills_root.is_dir() else []
    if not skills:
        errors.append("No packaged skills")
    for folder in skills:
        spec = folder / "SKILL.md"
        if not spec.is_file():
            errors.append(f"{folder.name}: SKILL.md missing")
            continue
        content = spec.read_text(encoding="utf-8")
        if not content.startswith("---\n") or "\n---\n" not in content[4:]:
            errors.append(f"{folder.name}: invalid frontmatter delimiters")
            continue
        metadata = content.split("---", 2)[1]
        name = re.search(r"(?m)^name:\s*(\S.*?)\s*$", metadata)
        description = re.search(r"(?m)^description:\s*(.+?)\s*$", metadata)
        if not name or name.group(1) != folder.name:
            errors.append(f"{folder.name}: name/folder mismatch")
        if not description:
            errors.append(f"{folder.name}: missing description")
        for category in ("references", "assets", "scripts"):
            path = folder / category
            if path.is_dir() and any(p.is_symlink() for p in path.rglob("*")):
                errors.append(f"{folder.name}: unsafe symlink in {category}")
    if target == "plugin":
        if not (root / "plugin.json").is_file():
            errors.append("Missing plugin.json")
        if list(root.rglob("mcp.json")):
            errors.append("Forbidden mcp.json in Plugin")
    else:
        if not (root / "project").is_dir():
            errors.append("Missing Claude Projects directory")
    return {"target": target, "status": "invalid" if errors else "offline_ready",
            "skills_checked": len(skills), "errors": errors,
            "host_installed": False, "host_execution_verified": False}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--distribution", type=Path, required=True)
    p.add_argument("--target", choices=("claude", "plugin"), required=True)
    args = p.parse_args()
    try:
        result = check(args.distribution, args.target)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
