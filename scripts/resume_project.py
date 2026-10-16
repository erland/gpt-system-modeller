#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path
import yaml

READ_ORDER=["gpt-project.yaml","project-status.yaml","docs/development-plan.md","STATUS.md","PROJECT.md"]
REQUIRED=READ_ORDER[:3]

def inspect(root, run_checks=True):
    if not (root/"gpt-project.yaml").exists():
        return {"status":"legacy_or_unknown","project_id":None,"project_name":None,
                "last_completed_step":None,"recommended_next_step":None,"recommended_next_title":None,
                "blockers":["Missing gpt-project.yaml"],"warnings":[],"validation":None,"hygiene":None,
                "files_read_order":[]}

    try:
        project=yaml.safe_load((root/"gpt-project.yaml").read_text(encoding="utf-8"))
    except Exception as e:
        return {"status":"blocked","project_id":None,"project_name":None,
                "last_completed_step":None,"recommended_next_step":None,"recommended_next_title":None,
                "blockers":[f"Invalid gpt-project.yaml: {e}"],"warnings":[],"validation":None,"hygiene":None,
                "files_read_order":["gpt-project.yaml"]}

    pid=project.get("project",{}).get("id")
    pname=project.get("project",{}).get("name")
    missing=[p for p in REQUIRED if not (root/p).exists()]
    if missing:
        return {"status":"blocked","project_id":pid,"project_name":pname,
                "last_completed_step":None,"recommended_next_step":None,"recommended_next_title":None,
                "blockers":[f"Missing required resume file: {p}" for p in missing],"warnings":[],
                "validation":None,"hygiene":None,
                "files_read_order":[p for p in READ_ORDER if (root/p).exists()]}

    try:
        status=yaml.safe_load((root/"project-status.yaml").read_text(encoding="utf-8"))
    except Exception as e:
        return {"status":"blocked","project_id":pid,"project_name":pname,
                "last_completed_step":None,"recommended_next_step":None,"recommended_next_title":None,
                "blockers":[f"Invalid project-status.yaml: {e}"],"warnings":[],
                "validation":None,"hygiene":None,
                "files_read_order":[p for p in READ_ORDER if (root/p).exists()]}

    blockers=[str(x) for x in (status.get("blocking_issues") or status.get("blockers") or [])]
    warnings=[str(x) for x in (status.get("warnings") or [])]
    next_id=status.get("next_step",{}).get("recommended")
    next_title=status.get("next_step",{}).get("title")

    if run_checks:
        lint_script=root/"scripts"/"lint_gpt_project.py"
        if lint_script.exists():
            r=subprocess.run([sys.executable,str(lint_script),"--project-root",str(root),"--json"],capture_output=True,text=True)
            try:
                rep=json.loads(r.stdout)
                for f in rep.get("findings",[]):
                    msg=f"{f.get('code')}: {f.get('message')}"
                    if f.get("severity")=="error": blockers.append(msg)
                    elif f.get("severity")=="warning": warnings.append(msg)
            except Exception:
                warnings.append("Could not parse lint result during resume.")

        next_script=root/"scripts"/"recommend_next_step.py"
        if next_script.exists():
            r=subprocess.run([sys.executable,str(next_script),"--project-root",str(root),"--json"],capture_output=True,text=True)
            try:
                rec=json.loads(r.stdout)["recommended"]
                next_id=rec.get("step_id")
                next_title=rec.get("title")
            except Exception:
                warnings.append("Could not calculate next-step recommendation during resume.")

    blockers=sorted(set(blockers))
    warnings=sorted(set(warnings))
    state="needs_correction" if blockers else ("ready_with_warnings" if warnings else "ready")

    return {"status":state,"project_id":pid,"project_name":pname,
            "last_completed_step":status.get("progress",{}).get("last_completed_step"),
            "recommended_next_step":next_id,"recommended_next_title":next_title,
            "blockers":blockers,"warnings":warnings,
            "validation":status.get("validation",{}).get("last_result"),
            "hygiene":status.get("project_hygiene",{}).get("last_result"),
            "files_read_order":[p for p in READ_ORDER if (root/p).exists()]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",default=".")
    ap.add_argument("--json",action="store_true")
    ap.add_argument("--no-checks",action="store_true")
    args=ap.parse_args()
    result=inspect(Path(args.project_root).resolve(),not args.no_checks)
    if args.json:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(f"Resume status: {result['status']}")
        print(f"Project: {result['project_name']} ({result['project_id']})")
        print(f"Last completed step: {result['last_completed_step']}")
        print(f"Recommended next step: {result['recommended_next_step']} - {result['recommended_next_title']}")
    return 0 if result["status"] in {"ready","ready_with_warnings"} else 1

if __name__=="__main__":
    raise SystemExit(main())
