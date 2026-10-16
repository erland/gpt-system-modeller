#!/usr/bin/env python3
"""A38: development/release versions and deterministic canonical ZIP output."""
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

import hashlib
def main():
    sys.path.insert(0,str(ROOT/"scripts"))
    import versioning
    dev=(ROOT/"VERSION").read_text(encoding="utf-8").strip()
    assert versioning.normalize_distribution_version(dev)==dev
    assert versioning.normalize_distribution_version("1.2.3")=="1.2.3"
    for invalid in ("v1.2.3-dev.4","1.2","1.2.3-beta","release-1.2.3"):
        try: versioning.normalize_distribution_version(invalid)
        except ValueError: pass
        else: raise AssertionError(f"Invalid version: {invalid}")
    cfg=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    version="0.1.0-a38"
    def build():
        result=run(ROOT/"scripts/build_distributions.py","--project-root",ROOT,"--version",version)
        if main_error(result): raise AssertionError("Canonical build failed")
        names={}
        for target in TARGETS:
            pattern=cfg["build_system"]["runtime_targets"][target]["filename_pattern"]
            name=pattern.replace("<project-id>",cfg["project"]["id"]).replace("<version>",version)
            names[target]=hashlib.sha256((ROOT/"dist"/name).read_bytes()).hexdigest()
        return names
    assert build()==build(), "Canonical ZIP outputs are not deterministic"
    print("A38 deterministic modern distribution build PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
