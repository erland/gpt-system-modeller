#!/usr/bin/env python3
"""System Modeller domain invariants independent of GPT Builder 1.5 schema."""
from pathlib import Path
import sys, yaml
ROOT=Path(__file__).resolve().parents[1]
def main():
    cfg=yaml.safe_load((ROOT/'gpt-project.yaml').read_text())
    if cfg.get('project',{}).get('id')!='system-modeller':
        raise SystemExit('Incorrect project id')
    for rel in ['instructions/chat-runtime.md','metamodel/common.yaml','metamodel/id-prefixes.yaml','schemas/common.schema.json','scripts/validate.py','scripts/ids.py']:
        if not (ROOT/rel).is_file(): raise SystemExit('Missing domain artifact: '+rel)
    expected=['INSPECT','VALIDATE','PLAN','CHANGE','VALIDATE','DERIVE','PACKAGE']
    text='\n'.join(f.read_text(errors='replace') for f in (ROOT/'instructions').rglob('*.md'))
    if not all(x in text for x in expected): raise SystemExit('Canonical Plan B steps missing from instructions')
    print('Domain project invariants OK (1.6-compatible)')
    return 0
if __name__=='__main__': sys.exit(main())
