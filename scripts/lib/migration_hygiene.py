"""Evidence-based migration hygiene and guided progress; never delete source files."""
from __future__ import annotations
from pathlib import Path
import re

DOCS = ("README.md", "PROJECT.md", "STATUS.md", "docs/development-plan.md")
LEGACY_VALIDATORS = (
    "scripts/validate_workflow_parity.py",
    "scripts/validate_release_readiness.py",
    "scripts/validate_runtime_parity.py",
)


def assess_hygiene(project: Path, *, engine_version: str | None = None) -> dict:
    missing_docs = [name for name in DOCS if not (project / name).is_file()]
    stale_versions = []
    stale_ci = []
    legacy_scripts = []
    broken_references = []
    unchecked_migration_steps = []
    for name in DOCS:
        path = project / name
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if engine_version:
            versions = set(re.findall(r"(?i)(?:gpt.byggaren.{0,30}?v?)(1\.\d+\.\d+)", content))
            if versions and versions != {engine_version}:
                stale_versions.append({"file": name, "mentioned_versions": sorted(versions)})
        for match in re.finditer(r"\[[^]]+\]\(([^)]+)\)", content):
            link = match.group(1).split("#", 1)[0].strip()
            if not link or link.startswith(("http:", "https:", "mailto:", "#", "/")):
                continue
            target = (path.parent / link).resolve()
            if target.is_relative_to(project.resolve()) and not target.exists():
                broken_references.append({"file": name, "target": link})
        if name == "docs/development-plan.md":
            unchecked_migration_steps.extend(re.findall(r"(?m)^\s*- \[ \]\s+(.+)$", content))
        if name == "STATUS.md" and re.search(r"(?i)CI\s*#\d+", content):
            stale_ci.append(name)
    migration_docs = sorted((project / "docs").glob("migration*.md")) if (project / "docs").is_dir() else []
    migration_checklists = []
    status_text = (project / "STATUS.md").read_text(encoding="utf-8") if (project / "STATUS.md").is_file() else ""
    unresolved_status_claims = []
    if re.search(r"(?i)migrationen (?:genomförs|pågår) i PR\s*#\d+", status_text):
        unresolved_status_claims.append("STATUS.md still describes migration as ongoing in a PR")
    for path in migration_docs:
        content = path.read_text(encoding="utf-8")
        open_items = re.findall(r"(?m)^\s*- \[ \]\s+(.+)$", content)
        if open_items:
            migration_checklists.append({"file": path.relative_to(project).as_posix(), "open_items": open_items})
    for name in LEGACY_VALIDATORS:
        if (project / name).is_file():
            legacy_scripts.append(name)
    return {
        "status": "review_required" if missing_docs or stale_versions or legacy_scripts or stale_ci or broken_references or unchecked_migration_steps or migration_checklists or unresolved_status_claims else "checked_no_known_findings",
        "missing_documents": missing_docs,
        "possible_stale_versions": stale_versions,
        "ci_references_to_reconcile": stale_ci,
        "legacy_validator_candidates": legacy_scripts,
        "broken_document_links": broken_references,
        "open_development_checklist_items": unchecked_migration_steps,
        "open_migration_checklists": migration_checklists,
        "unresolved_status_claims": unresolved_status_claims,
        "files_deleted": [],
        "documentation_modified": False,
        "required_actions": [
            "Update README, PROJECT, STATUS, development plan and migration checklist together.",
            "Compare legacy validator behavior with canonical checks before deleting any file.",
            "Reconcile CI identifiers and actual validation evidence; do not claim host parity from ZIP builds.",
            "Verify no documentation points at removed paths before release.",
        ],
    }


def migration_steps(report: dict) -> list[dict]:
    build = report.get("canonical_build_upgrade") or {}
    hygiene = report.get("project_hygiene") or {}
    engine = report.get("engine_migration") or {}
    rows = [
        ("inventory", "Inventera källprojekt", "completed" if report.get("generic_discovery") else "pending"),
        ("model", "Granska projektmodell och runtime-mappning",
         "review_required" if report.get("apply", {}).get("result") == "blocked" else "completed"),
        ("engine", "Bedöm och installera kanonisk byggmotor",
         "completed" if build.get("status") == "built_pending_host_acceptance" else "pending_or_blocked"),
        ("distributions", "Bygg och kontrollera fem distributioner",
         "completed" if build.get("status") == "built_pending_host_acceptance" else "pending_or_blocked"),
        ("hygiene", "Uppdatera dokumentation och granska äldre filer",
         "review_required" if hygiene.get("status") != "checked_no_known_findings" else "checked"),
        ("release", "Slutverifiera runtime och release",
         "pending" if not build.get("release_ready") else "review_required"),
    ]
    return [{"id": key, "title": title, "status": status} for key, title, status in rows]
