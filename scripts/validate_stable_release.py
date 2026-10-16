#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, json
from pathlib import Path
import yaml

def select_profile(features):
    if features.get("research_heavy") or features.get("evidence_required") or features.get("multi_stage_workflow"):
        return "workflow_research_heavy"
    if features.get("project_zip_manipulation") or features.get("scripts_required") or features.get("rich_structured_runtime"):
        return "zip_first_advanced"
    if features.get("structured_knowledge") or features.get("repeatable_outputs") or features.get("moderate_workflow"):
        return "standard"
    return "simple"

def validate(root, version):
    gates={}

    required=[
        "gpt-project.yaml","project-status.yaml","architecture.yaml",
        "docs/development-plan.md","src/instructions/system.md",
        "docs/stable-release.md","schemas/stable-release.schema.json"
    ]
    gates["project_contract"]="pass" if all((root/p).exists() for p in required) else "blocked"

    ok=True
    refs=list((root/"evals"/"reference-projects").glob("*.yaml"))
    if len(refs)!=3:
        ok=False
    for p in refs:
        case=yaml.safe_load(p.read_text(encoding="utf-8"))
        ok &= select_profile(case["characteristics"]) == case["expected"]["profile"]
    gates["reference_projects"]="pass" if ok else "blocked"

    scenario=yaml.safe_load((root/"evals"/"e2e"/"blank-idea-001.yaml").read_text(encoding="utf-8"))
    gates["blank_idea_e2e"]="pass" if select_profile(scenario["features"]) == scenario["expected"]["profile"] else "blocked"

    cfg=yaml.safe_load((root/"gpt-project.yaml").read_text(encoding="utf-8"))
    instr=(root/"src"/"instructions"/"system.md").read_text(encoding="utf-8")
    custom=cfg.get("runtime",{}).get("custom_gpt",{})
    max_chars=custom.get("instruction",{}).get("max_characters") or custom.get("instruction_max_characters") or 8000
    gates["custom_instruction_limit"]="pass" if len(instr)<=int(max_chars) else "blocked"

    kroot=root/"knowledge"
    kfiles=[p for p in kroot.rglob("*") if p.is_file() and p.name!="KNOWLEDGE.md"] if kroot.exists() else []
    max_files=custom.get("knowledge",{}).get("max_files") or custom.get("knowledge_max_files") or 20
    gates["custom_knowledge_limit"]="pass" if len(kfiles)<=int(max_files) else "blocked"

    compile_ok=True
    for p in list((root/"scripts").rglob("*.py"))+list((root/"tests").rglob("*.py")):
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:
            compile_ok=False
    gates["python_compile"]="pass" if compile_ok else "blocked"

    bad=[]
    for p in root.rglob("*"):
        if p.name in {"__pycache__",".pytest_cache",".DS_Store"}:
            bad.append(p)
        if p.is_file() and p.suffix.lower() in {".tmp",".temp",".bak",".old"}:
            bad.append(p)
    gates["project_hygiene"]="pass" if not bad else "blocked"

    status=yaml.safe_load((root/"project-status.yaml").read_text(encoding="utf-8"))
    stable_ok=status.get("release",{}).get("state")=="stable" and status.get("release",{}).get("version")==version
    gates["stable_status"]="pass" if stable_ok else "blocked"

    result="pass" if all(v=="pass" for v in gates.values()) else "blocked"
    return {"schema_version":1,"version":version,"result":result,"stable":True,"gates":gates,"artifacts":[]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",default=".")
    ap.add_argument("--version",required=True)
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    result=validate(Path(args.project_root).resolve(),args.version)
    print(json.dumps(result,ensure_ascii=False,indent=2) if args.json else f"Stable release: {result['result'].upper()}")
    return 0 if result["result"]=="pass" else 1

if __name__=="__main__":
    raise SystemExit(main())
