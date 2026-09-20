#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from zipfile import ZipFile
import yaml

ROOT=Path(__file__).resolve().parents[1]
PREFIX="system-modeller-claude/"

def digest(b): return hashlib.sha256(b).hexdigest()

def read(path):
    if path.is_dir():
        return {p.relative_to(path).as_posix():p.read_bytes() for p in path.rglob("*") if p.is_file()}
    with ZipFile(path) as zf:
        return {n[len(PREFIX):]:zf.read(n) for n in zf.namelist() if n.startswith(PREFIX) and not n.endswith("/")}

def validate(path:Path):
    files=read(path); errors=[]
    required={"project-instructions.md","project/runtime-contract.json","manifest.yaml","README.md","VERSION"}
    missing=required-set(files)
    if missing: errors.append(f"missing: {sorted(missing)}")
    if errors: return errors
    manifest=yaml.safe_load(files["manifest.yaml"].decode())
    contract=json.loads(files["project/runtime-contract.json"].decode())
    if manifest.get("distribution_type")!="claude_project": errors.append("wrong distribution_type")
    if contract.get("tools",{}).get("local_script_execution")!="unavailable": errors.append("Claude must declare local scripts unavailable")
    if contract.get("tools",{}).get("canonical_mutation_requires_reliable_validation") is not True: errors.append("mutation validation gate missing")
    text=files["project-instructions.md"].decode()
    for marker in ("System Modeller","canonical YAML","Påstå därför aldrig","mutation stoppas"):
        if marker.casefold() not in text.casefold(): errors.append("missing instruction marker: "+marker)
    for rel,meta in (manifest.get("generated") or {}).items():
        if rel not in files or digest(files[rel])!=meta.get("sha256"): errors.append("generated hash mismatch: "+rel)
    for rel,expected in (manifest.get("source_hashes") or {}).items():
        p=ROOT/rel
        if not p.is_file() or digest(p.read_bytes())!=expected: errors.append("source hash mismatch: "+rel)
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--claude",type=Path,required=True); ns=ap.parse_args()
    errors=validate(ns.claude)
    for e in errors: print("ERROR",e)
    print(f"Claude validation: errors={len(errors)}")
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
