#!/usr/bin/env python3
"""A37: release events and guarded five-target GitHub workflows."""
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("chat", "plugin", "claude-project", "claude-skills", "opencode")
def run(*args):
    return subprocess.run([sys.executable, *map(str,args)], cwd=ROOT, text=True, capture_output=True)
def main_error(result):
    if result.returncode:
        print(result.stdout, result.stderr)
    return result.returncode

def main():
    sys.path.insert(0,str(ROOT/"scripts"))
    import versioning
    ctx={"GITHUB_EVENT_NAME":"release","GITHUB_EVENT_RELEASE_TAG_NAME":"v3.4.5"}
    info=versioning.resolve(env=ctx)
    assert (info.release_version,info.source,info.tag)==("3.4.5","github_release","v3.4.5")
    conflict=versioning.resolve(env=dict(ctx,GITHUB_REF_TYPE="tag",GITHUB_REF_NAME="v9.9.9"))
    assert conflict.release_version=="3.4.5"
    ci=(ROOT/".github/workflows/ci.yml").read_text(encoding="utf-8")
    release=(ROOT/".github/workflows/release.yml").read_text(encoding="utf-8")
    for value in ("pull_request:","standalone-abc:","validate-and-build:","needs: [standalone-abc, behavior-parity]","validate_distributions.py"):
        assert value in ci, f"CI lacks {value}"
    for value in ("types: [published]","contents: write","build_distributions.py","validate_distributions.py","gh release upload"):
        assert value in release, f"Release lacks {value}"
    assert "ci_build.py" not in release and "custom-gpt" not in release.lower()
    print("A37 release workflow PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
