#!/usr/bin/env python3
"""A36: version parsing and artifact naming under the canonical builder."""
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
    sys.path.insert(0,str(ROOT/"scripts"))
    import versioning
    assert versioning.normalize_release("v2.3.4")=="2.3.4"
    for invalid in ("v1.2","release-1.2.3","v1.2.3-beta"):
        try: versioning.normalize_release(invalid)
        except ValueError: pass
        else: raise AssertionError(f"Invalid release accepted: {invalid}")
    tag=versioning.resolve(env={"GITHUB_REF_TYPE":"tag","GITHUB_REF_NAME":"v2.3.4"})
    assert (tag.release_version,tag.source)==("2.3.4","github_tag")
    cfg=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    targets=cfg["build_system"]["runtime_targets"]
    for target in TARGETS:
        name=targets[target]["filename_pattern"].replace("<project-id>",cfg["project"]["id"]).replace("<version>","2.3.4")
        assert "2.3.4" in name and name.endswith(".zip")
    assert "custom_gpt" not in targets
    print("A36 version contract PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
