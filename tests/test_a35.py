#!/usr/bin/env python3
"""A35: canonical five-target release readiness (replaces legacy Custom GPT readiness)."""
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("chat", "plugin", "claude_project", "claude_skills", "opencode")
def run(*args):
    return subprocess.run([sys.executable, *map(str,args)], cwd=ROOT, text=True, capture_output=True)
def main_error(result):
    if result.returncode:
        print(result.stdout, result.stderr)
    return result.returncode

def main():
    cfg=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    targets=cfg["build_system"]["runtime_targets"]
    assert set(TARGETS).issubset(targets), "All five runtime targets must be declared"
    assert cfg["runtime"]["custom_gpt"]["enabled"] is False
    with tempfile.TemporaryDirectory() as tmp:
        # Builds use the modern canonical builder; do not use ci_build.py.
        version="0.1.0-a35"
        result=run(ROOT/"scripts/build_distributions.py","--project-root",ROOT,"--version",version)
        if main_error(result): return 1
        dist=ROOT/"dist"
        for target in TARGETS:
            pattern=targets[target]["filename_pattern"]
            filename=pattern.replace("<project-id>",cfg["project"]["id"]).replace("<version>",version)
            assert (dist/filename).is_file(), f"Missing canonical artifact: {filename}"
            with zipfile.ZipFile(dist/filename) as z:
                assert z.testzip() is None
        check=run(ROOT/"scripts/validate_distributions.py","--project-root",ROOT)
        if main_error(check): return 1
    print("A35 canonical release readiness PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
