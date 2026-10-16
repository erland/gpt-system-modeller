"""Validate opt-in canonical Skills and built ZIP contents before migration completion."""
from __future__ import annotations
import json
from pathlib import Path
import zipfile


def inspect(root: Path, cfg: dict, version: str | None = None) -> dict:
    from .canonical_skill_sources import is_modular, modules, projected_instruction, skill_instruction
    definitions = (cfg.get("skills") or {}).get("definitions") or []
    if not is_modular(cfg):
        return {"status": "blocked", "reason": "instructions.mode is not modular_skills", "release_ready": False}
    try:
        core, parts = modules(root, cfg, definitions)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {"status": "blocked", "reason": str(exc), "release_ready": False}
    if not version:
        return {"status": "sources_valid_pending_archive_checks", "skills": [s["id"] for s, _ in parts],
                "release_ready": False}
    dist = root / "dist"
    project_id = cfg["project"]["id"]
    targets = {"chat": f"{project_id}-chat-{version}.zip",
               "plugin": f"{project_id}-plugin-{version}.zip",
               "claude_project": f"{project_id}-claude-project-{version}.zip",
               "claude_skills": f"{project_id}-claude-skills-{version}.zip",
               "opencode": f"{project_id}-opencode-{version}.zip"}
    expected = projected_instruction(root, cfg, definitions).strip()
    checks = {}
    errors = []
    for target, filename in targets.items():
        archive = dist / filename
        if not archive.is_file():
            errors.append(f"{target}: missing archive {filename}")
            continue
        try:
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                if z.testzip() is not None:
                    errors.append(f"{target}: invalid ZIP member")
                    continue
                if target in ("chat", "claude_project", "opencode"):
                    suffix = {"chat": "assistant/instructions.md", "claude_project": "project/instructions.md",
                              "opencode": "AGENTS.md"}[target]
                    matches = [n for n in names if n.endswith(suffix)]
                    if len(matches) != 1 or expected not in z.read(matches[0]).decode("utf-8"):
                        errors.append(f"{target}: incomplete assembled instruction")
                else:
                    for skill in definitions:
                        suffix = f"skills/{skill['id']}/SKILL.md"
                        matches = [n for n in names if n.endswith(suffix)]
                        if len(matches) != 1:
                            errors.append(f"{target}/{skill['id']}: missing or duplicate SKILL.md")
                            continue
                        body = z.read(matches[0]).decode("utf-8")
                        own = skill_instruction(root, cfg, definitions, skill)
                        if own.strip() not in body:
                            errors.append(f"{target}/{skill['id']}: canonical behavior missing")
                        for other, text in parts:
                            if other["id"] != skill["id"] and text.strip() in body:
                                errors.append(f"{target}/{skill['id']}: duplicates behavior of {other['id']}")
                checks[target] = "checked"
        except (OSError, zipfile.BadZipFile, UnicodeError) as exc:
            errors.append(f"{target}: {exc}")
    return {"status": "blocked" if errors else "archive_content_verified_pending_host",
            "errors": errors, "checked_targets": checks,
            "skills": [s["id"] for s, _ in parts], "release_ready": False,
            "runtime_parity_verified": False}
