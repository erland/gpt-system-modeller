from pathlib import Path
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def test_instruction_adherence_contract():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_instruction_adherence.py"),
         "--project-root", str(ROOT)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Instruction-adherence contract OK" in result.stdout

def test_instruction_adherence_eval_ids():
    files = sorted((ROOT / "evals" / "instruction-adherence").glob("*.yaml"))
    ids = {yaml.safe_load(p.read_text(encoding="utf-8"))["id"] for p in files}
    assert {
        "bootstrap-core-001",
        "multiturn-retention-001",
        "source-analysis-001",
        "runtime-reference-independence-001",
    }.issubset(ids)
