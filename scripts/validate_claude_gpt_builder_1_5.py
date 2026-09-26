#!/usr/bin/env python3
from pathlib import Path
import argparse, json, zipfile, yaml

ROOT=Path(__file__).resolve().parents[1]

def member(zf,suffix):
    m=[n for n in zf.namelist() if n.endswith("/"+suffix) or n==suffix]
    if len(m)!=1: raise ValueError(f"expected one {suffix}, found {m}")
    return m[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",required=True)
    a=ap.parse_args()
    artifact=Path(a.artifact)
    if not artifact.is_absolute():
        artifact=ROOT/artifact

    errors=[]
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    runtime=project["runtimes"]["claude"]

    with zipfile.ZipFile(artifact) as zf:
        if zf.testzip():
            errors.append("Claude ZIP is corrupt")
        try:
            instruction=zf.read(member(zf,"project-instructions.md")).decode("utf-8").casefold()
            for marker in [
                "ingen lokal exekvering",
                "påstå därför aldrig att scripts har körts",
                "canonical mutation stoppas",
                "inspect → validate → plan → change → validate → derive → package",
            ]:
                if marker.casefold() not in instruction:
                    errors.append(f"Claude instruction missing reduced-runtime marker: {marker}")
        except ValueError as exc:
            errors.append(str(exc))

        try:
            contract=json.loads(zf.read(member(zf,"project/runtime-contract.json")).decode("utf-8"))
            if contract.get("workspace_state")!="reduced":
                errors.append("Claude workspace_state must remain reduced")
            tools=contract.get("tools",{})
            if tools.get("local_script_execution")!="unavailable":
                errors.append("Claude local scripts must remain unavailable")
            if tools.get("canonical_mutation_requires_reliable_validation") is not True:
                errors.append("Claude mutation validation gate missing")
        except ValueError as exc:
            errors.append(str(exc))

        names=zf.namelist()
        if any("/scripts/" in "/"+n for n in names):
            errors.append("Claude Project must not package executable repository scripts")

    parity=runtime["parity"]
    if runtime.get("local_tools")!="unavailable":
        errors.append("Claude project contract local_tools must remain unavailable")
    if parity.get("workspace_state")!="reduced":
        errors.append("Claude project workspace_state parity must remain reduced")
    if parity.get("tools")!="unavailable":
        errors.append("Claude project tool parity must remain unavailable")
    if parity.get("capabilities")!="ready_with_fallbacks":
        errors.append("Claude capability parity must remain ready_with_fallbacks")

    if errors:
        print("FAILED: Claude Project GPT Builder 1.5 verification")
        for e in errors: print("-",e)
        return 1
    print("OK: Claude Project GPT Builder 1.5 verification")
    print("Reduced workspace/tool parity and mutation stop rules preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
