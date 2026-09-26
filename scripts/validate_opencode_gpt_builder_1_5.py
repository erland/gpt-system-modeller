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
    runtime=project["runtimes"]["opencode"]

    with zipfile.ZipFile(artifact) as zf:
        if zf.testzip():
            errors.append("OpenCode ZIP is corrupt")
        contract=json.loads(zf.read(member(zf,".opencode/runtime-contract.json")).decode("utf-8"))
        config=json.loads(zf.read(member(zf,"opencode.json")).decode("utf-8"))
        agents=zf.read(member(zf,"AGENTS.md")).decode("utf-8").casefold()

        if contract.get("workspace_state")!="ready":
            errors.append("OpenCode workspace_state must remain ready")
        target=contract.get("target_project",{})
        if target.get("project_root_argument")!="projectRoot":
            errors.append("OpenCode must expose explicit projectRoot")

        expected={
            "system_context","system_validate","system_model","system_view",
            "system_report","system_package","system_analyze"
        }
        tools={x.get("id"):x for x in contract.get("tools",[])}
        if set(tools)!=expected:
            errors.append("OpenCode typed tool set mismatch")
        for tid,tool in tools.items():
            if tid=="system_model":
                if tool.get("permission")!="ask" or tool.get("mutates_workspace") is not True:
                    errors.append("system_model must mutate with ask approval")
            else:
                if tool.get("permission")!="allow":
                    errors.append(f"{tid} must be allowed")

        permissions={
            (x.get("action"),x.get("resource")):x.get("effect")
            for x in config.get("permissions",[]) if isinstance(x,dict)
        }
        if permissions.get(("system_model","*"))!="ask":
            errors.append("OpenCode config must require ask for system_model")
        if permissions.get(("shell","*"))!="ask":
            errors.append("OpenCode shell permission must remain ask")
        if permissions.get(("edit","*"))!="ask":
            errors.append("OpenCode edit permission must remain ask")

        for tid in expected:
            try:
                wrapper=zf.read(member(zf,f".opencode/tools/{tid}.ts")).decode("utf-8")
                if "tool.schema" not in wrapper:
                    errors.append(f"{tid} wrapper lacks typed schema")
                if tid!="system_analyze" and "projectRoot" not in wrapper:
                    errors.append(f"{tid} wrapper lacks projectRoot")
            except ValueError as exc:
                errors.append(str(exc))

        for marker in [
            "projectroot explicit",
            "mutating model operations require approval",
            "canonical model",
        ]:
            if marker.casefold() not in agents:
                errors.append(f"OpenCode AGENTS missing marker: {marker}")

    parity=runtime["parity"]
    if runtime.get("local_tools")!="declared_custom_tools":
        errors.append("OpenCode local_tools must remain declared_custom_tools")
    if parity.get("workspace_state")!="ready":
        errors.append("OpenCode workspace_state parity must remain ready")
    if parity.get("tools")!="declared_custom_tools":
        errors.append("OpenCode tool parity must remain declared_custom_tools")

    if errors:
        print("FAILED: OpenCode GPT Builder 1.5 verification")
        for e in errors: print("-",e)
        return 1
    print("OK: OpenCode GPT Builder 1.5 verification")
    print("Equivalent workspace/tool parity, typed tools, projectRoot and approvals preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
