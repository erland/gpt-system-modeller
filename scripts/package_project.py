#!/usr/bin/env python3
"""Build a deterministic ZIP of a System Modeller system project."""
from __future__ import annotations
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

FIXED_DATE=(2020,1,1,0,0,0)
EXCLUDED_DIRS={'.git','__pycache__','.pytest_cache','.venv','venv'}
EXCLUDED_SUFFIXES={'.pyc','.pyo'}

def files(root:Path):
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(x in EXCLUDED_DIRS for x in rel.parts): continue
        if p.suffix in EXCLUDED_SUFFIXES or p.name=='.DS_Store': continue
        yield p,rel

def build(project:Path,out:Path):
    project=project.resolve(); out=out.resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,'w',compression=ZIP_DEFLATED,compresslevel=9) as zf:
        for p,rel in files(project):
            info=ZipInfo(f'{project.name}/{rel.as_posix()}',FIXED_DATE); info.compress_type=ZIP_DEFLATED; info.external_attr=0o644<<16
            zf.writestr(info,p.read_bytes())
    return out

def main():
    ap=argparse.ArgumentParser(description='Package a System Modeller system project deterministically')
    ap.add_argument('project',type=Path); ap.add_argument('--output',type=Path)
    ns=ap.parse_args()
    if not (ns.project/'project.yaml').is_file(): print('ERROR: project.yaml not found'); return 2
    out=ns.output or ns.project.parent/f'{ns.project.name}.zip'
    print(build(ns.project,out)); return 0
if __name__=='__main__': raise SystemExit(main())
