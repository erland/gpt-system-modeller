#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    registry=yaml.safe_load((ROOT/"runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    normalized=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))

    if registry["builder_contract"]["target_version"]!="1.5.0":
        errors.append("registry builder target must be 1.5.0")
    if registry["builder_contract"]["normalized_contract"]!="gpt-builder-1.5-contract.yaml":
        errors.append("registry normalized contract mismatch")
    if registry["builder_contract"]["runtime_selection"]!="active_targets":
        errors.append("runtime selection must use active_targets")
    if registry["builder_contract"]["artifact_policy"]!="exact_active_target_set":
        errors.append("artifact policy must be exact_active_target_set")

    active=registry.get("active_targets") or []
    if active!=project["build"]["active_targets"]:
        errors.append("registry active targets differ from gpt-project.yaml")
    if active!=normalized["runtime_policy"]["active"]:
        errors.append("registry active targets differ from 1.5 normalized contract")

    for rid in active:
        target=registry["targets"].get(rid,{})
        runtime=project["runtimes"].get(rid,{})
        if target.get("status")!="active":
            errors.append(f"{rid}: registry status must be active")
        if target.get("source_runtime")!=rid:
            errors.append(f"{rid}: source_runtime mismatch")
        if target.get("artifact_pattern")!=runtime.get("artifact_pattern"):
            errors.append(f"{rid}: artifact pattern mismatch")

    plugin=registry.get("inactive_targets",{}).get("openai_plugin",{})
    if plugin.get("status")!="not_active" or plugin.get("compatibility")!="reduced":
        errors.append("OpenAI Plugin baseline must remain not_active/reduced")

    release=registry.get("release",{})
    if release.get("runtime_assets_from")!="active_targets":
        errors.append("release runtime assets must derive from active_targets")
    if release.get("wildcard_runtime_selection") is not False:
        errors.append("wildcard runtime selection must be false")

    derived=registry.get("derived_artifacts",{})
    expected={"runtime_parity":"runtime-parity.yaml","checksums":"SHA256SUMS.txt","manifest":"build-manifest.yaml"}
    if derived!=expected:
        errors.append("derived artifact registry mismatch")

    if errors:
        print("FAILED: GPT Builder 1.5 runtime distribution registry")
        for e in errors: print("-",e)
        return 1

    print("OK: GPT Builder 1.5 runtime distribution registry")
    print("Four active runtimes and artifact patterns are synchronized with gpt-project.yaml")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
