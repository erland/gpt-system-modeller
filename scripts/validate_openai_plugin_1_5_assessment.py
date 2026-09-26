#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    normalized=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))
    registry=yaml.safe_load((ROOT/"runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    doc=(ROOT/"docs/openai-plugin-1.5-assessment.md").read_text(encoding="utf-8").casefold()

    plugin=normalized["runtime_policy"]["openai_plugin"]
    if plugin.get("status")!="not_active":
        errors.append("normalized plugin status must remain not_active")
    if plugin.get("target")!="reduced":
        errors.append("normalized plugin target must remain reduced")
    if plugin.get("assessment_required") is not True:
        errors.append("plugin assessment must remain required")

    rplugin=registry.get("inactive_targets",{}).get("openai_plugin",{})
    if rplugin.get("status")!="not_active":
        errors.append("registry plugin status must remain not_active")
    if rplugin.get("compatibility")!="reduced":
        errors.append("registry plugin compatibility must remain reduced")
    if rplugin.get("advisory_only") is not True:
        errors.append("registry plugin must remain advisory_only")

    if "openai_plugin" in registry.get("active_targets",[]):
        errors.append("OpenAI Plugin must not be active")
    if "openai_plugin" in registry.get("targets",{}):
        errors.append("OpenAI Plugin must not have an active build target")
    if "openai_plugin" in project["contracts"]["artifacts"]["runtime_distributions"]:
        errors.append("OpenAI Plugin must not appear in runtime distributions")

    markers=[
        "reduced / advisory only",
        "projektfilåtkomst",
        "validation before/after",
        "persistent workspace/state",
        "kontrollerad canonical mutation",
        "runtime-tool execution",
        "komplett projektpaketering",
        "unrun verification",
        "pass",
    ]
    for marker in markers:
        if marker.casefold() not in doc:
            errors.append(f"assessment missing marker: {marker}")

    if errors:
        print("FAILED: OpenAI Plugin GPT Builder 1.5 compatibility assessment")
        for e in errors: print("-",e)
        return 1

    print("OK: OpenAI Plugin remains not_active/reduced/advisory_only")
    print("No active distribution or full peer-runtime parity is claimed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
