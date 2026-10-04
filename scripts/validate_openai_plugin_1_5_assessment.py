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
    if plugin.get("status")!="active":
        errors.append("normalized plugin status must be active")
    if plugin.get("target")!="equivalent_runtime_dependent":
        errors.append("normalized plugin target must be equivalent_runtime_dependent")
    if plugin.get("assessment_required") is not True:
        errors.append("plugin assessment must remain required")

    rplugin=registry.get("targets",{}).get("openai_plugin",{})
    if rplugin.get("status")!="active":
        errors.append("registry plugin status must be active")
    if rplugin.get("compatibility")!="equivalent_runtime_dependent":
        errors.append("registry plugin compatibility must be equivalent_runtime_dependent")

    if "openai_plugin" not in registry.get("active_targets",[]):
        errors.append("OpenAI Plugin must be active")
    if "openai_plugin" not in project["contracts"]["artifacts"]["runtime_distributions"]:
        errors.append("OpenAI Plugin must appear in runtime distributions")
    runtime=project.get("runtimes",{}).get("openai_plugin",{})
    if runtime.get("enabled") is not True:
        errors.append("OpenAI Plugin runtime must be enabled")

    markers=[
        "equivalent_runtime_dependent",
        "projektfilåtkomst",
        "validation before/after",
        "persistent workspace/state",
        "kontrollerad canonical mutation",
        "python",
        "runtime-tool execution",
        "komplett projektpaketering",
        "unrun verification",
        "pass",
        "approval",
    ]
    for marker in markers:
        if marker.casefold() not in doc:
            errors.append(f"assessment missing marker: {marker}")

    if errors:
        print("FAILED: OpenAI Plugin GPT Builder 1.5 compatibility assessment")
        for e in errors: print("-",e)
        return 1

    print("OK: OpenAI Plugin active/equivalent_runtime_dependent")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
