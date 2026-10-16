"""Canonical modular Skill activation must preserve the original instruction exactly."""
import importlib.util
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def test_modular_activation_exact_instruction():
    cfg=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    assert cfg["instructions"]["mode"]=="modular_skills"
    from_path=ROOT/"scripts/lib/canonical_skill_sources.py"
    spec=importlib.util.spec_from_file_location("canonical_skill_sources",from_path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    definitions=cfg["skills"]["definitions"]
    assert len(definitions)==6
    actual=mod.projected_instruction(ROOT,cfg,definitions)
    original=(ROOT/"instructions/chat-runtime.md").read_text(encoding="utf-8")
    assert actual==original, "Modular assembly must be byte-identical to legacy instruction"
    manifest=json.loads((ROOT/"canonical/assembly.json").read_text(encoding="utf-8"))
    assert len(manifest["sections"])==10
    for definition in definitions:
        own=mod.skill_instruction(ROOT,cfg,definitions,definition)
        assert (ROOT/definition["source"]).read_text(encoding="utf-8").strip() in own
        assert original.startswith("# System Modeller")
