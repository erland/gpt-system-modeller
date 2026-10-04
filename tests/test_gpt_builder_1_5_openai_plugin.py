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
    registry=yaml.safe_load((ROOT/"runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    if "openai_plugin" not in registry["active_targets"]:
        return fail("OpenAI Plugin must be active")
    plugin=registry["targets"].get("openai_plugin",{})
    if plugin.get("compatibility")!="equivalent_runtime_dependent":
        return fail("OpenAI Plugin compatibility mismatch")
    result=subprocess.run(
        [sys.executable,str(ROOT/"scripts/validate_openai_plugin_1_5_assessment.py")],
        cwd=ROOT,text=True,capture_output=True,
    )
    if result.returncode!=0:
        print(result.stdout); print(result.stderr)
        return fail("OpenAI Plugin 1.5 assessment validation failed")
    print("GPT Builder 1.5 OpenAI Plugin active-runtime assessment regression passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
