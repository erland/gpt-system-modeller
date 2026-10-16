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
        if runtime in ("plugin", "claude-skills"):
            import re
            declared = {"analyze.py", "context.py", "model.py", "package_project.py",
                        "report.py", "validate.py", "view.py"}
            for skill in SKILLS:
                skill_root = destination/"skills"/skill
                body = (skill_root/"SKILL.md").read_text(encoding="utf-8")
                assert body.startswith("---\\nname: "+skill+"\\n"),(runtime,skill)
                routing = body.split("## Installed tool availability (authoritative)",1)[1].split("## Canonical behavior",1)[0]
                assert "reliable validation is mandatory" in routing
                for name in declared:
                    exists = (skill_root/"scripts"/name).is_file()
                    label = f"`scripts/{name}`"
                    status = "available locally" if exists else "NOT installed"
                    assert f"{label}: {status}" in routing,(runtime,skill,name)
                assert "INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE" in body
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
