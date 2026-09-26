#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"runtime-distribution-registry.yaml"

VALIDATORS={
    "chat":"validate_chat_gpt_builder_1_5.py",
    "custom_gpt":"validate_custom_gpt_builder_1_5.py",
    "claude":"validate_claude_gpt_builder_1_5.py",
    "opencode":"validate_opencode_gpt_builder_1_5.py",
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--version",required=True)
    ap.add_argument("--dir",default="dist")
    ns=ap.parse_args()

    registry=yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    out=Path(ns.dir)
    if not out.is_absolute():
        out=ROOT/out

    active=registry["active_targets"]
    if set(active)!=set(VALIDATORS):
        raise SystemExit(f"FAILED: no exact 1.5 validator mapping for active runtimes: {active}")

    subprocess.run([sys.executable,str(ROOT/"scripts/validate_gpt_builder_1_5_contract.py")],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/validate_runtime_distribution_registry.py")],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/validate_openai_plugin_1_5_assessment.py")],cwd=ROOT,check=True)

    for rid in active:
        artifact=out/registry["targets"][rid]["artifact_pattern"].format(version=ns.version)
        subprocess.run(
            [sys.executable,str(ROOT/"scripts"/VALIDATORS[rid]),"--artifact",str(artifact)],
            cwd=ROOT,check=True,
        )

    print("OK: all active GPT Builder 1.5 runtime artifacts verified from registry")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
