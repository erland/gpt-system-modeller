#!/usr/bin/env python3
from pathlib import Path
import subprocess, tempfile, sys, yaml

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
        for rid,script in [
            ("claude","validate_claude_gpt_builder_1_5.py"),
            ("opencode","validate_opencode_gpt_builder_1_5.py"),
        ]:
            artifact=out/registry["targets"][rid]["artifact_pattern"].format(version=release)
            result=subprocess.run(
                [sys.executable,str(ROOT/"scripts"/script),"--artifact",str(artifact)],
                cwd=ROOT,text=True,capture_output=True,
            )
            if result.returncode!=0:
                print(result.stdout); print(result.stderr)
                return fail(f"{rid} GPT Builder 1.5 verification failed")

    print("GPT Builder 1.5 Claude/OpenCode regression passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
