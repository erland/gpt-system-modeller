#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]

def fail(message):
    print("FAIL:",message)
    return 1

def main():
    normalized=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))
    migration=yaml.safe_load((ROOT/"migration-status-1.5.yaml").read_text(encoding="utf-8"))

    if normalized.get("builder",{}).get("target_version")!="1.5.0":
        return fail("normalized contract target must be 1.5.0")
    if normalized.get("builder",{}).get("behavior_preserving") is not True:
        return fail("migration must remain behavior-preserving")

    result=subprocess.run(
        [sys.executable,str(ROOT/"scripts/validate_gpt_builder_1_5_contract.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode!=0:
        print(result.stdout)
        print(result.stderr)
        return fail("GPT Builder 1.5 normalized contract validation failed")

    if migration.get("preservation",{}).get("preserve_plan_c") is not True:
        return fail("Plan C preservation must remain explicit")

    print("GPT Builder 1.5 normalized contract regression passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
