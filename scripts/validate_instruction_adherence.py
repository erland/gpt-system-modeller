#!/usr/bin/env python3
"""Static validation of the System Modeller instruction-adherence contract."""
from __future__ import annotations
import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_IDS = {
    "bootstrap-core-001",
    "multiturn-retention-001",
    "source-analysis-001",
    "runtime-reference-independence-001",
}

RUNTIME_MARKERS = [
    "Den kanoniska YAML-modellen",
    "stabila ID",
    "origin",
    "evidence",
    "Validera efter ändringar",
    "instructions/source-analysis.md",
    "Class ≠ Component",
    "Endpoint ≠ UseCase",
    "DatabaseTable ≠ InformationObject",
    "Blanda aldrig ihop dem",
]

SOURCE_MARKERS = [
    "Preserve the canonical model as the truth source",
    "Separate observed facts from inferred architecture concepts",
    "Never infer Class=Component",
    "Endpoint=UseCase",
    "Table=InformationObject",
    "origin: [inferred]",
    "Record unresolved ambiguity",
]

BOOTSTRAP_MARKERS = [
    "instructions/chat-runtime.md",
    "instructions/source-analysis.md",
    "metamodel/",
    "schemas/",
    "examples/",
    "Kärnflödet ska fungera",
]

def validate(root: Path) -> None:
    eval_root = root / "evals" / "instruction-adherence"
    if not eval_root.is_dir():
        raise SystemExit("Missing evals/instruction-adherence")
    files = sorted(eval_root.glob("*.yaml"))
    ids = set()
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key in ["id", "title", "criticality", "input", "expected"]:
            if key not in data:
                raise SystemExit(f"{path.name}: missing {key}")
        ids.add(data["id"])
    missing = REQUIRED_IDS - ids
    if missing:
        raise SystemExit(f"Missing instruction-adherence evals: {sorted(missing)}")

    runtime = (root / "instructions" / "chat-runtime.md").read_text(encoding="utf-8")
    source = (root / "instructions" / "source-analysis.md").read_text(encoding="utf-8")
    bootstrap = (root / "SYSTEM-MODELLER-CHAT.md").read_text(encoding="utf-8")

    for marker in RUNTIME_MARKERS:
        if marker.casefold() not in runtime.casefold():
            raise SystemExit(f"Runtime contract missing marker: {marker}")
    for marker in SOURCE_MARKERS:
        if marker.casefold() not in source.casefold():
            raise SystemExit(f"Source-analysis contract missing marker: {marker}")
    for marker in BOOTSTRAP_MARKERS:
        if marker.casefold() not in bootstrap.casefold():
            raise SystemExit(f"Bootstrap contract missing marker: {marker}")

    print(f"Instruction-adherence contract OK: {len(files)} eval cases")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=str(ROOT))
    ns = ap.parse_args()
    validate(Path(ns.project_root).resolve())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
