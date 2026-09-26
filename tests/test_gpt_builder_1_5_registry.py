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
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))

    if registry["active_targets"]!=["chat","custom_gpt","claude","opencode"]:
        return fail("unexpected active runtime set")
    if registry["active_targets"]!=project["build"]["active_targets"]:
        return fail("registry and project active targets differ")

    result=subprocess.run(
        [sys.executable,str(ROOT/"scripts/validate_runtime_distribution_registry.py")],
        cwd=ROOT,text=True,capture_output=True,
    )
    if result.returncode!=0:
        print(result.stdout); print(result.stderr)
        return fail("runtime distribution registry validation failed")

    ci=(ROOT/"scripts/ci_build.py").read_text(encoding="utf-8")
    if 'REGISTRY = ROOT / "runtime-distribution-registry.yaml"' not in ci:
        return fail("ci_build does not use runtime distribution registry")
    if 'registry["targets"][runtime_id]["artifact_pattern"]' not in ci:
        return fail("ci_build does not derive runtime artifact names from registry")

    print("GPT Builder 1.5 runtime registry regression passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
