"""Conservative, reviewable separation-of-concerns suggestions from a legacy instruction."""
from __future__ import annotations
import re
from pathlib import Path


def propose(instruction: str, project_id: str) -> dict:
    """Preserve source text. Do not pretend headings prove independently useful Skills."""
    sections = re.split(r"(?=^#{2,3} )", instruction, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]
    topical = [part for part in sections if part.startswith(("## ", "### "))]
    # Deliberately propose one Skill by default. The user/assistant can review
    # topical boundaries and approve a genuine independent responsibility.
    return {
        "status": "proposal_requires_review",
        "core_source": "canonical legacy instruction (unmodified)",
        "suggested_skills": [{
            "id": project_id, "reason": "Single cohesive capability is the safe baseline",
            "source_sections": list(range(len(sections))),
        }],
        "candidate_boundaries": [
            {"heading": part.splitlines()[0].lstrip("# ").strip(),
             "reason": "Candidate responsibility; verify independent workflow and low coupling"}
            for part in topical
        ],
        "decision_criteria": ["distinct_activation", "cohesive_responsibility", "independent_workflow", "low_coupling"],
        "duplication_policy": {"canonical_sources": "avoid_repeated_behavior", "generated_distributions": "allow_shared_core_for_standalone_skills", "similarity_threshold": None},
        "approval_required_for_split": True,
        "source_text_preserved": True,
        "source_sections": sections,
    }


def propose_file(path: Path, project_id: str) -> dict:
    return propose(path.read_text(encoding="utf-8"), project_id)
