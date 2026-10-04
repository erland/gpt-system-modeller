#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys, tempfile, zipfile
from pathlib import Path

REQUIRED={
 "plugin.json","runtime-contract.json","README.md","VERSION",
 "skills/system-modeller/SKILL.md",
 "skills/system-modeller/scripts/context.py",
 "skills/system-modeller/scripts/validate.py",
 "skills/system-modeller/scripts/model.py",
 "skills/system-modeller/scripts/view.py",
 "skills/system-modeller/scripts/report.py",
 "skills/system-modeller/scripts/package_project.py",
 "skills/system-modeller/scripts/analyze.py",
 "skills/system-modeller/scripts/ids.py",
 "skills/system-modeller/scripts/report_profile.py",
 "skills/system-modeller/scripts/sequence_diagrams.py",
 "skills/system-modeller/scripts/view_split.py",
 "skills/system-modeller/scripts/diagram_complexity.py",
 "skills/system-modeller/schemas/views.schema.json",
 "skills/system-modeller/metamodel/id-prefixes.yaml",
}

def validate(path:Path)->list[str]:
    errors=[]
    with zipfile.ZipFile(path) as zf:
        names=set(zf.namelist())
        missing=sorted(REQUIRED-names)
        if missing: errors.append("missing members: "+", ".join(missing))
        if "runtime-contract.json" in names:
            c=json.loads(zf.read("runtime-contract.json").decode("utf-8"))
            if c.get("runtime_id")!="openai_plugin": errors.append("runtime_id mismatch")
            if c.get("compatibility")!="equivalent_runtime_dependent": errors.append("compatibility mismatch")
            req=c.get("runtime_requirements",{})
            if req.get("filesystem",{}).get("write")!="required": errors.append("filesystem write must be required")
            if req.get("code_execution",{}).get("level")!="required": errors.append("code execution must be required")
            if req.get("code_execution",{}).get("fallback")!="block": errors.append("code execution fallback must block")
            if c.get("tool_policy",{}).get("approval_required_for_mutation") is not True: errors.append("mutation approval must be required")
            if c.get("script_resources",{}).get("mcp_required_for_resource_use") is not False: errors.append("script resources must not require MCP")
        if "skills/system-modeller/SKILL.md" in names:
            skill=zf.read("skills/system-modeller/SKILL.md").decode("utf-8")
            for marker in ("Python code execution is required","Mutating model operations require explicit approval","INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE","Never report an unrun validation"):
                if marker not in skill: errors.append("SKILL.md missing marker: "+marker)
        if not errors:
            with tempfile.TemporaryDirectory() as td:
                zf.extractall(td)
                scripts=Path(td)/"skills"/"system-modeller"/"scripts"
                for script in ("context.py","validate.py","model.py","view.py","report.py","package_project.py","analyze.py"):
                    result=subprocess.run([sys.executable,str(scripts/script),"--help"],cwd=scripts,capture_output=True,text=True)
                    if result.returncode!=0:
                        errors.append(f"{script} import/help failed: "+(result.stderr or result.stdout).strip())
    return errors

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--artifact",type=Path,required=True)
    ns=ap.parse_args(); errors=validate(ns.artifact)
    if errors:
        print("FAILED: OpenAI Plugin runtime")
        for e in errors: print("-",e)
        return 1
    print("OK: OpenAI Plugin runtime"); return 0

if __name__=="__main__": raise SystemExit(main())
