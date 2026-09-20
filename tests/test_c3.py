#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, tempfile, yaml, zipfile, json, re
ROOT=Path(__file__).resolve().parents[1]

def fail(m): print("FAIL:",m); return 1
def dg(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    for rel in ("templates/claude-project-distribution.yaml","scripts/package_claude.py","scripts/validate_claude.py","docs/claude-project-distribution.md"):
        if not (ROOT/rel).is_file(): return fail("missing "+rel)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); z1=td/"one.zip"; z2=td/"two.zip"; tree=td/"tree"
        subprocess.run(["python3",str(ROOT/"scripts/package_claude.py"),"--output",str(z1),"--directory",str(tree)],check=True,cwd=ROOT)
        subprocess.run(["python3",str(ROOT/"scripts/package_claude.py"),"--output",str(z2)],check=True,cwd=ROOT)
        if dg(z1)!=dg(z2): return fail("Claude ZIP is not deterministic")
        subprocess.run(["python3",str(ROOT/"scripts/validate_claude.py"),"--claude",str(z1)],check=True,cwd=ROOT)
        contract=json.loads((tree/"project/runtime-contract.json").read_text())
        if contract["tools"]["local_script_execution"]!="unavailable": return fail("tool reduction missing")
        if not contract["tools"]["canonical_mutation_requires_reliable_validation"]: return fail("validation gate missing")
        manifest=yaml.safe_load((tree/"manifest.yaml").read_text())
        if manifest.get("distribution_type")!="claude_project": return fail("wrong manifest type")
    status=yaml.safe_load((ROOT/"project-status.yaml").read_text())
    m=re.fullmatch(r"C([1-7])",status["progress"]["completed_step"])
    if not m or int(m.group(1))<3: return fail("status predates C3")
    print("C3 Claude distribution tests passed"); return 0
if __name__=="__main__": raise SystemExit(main())
