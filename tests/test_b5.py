#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import report
import report_profile

REF = ROOT / "examples" / "reference-order-system" / "project"


def fail(message):
    print("FAIL:", message)
    return 1


def main():
    profile_path = ROOT / "metamodel" / "report-profiles" / "standard.yaml"
    doc = ROOT / "docs" / "architecture-report-profile.md"
    for path in (profile_path, ROOT / "scripts" / "report_profile.py", doc):
        if not path.is_file():
            return fail(f"missing B5 artifact {path.relative_to(ROOT)}")

    profile = report_profile.load(profile_path)
    if profile.get("user_selectable") is not False:
        return fail("standard report profile must remain internal in B5")

    expected_ids = report_profile.REQUIRED_SECTION_IDS
    actual_ids = [section["id"] for section in profile["sections"]]
    if actual_ids != expected_ids:
        return fail(f"unexpected section order {actual_ids}")

    expected_titles = [
        "Syfte och omfattning",
        "Systemets sammanhang",
        "Funktionell översikt",
        "Aktörer och use cases",
        "Informationsarkitektur",
        "Logisk arkitektur",
        "Integrationsarkitektur",
        "Viktiga scenarier",
        "Runtime och deployment",
        "Arkitekturbeslut och constraints",
        "Kända osäkerheter",
        "Källor och evidens",
    ]
    if report_profile.section_titles(profile) != expected_titles:
        return fail("standard profile titles no longer match the canonical architecture description")

    diagrams = profile["diagrams"]
    expected_budgets = {
        "preferred_max_elements": 12,
        "hard_max_elements": 20,
        "preferred_max_relationships": 18,
        "hard_max_relationships": 30,
    }
    for key, value in expected_budgets.items():
        if diagrams.get(key) != value:
            return fail(f"unexpected diagram budget {key}={diagrams.get(key)}")
    if diagrams.get("split_large_views") is not True:
        return fail("large-view splitting must be declared in standard profile")
    if (diagrams.get("sequence") or {}).get("one_interaction_per_diagram") is not True:
        return fail("sequence profile must declare one interaction per diagram")

    primary_views = report_profile.primary_view_by_title(profile)
    if primary_views.get("Systemets sammanhang") != "system_context":
        return fail("system context view mapping missing")
    if primary_views.get("Logisk arkitektur") != "logical_component":
        return fail("logical view mapping missing")

    text = report.architecture_description(REF, include_diagrams=True)
    headings = re.findall(r"^##\s+\d+\.\s+(.+)$", text, flags=re.MULTILINE)
    if headings != expected_titles:
        return fail(f"generated report sections diverge from canonical profile: {headings}")

    doc_text = doc.read_text(encoding="utf-8")
    for phrase in (
        "metamodel/report-profiles/standard.yaml",
        "user_selectable: false",
        "B6",
        "B7",
        "B8",
        "B11",
    ):
        if phrase not in doc_text:
            return fail(f"B5 documentation missing {phrase}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    match = re.fullmatch(r"0\.1\.0-dev\.(\d+)", version)
    if not match or int(match.group(1)) < 43:
        return fail(f"expected version >= dev.43, got {version}")

    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    progress = re.search(r"Plan B progress: B(\d+) / B12", status)
    if not progress or int(progress.group(1)) < 5:
        return fail("STATUS not advanced to B5 or later")
    if "B6" not in status:
        return fail("next Plan B step B6 missing")

    print("B5 tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
