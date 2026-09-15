#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import tempfile
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_check


def fail(message):
    print("FAIL:", message)
    return 1


def main():
    spec_path = ROOT / "templates" / "custom-gpt-distribution.yaml"
    doc_path = ROOT / "docs" / "plan-b-release-readiness.md"
    workflow_path = ROOT / ".github" / "workflows" / "build-distributions.yml"
    for path in (spec_path, doc_path, workflow_path, ROOT / "metamodel" / "report-profiles" / "catalog.yaml"):
        if not path.is_file():
            return fail(f"missing B12 artifact {path.relative_to(ROOT)}")

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    knowledge = {item["output"]: item for item in spec.get("knowledge") or []}
    report_sources = set((knowledge.get("04-views-and-architecture-description.md") or {}).get("sources") or [])
    required_report_sources = {
        "docs/views.md",
        "docs/architecture-description.md",
        "docs/architecture-report-profile.md",
        "docs/diagram-complexity.md",
        "docs/diagram-splitting.md",
        "docs/scenario-sequence-diagrams.md",
        "docs/pdf-presentation-contract.md",
        "docs/report-profile-groundwork.md",
    }
    if not required_report_sources.issubset(report_sources):
        return fail("Custom GPT report Knowledge does not include all Plan B report sources")
    if len(knowledge) != 6:
        return fail("B12 must retain exactly six Custom GPT Knowledge files")

    capabilities = set((spec.get("parity_contract") or {}).get("shared_capabilities") or [])
    required_caps = {
        "deterministic_runtime_flow",
        "architecture_report_profile",
        "diagram_complexity_budgets",
        "automatic_diagram_splitting",
        "scenario_specific_sequence_diagrams",
        "pdf_presentation_contract",
        "report_profile_catalog",
    }
    if not required_caps.issubset(capabilities):
        return fail("Plan B capabilities missing from parity contract")

    workflow = workflow_path.read_text(encoding="utf-8")
    if "github.event_name == 'pull_request'" not in workflow:
        return fail("PR workflow does not build and validate distributions")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "release"
        readiness = release_check.build_and_check(out)
        if readiness.get("status") != "READY":
            return fail(f"release readiness failed: {readiness.get('errors')}")
        checks = readiness.get("local_checks") or {}
        if not checks or not all(checks.values()):
            return fail(f"not all release-readiness checks passed: {checks}")

        release = readiness["release_version"]
        chat = out / f"system-modeller-chat-v{release}.zip"
        custom = out / f"system-modeller-custom-gpt-v{release}.zip"
        if not chat.is_file() or not custom.is_file():
            return fail("release readiness did not materialize both distribution ZIPs")

        with zipfile.ZipFile(chat) as zf:
            names = set(zf.namelist())
            required_chat = {
                "system-modeller/scripts/context.py",
                "system-modeller/scripts/report_profile.py",
                "system-modeller/scripts/diagram_complexity.py",
                "system-modeller/scripts/view_split.py",
                "system-modeller/scripts/sequence_diagrams.py",
                "system-modeller/scripts/pdf_contract.py",
                "system-modeller/metamodel/report-profiles/catalog.yaml",
                "system-modeller/metamodel/report-profiles/standard.yaml",
                "system-modeller/docs/report-profile-groundwork.md",
                "system-modeller/docs/plan-b-release-readiness.md",
            }
            missing = required_chat - names
            if missing:
                return fail(f"Chat ZIP missing Plan B files: {sorted(missing)}")

        with zipfile.ZipFile(custom) as zf:
            names = set(zf.namelist())
            knowledge_name = "system-modeller-custom-gpt/knowledge/04-views-and-architecture-description.md"
            manifest_name = "system-modeller-custom-gpt/manifest.yaml"
            if knowledge_name not in names or manifest_name not in names:
                return fail("Custom GPT ZIP missing report Knowledge or manifest")
            text = zf.read(knowledge_name).decode("utf-8")
            for source in required_report_sources:
                if f"## Källa: `{source}`" not in text:
                    return fail(f"Custom GPT report Knowledge missing generated source {source}")
            manifest = yaml.safe_load(zf.read(manifest_name).decode("utf-8"))
            source_hashes = manifest.get("source_hashes") or {}
            for source in (
                "metamodel/report-profiles/catalog.yaml",
                "metamodel/report-profiles/standard.yaml",
                "docs/diagram-splitting.md",
                "docs/pdf-presentation-contract.md",
            ):
                if source not in source_hashes:
                    return fail(f"Custom GPT manifest missing Plan B source hash {source}")

    doc = doc_path.read_text(encoding="utf-8")
    for phrase in ("Chat-ZIP", "Custom GPT", "hosted GitHub Actions", "Definition of done för Plan B"):
        if phrase not in doc:
            return fail(f"B12 documentation missing {phrase}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    m = re.fullmatch(r"0\.1\.0-dev\.(\d+)", version)
    if not m or int(m.group(1)) < 50:
        return fail(f"expected version >= dev.50, got {version}")

    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    progress = re.search(r"Plan B progress: B(\d+) / B12", status)
    if not progress or int(progress.group(1)) < 12:
        return fail("STATUS not advanced to B12")
    if "Plan B complete" not in status:
        return fail("STATUS missing Plan B complete marker")

    print("B12 distribution and release-readiness tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
