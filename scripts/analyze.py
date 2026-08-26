#!/usr/bin/env python3
"""Prepare deterministic source inventories for A29 LLM-based analysis.

This script intentionally does not perform semantic LLM inference. It inventories a
source tree, classifies likely architectural artifacts and emits a stable YAML packet
that a GPT/LLM can use as an analysis checklist.
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import yaml

IGNORED_DIRS={'.git','.idea','.vscode','node_modules','dist','build','target','.gradle','.next','coverage','__pycache__','.venv','venv'}
TEXT_EXT={'.md','.txt','.rst','.adoc'}
CODE_EXT={'.java','.kt','.kts','.ts','.tsx','.js','.jsx','.py','.cs','.go','.rs','.swift'}
SQL_EXT={'.sql'}
CONFIG_EXT={'.yaml','.yml','.json','.toml','.properties','.conf','.ini','.env'}

SPECIAL={
 'pom.xml':('build','high'),'build.gradle':('build','high'),'build.gradle.kts':('build','high'),
 'settings.gradle':('build','medium'),'settings.gradle.kts':('build','medium'),'package.json':('build','high'),
 'dockerfile':('deployment','high'),'docker-compose.yml':('deployment','high'),'docker-compose.yaml':('deployment','high'),
 'openapi.yaml':('api','high'),'openapi.yml':('api','high'),'openapi.json':('api','high'),
 'swagger.yaml':('api','high'),'swagger.yml':('api','high'),'asyncapi.yaml':('messaging','high'),'asyncapi.yml':('messaging','high')
}

def classify(path:Path):
    n=path.name.lower(); suf=path.suffix.lower(); parts={p.lower() for p in path.parts}
    if n in SPECIAL: return SPECIAL[n]
    if n.startswith('readme') or suf in TEXT_EXT: return ('documentation','high' if n.startswith('readme') else 'medium')
    if suf in SQL_EXT or 'migration' in parts or 'migrations' in parts: return ('database','medium')
    if suf in CODE_EXT: return ('source_code','medium')
    if suf in CONFIG_EXT:
        if any(x in parts for x in {'k8s','kubernetes','helm','deploy','deployment'}): return ('deployment','high')
        return ('configuration','low')
    return ('other','low')

def language(path:Path):
    return {'.java':'Java','.kt':'Kotlin','.kts':'Kotlin','.ts':'TypeScript','.tsx':'TypeScript','.js':'JavaScript','.jsx':'JavaScript','.py':'Python','.cs':'C#','.go':'Go','.rs':'Rust','.swift':'Swift','.sql':'SQL','.md':'Markdown','.yaml':'YAML','.yml':'YAML','.json':'JSON','.xml':'XML'}.get(path.suffix.lower())

def inventory(root:Path):
    files=[]
    for p in sorted(root.rglob('*')) if root.is_dir() else [root]:
        if not p.is_file(): continue
        rel=p.relative_to(root) if root.is_dir() else Path(p.name)
        if any(part in IGNORED_DIRS for part in rel.parts): continue
        try: data=p.read_bytes()
        except OSError: continue
        category,priority=classify(rel)
        if category=='other' and len(data)>2_000_000: continue
        files.append({'path':rel.as_posix(),'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                      'category':category,'priority':priority,**({'language':language(rel)} if language(rel) else {})})
    counts={}
    for f in files: counts[f['category']]=counts.get(f['category'],0)+1
    return {'analysis_packet':{'format':'system-modeller-analysis-inventory','root_name':root.name,'file_count':len(files),'category_counts':counts,'files':files}}

def main():
    ap=argparse.ArgumentParser(description='Prepare source material for System Modeller LLM analysis')
    sub=ap.add_subparsers(dest='cmd',required=True)
    inv=sub.add_parser('inventory'); inv.add_argument('path',type=Path); inv.add_argument('--output',type=Path)
    args=ap.parse_args()
    if args.cmd=='inventory':
        if not args.path.exists(): print(f'ERROR: path not found: {args.path}'); return 2
        packet=inventory(args.path.resolve()); text=yaml.safe_dump(packet,allow_unicode=True,sort_keys=False)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text,encoding='utf-8')
        else: print(text.rstrip())
    return 0
if __name__=='__main__': raise SystemExit(main())
