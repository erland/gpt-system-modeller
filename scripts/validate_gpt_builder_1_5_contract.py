#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    normalized=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    status=yaml.safe_load((ROOT/"project-status.yaml").read_text(encoding="utf-8"))
    instruction=(ROOT/project["project"]["canonical_instruction"]).read_text(encoding="utf-8")

    if normalized["builder"]["target_version"]!="1.5.0":
        errors.append("target builder version must be 1.5.0")
    if normalized["builder"]["behavior_preserving"] is not True:
        errors.append("migration must remain behavior-preserving")

    if project["project"]["canonical_instruction"]!=normalized["canonical"]["instruction"]:
        errors.append("canonical instruction path mismatch")

    capabilities={x["id"]:x for x in project["contracts"]["capabilities"]}
    for cid in normalized["contracts"]["capabilities"]["critical"]:
        if cid not in capabilities or capabilities[cid].get("critical") is not True:
            errors.append(f"critical capability mismatch: {cid}")

    canonical_artifacts={x["id"] for x in project["contracts"]["artifacts"]["canonical"]}
    for aid in normalized["contracts"]["artifacts"]["required"]:
        if aid not in canonical_artifacts:
            errors.append(f"required canonical artifact missing: {aid}")

    ws=project["contracts"]["workspace"]
    state=normalized["contracts"]["state"]
    if ws.get("source_of_truth")!=state["authority"]:
        errors.append("workspace authority mismatch")
    if ws.get("required_project_file")!=state["required_project_file"]:
        errors.append("required project file mismatch")
    if ws.get("mutation_policy")!=state["mutation_policy"]:
        errors.append("mutation policy mismatch")
    if ws.get("runtime_sequence")!=state["runtime_sequence"]:
        errors.append("runtime sequence mismatch")

    preserve=set(ws.get("preserve") or [])
    for key,val in normalized["preservation"].items():
        if val and key not in preserve:
            errors.append(f"preservation invariant missing: {key}")

    tools={x["id"]:x for x in project["contracts"]["tools"]}
    for tid in normalized["contracts"]["tools"]["required_runtime_tools"]:
        if tid not in tools or tools[tid].get("runtime_required") is not True:
            errors.append(f"required runtime tool mismatch: {tid}")
    mut=tools.get(normalized["contracts"]["tools"]["mutating_tool"],{})
    if mut.get("mode")!="mutating" or mut.get("approval_required") is not True:
        errors.append("canonical mutating tool must require approval")

    active=project["build"]["active_targets"]
    if active!=normalized["runtime_policy"]["active"]:
        errors.append("active runtime set mismatch")

    expected_parity={
        "chat":{"behavior":"ready","capabilities":"ready","artifacts":"ready"},
        "custom_gpt":{"behavior":"ready","artifacts":"ready"},
        "claude":{"behavior":"ready","artifacts":"ready"},
        "opencode":{"behavior":"ready","capabilities":"ready","artifacts":"ready","workspace_state":"ready"},
    }
    for rid,expected in expected_parity.items():
        runtime=project["runtimes"].get(rid,{})
        if runtime.get("enabled") is not True or runtime.get("compatibility")!="ready":
            errors.append(f"runtime not enabled/ready: {rid}")
        parity=runtime.get("parity",{})
        for dim,val in expected.items():
            if parity.get(dim)!=val:
                errors.append(f"{rid} parity mismatch: {dim}")

    if status.get("progress",{}).get("completed_step")!="C7" or status.get("progress",{}).get("state")!="complete":
        errors.append("Plan C status must remain complete")

    markers=[
        "kanoniska yaml-modellen",
        "påstå aldrig att ett verktyg har körts",
        "validering inte kan utföras",
        "inspect → validate → plan → change → validate → derive → package",
    ]
    folded=instruction.casefold()
    for marker in markers:
        if marker.casefold() not in folded:
            errors.append(f"canonical instruction missing invariant: {marker}")

    if errors:
        print("FAILED: GPT Builder 1.5 normalized project contract")
        for e in errors: print("-",e)
        return 1

    print("OK: GPT Builder 1.5 normalized project contract")
    print("Plan C behavior/capability/artifact/state/tool contracts preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
