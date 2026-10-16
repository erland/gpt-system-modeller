#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml
import jsonschema

REQUIRED_IDS = {
    "bootstrap-core-001",
    "multiturn-retention-001",
    "terminal-contract-001",
    "no-knowledge-core-001",
}

def validate(root: Path) -> None:
    cfg = yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8"))
    schema = json.loads((root / "schemas" / "eval-case.schema.json").read_text(encoding="utf-8"))
    eval_root = root / "evals" / "instruction-adherence"
    if not eval_root.exists():
        raise SystemExit("Missing evals/instruction-adherence")

    files = sorted(eval_root.glob("*.yaml"))
    ids = set()
    for path in files:
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        jsonschema.validate(case, schema)
        ids.add(case["id"])

    missing = REQUIRED_IDS - ids
    if missing:
        raise SystemExit(f"Missing instruction-adherence evals: {sorted(missing)}")

    core = cfg.get("instructions", {}).get("core_contract", {})
    if not core.get("enabled"):
        raise SystemExit("instructions.core_contract must be enabled")
    if not core.get("required_markers"):
        raise SystemExit("core_contract.required_markers must not be empty")
    if core.get("knowledge_may_not_be_required_for_core_behavior") is not True:
        raise SystemExit("Core behavior must be independent of optional Knowledge")

    deps = core.get("required_runtime_dependencies") or []
    for dep in deps:
        if str(dep).replace("\\", "/").lstrip("./").startswith("knowledge/"):
            raise SystemExit("Core behavior may not require Knowledge dependencies")

    max_hops = core.get("max_required_file_hops", 1)
    if isinstance(max_hops, int) and len(deps) > max_hops:
        raise SystemExit(
            f"Required runtime dependencies exceed hop budget: {len(deps)} > {max_hops}"
        )

    print(f"Instruction-adherence contract OK: {len(files)} eval cases")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    args = ap.parse_args()
    validate(Path(args.project_root).resolve())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
