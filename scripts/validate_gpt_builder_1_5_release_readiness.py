#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    status=yaml.safe_load((ROOT/"migration-status-1.5.yaml").read_text(encoding="utf-8"))
    registry=yaml.safe_load((ROOT/"runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    contract=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))

    progress=status.get("progress",{})
    if progress.get("last_completed_step")!=9:
        errors.append("last_completed_step must be 9")
    if progress.get("completed_steps")!=list(range(1,10)):
        errors.append("completed_steps must be exactly 1..9")
    if status.get("state",{}).get("overall")!="pass":
        errors.append("overall migration state must be pass")
    if status.get("state",{}).get("blocking_issues"):
        errors.append("blocking_issues must be empty")
    if status.get("state",{}).get("warnings"):
        errors.append("warnings must be empty")

    expected=["chat","custom_gpt","claude","opencode"]
    if registry.get("active_targets")!=expected:
        errors.append("registry active target set mismatch")
    if contract.get("runtime_policy",{}).get("active")!=expected:
        errors.append("normalized contract active target set mismatch")

    plugin=registry.get("inactive_targets",{}).get("openai_plugin",{})
    if plugin.get("status")!="not_active" or plugin.get("compatibility")!="reduced" or plugin.get("advisory_only") is not True:
        errors.append("OpenAI Plugin must remain not_active/reduced/advisory_only")

    release=registry.get("release",{})
    if release.get("runtime_assets_from")!="active_targets":
        errors.append("release runtime assets must derive from active_targets")
    if release.get("wildcard_runtime_selection") is not False:
        errors.append("wildcard runtime selection must be false")

    for path in ["README.md","STATUS.md","docs/gpt-builder-1.5-runtime-migration.md"]:
        text=(ROOT/path).read_text(encoding="utf-8")
        if "GPT Byggaren 1.5" not in text:
            errors.append(f"{path} missing GPT Builder 1.5 status")

    if errors:
        print("FAILED: final GPT Builder 1.5 release readiness")
        for e in errors: print("-",e)
        return 1

    print("OK: final GPT Builder 1.5 release readiness")
    print("Migration 9/9 complete; four active runtimes; plugin advisory only; registry-driven release")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
