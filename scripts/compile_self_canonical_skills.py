#!/usr/bin/env python3
"""Regenerate or check GPT Byggaren's legacy system.md from canonical modules."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "canonical_skill_sources", ROOT / "scripts/lib/canonical_skill_sources.py"
)
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)


def main() -> int:
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--check", action="store_true")
    choice.add_argument("--write", action="store_true")
    args = parser.parse_args()
    cfg = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
    if cfg["instructions"].get("mode") != "modular_skills":
        raise SystemExit("Modular canonical Skills are not active")
    projected = compiler.projected_instruction(ROOT, cfg, cfg["skills"]["definitions"])
    target = ROOT / cfg["instructions"]["canonical"]
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != projected:
            raise SystemExit("FAIL: system.md does not match canonical Skill assembly")
        print("PASS: canonical assembly is byte-identical")
    else:
        target.write_text(projected, encoding="utf-8")
        print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
