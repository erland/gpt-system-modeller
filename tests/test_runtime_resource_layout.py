"""Verify runnable System Modeller ZIP layouts, not just declared skill files."""
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION="0.0.0-ci"
SKILLS=("sparbarhet-och-osakerhet","kallanalys","modellforstaelse","arkitekturvyer","arkitekturrapport","projektleverans")

def test_runtime_layout_and_validator(tmp_path):
    targets={
        "plugin":f"system-modeller-plugin-{VERSION}.zip",
        "claude-skills":f"system-modeller-claude-skills-{VERSION}.zip",
        "opencode":f"system-modeller-opencode-{VERSION}.zip",
    }
    for runtime,filename in targets.items():
        archive=ROOT/"dist"/filename
        assert archive.is_file(),filename
        destination=tmp_path/runtime
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(destination)
        if runtime=="opencode":
            roots=[destination]
        else:
            roots=[destination/"skills"/skill for skill in SKILLS]
        for root in roots:
            for directory in ("schemas","metamodel"):
                assert (root/directory/"common.yaml").is_file() if directory=="metamodel" else (root/directory/"common.schema.json").is_file()
            script=root/"scripts"/"validate.py"
            assert script.is_file()
            project=ROOT/"examples"/"reference-order-system"/"project"
            assert project.is_dir()
            result=subprocess.run([sys.executable,"-B",str(script),str(project),"--format","json"],
                                  cwd=root,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},
                                  capture_output=True,text=True,timeout=30)
            assert result.returncode==0,(runtime,root,result.stdout,result.stderr)
            assert "VALIDATION_OK" in result.stdout,(runtime,root,result.stdout)
