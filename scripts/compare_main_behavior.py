#!/usr/bin/env python3
"""Compare unchanged System Modeller domain assets and golden scenarios against main."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("test_a25.py","test_a26.py","test_a27.py","test_a28.py","test_a29.py","test_a30.py")
DOMAINS = ("metamodel","schemas","instructions","examples","docs","templates")
# Distribution-related additions are not domain regression inputs.
DOMAIN_SCRIPTS = (
    "analyze.py","context.py","diagram_complexity.py","ids.py","model.py",
    "package_project.py","pdf_contract.py","report.py","report_profile.py",
    "sequence_diagrams.py","validate.py","view.py","view_split.py",
)

def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_test(root, filename):
    result = subprocess.run([sys.executable, str(root/"tests"/filename)],
                            cwd=root, text=True, capture_output=True, timeout=180)
    return {"exit_code":result.returncode,
            "stdout_tail":result.stdout[-1600:],
            "stderr_tail":result.stderr[-1200:]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main-root",required=True)
    ap.add_argument("--pr-root",default=".")
    ap.add_argument("--output",default="test-results/main-pr-behavior-parity.json")
    a=ap.parse_args()
    main=Path(a.main_root).resolve()
    pr=Path(a.pr_root).resolve()
    differences=[]
    checks={}
    for folder in DOMAINS:
        for source in (main/folder).rglob("*"):
            if not source.is_file(): continue
            rel=source.relative_to(main)
            target=pr/rel
            if not target.is_file() or fingerprint(source)!=fingerprint(target):
                differences.append(str(rel))
    for filename in DOMAIN_SCRIPTS:
        rel=Path("scripts")/filename
        if not (pr/rel).is_file() or fingerprint(main/rel)!=fingerprint(pr/rel):
            differences.append(str(rel))
    for filename in SCENARIOS:
        reference=run_test(main,filename)
        candidate=run_test(pr,filename)
        checks[filename]={"main":reference,"pr":candidate,
                          "pass":reference["exit_code"]==0 and candidate["exit_code"]==0}
    outcome=not differences and all(x["pass"] for x in checks.values())
    report={"result":"PASS" if outcome else "FAIL",
            "changed_domain_files":sorted(differences),
            "scenarios":checks,
            "note":"Golden test assertions validate substantive outputs; this is not live LLM evaluation."}
    dst=Path(a.output);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Domain parity: {report['result']}; changed domain files: {len(differences)}")
    for key,val in checks.items(): print(key, "PASS" if val["pass"] else "FAIL")
    if differences: print("Changed domain files:",*differences,sep="\n")
    return 0 if outcome else 1

if __name__=="__main__": raise SystemExit(main())
