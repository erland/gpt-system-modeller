#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    result=subprocess.run(
        [sys.executable,str(ROOT/"scripts/validate_gpt_builder_1_5_release_readiness.py")],
        cwd=ROOT,text=True,capture_output=True,
    )
    if result.returncode!=0:
        print(result.stdout); print(result.stderr)
        print("FAIL: final GPT Builder 1.5 release readiness")
        return 1
    print("GPT Builder 1.5 final release readiness regression passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
