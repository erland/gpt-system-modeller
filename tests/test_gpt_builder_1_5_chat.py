#!/usr/bin/env python3
from pathlib import Path
import subprocess
import tempfile
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]

def fail(message):
    print("FAIL:",message)
    return 1

def main():
    registry=yaml.safe_load((ROOT/"runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    version=(ROOT/"VERSION").read_text(encoding="utf-8").strip()
    release=version.split("-dev.",1)[0]

    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/"dist"
        subprocess.run([sys.executable,str(ROOT/"scripts/ci_build.py"),"--output-dir",str(out)],cwd=ROOT,check=True)
        artifact=out/registry["targets"]["chat"]["artifact_pattern"].format(version=release)
        result=subprocess.run(
            [sys.executable,str(ROOT/"scripts/validate_chat_gpt_builder_1_5.py"),"--artifact",str(artifact)],
            cwd=ROOT,text=True,capture_output=True,
        )
        if result.returncode!=0:
            print(result.stdout); print(result.stderr)
            return fail("Chat ZIP GPT Builder 1.5 verification failed")

    print("GPT Builder 1.5 Chat ZIP regression passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
