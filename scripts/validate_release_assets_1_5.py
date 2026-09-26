#!/usr/bin/env python3
from pathlib import Path
import argparse
import yaml

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"runtime-distribution-registry.yaml"

def resolve_assets(version:str):
    registry=yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    result=[]
    if registry["release"].get("include_project_artifact"):
        result.append(("project",registry["project_artifact"]["artifact_pattern"].format(version=version)))
    for rid in registry["active_targets"]:
        result.append((rid,registry["targets"][rid]["artifact_pattern"].format(version=version)))
    for key in registry["release"].get("include_derived_artifacts",[]):
        result.append((key,registry["derived_artifacts"][key]))
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--version",required=True)
    ap.add_argument("--dir",default="dist")
    ap.add_argument("--print-paths",action="store_true")
    ns=ap.parse_args()
    out=Path(ns.dir)
    if not out.is_absolute():
        out=ROOT/out
    assets=resolve_assets(ns.version)
    missing=[name for _,name in assets if not (out/name).is_file()]
    expected_zip=sorted(name for _,name in assets if name.endswith(".zip"))
    actual_zip=sorted(p.name for p in out.glob("*.zip"))
    if actual_zip!=expected_zip:
        raise SystemExit(f"FAILED: exact ZIP asset set mismatch: actual={actual_zip} expected={expected_zip}")
    if missing:
        raise SystemExit("FAILED: missing release assets: "+", ".join(missing))
    if ns.print_paths:
        for _,name in assets:
            print(out/name)
    else:
        print("OK: exact registry-driven release asset set verified")
        for typ,name in assets:
            print(f"{typ}: {name}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
