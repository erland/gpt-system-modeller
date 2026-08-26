#!/usr/bin/env python3
from pathlib import Path
import hashlib
import subprocess
import tempfile
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]

def fail(msg):
    print('FAIL:',msg); return 1

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    script=ROOT/'scripts/package_custom_gpt.py'
    doc=ROOT/'docs/custom-gpt-builder.md'
    if not script.is_file(): return fail('missing Custom GPT builder')
    if not doc.is_file(): return fail('missing builder documentation')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        z1=td/'one.zip'; z2=td/'two.zip'; materialized=td/'tree'
        subprocess.run(['python3',str(script),'--output',str(z1),'--directory',str(materialized)],check=True,cwd=ROOT)
        subprocess.run(['python3',str(script),'--output',str(z2)],check=True,cwd=ROOT)
        if digest(z1)!=digest(z2): return fail('Custom GPT ZIP is not deterministic')
        expected=[
            'instructions.md','manifest.yaml',
            'knowledge/01-modeling-core.md','knowledge/02-metamodel-reference.md',
            'knowledge/03-project-format-and-validation.md','knowledge/04-views-and-architecture-description.md',
            'knowledge/05-source-analysis-and-evidence.md','knowledge/06-reference-example.md'
        ]
        for rel in expected:
            if not (materialized/rel).is_file(): return fail('missing generated '+rel)
        manifest=yaml.safe_load((materialized/'manifest.yaml').read_text(encoding='utf-8'))
        version=(ROOT/'VERSION').read_text().strip()
        if manifest.get('version')!=version: return fail('manifest version not from VERSION')
        if manifest.get('generator')!='scripts/package_custom_gpt.py': return fail('manifest generator missing')
        if len(manifest.get('source_hashes',{}))<10: return fail('too few canonical source hashes')
        generated=manifest.get('generated',{})
        for rel in ['instructions.md']+[f'knowledge/{Path(x).name}' for x in expected if x.startswith('knowledge/')]:
            if rel not in generated: return fail('generated manifest entry missing '+rel)
        inst=(materialized/'instructions.md').read_text(encoding='utf-8')
        for phrase in ['System Modeller','YAML','Källanalys','Kanonisk Knowledge','Osäkerhet']:
            if phrase not in inst: return fail('instructions missing '+phrase)
        # Keep the Custom GPT instruction comfortably compact; A33 can tighten policy.
        if len(inst)>12000: return fail('instructions unexpectedly large')
        with zipfile.ZipFile(z1) as zf:
            names=zf.namelist()
            if any('/tests/' in n or '/scripts/' in n or '__pycache__' in n for n in names):
                return fail('excluded development content leaked into Custom GPT ZIP')
            if not all(n.startswith('system-modeller-custom-gpt/') for n in names):
                return fail('unexpected ZIP root')
    text=doc.read_text(encoding='utf-8')
    for phrase in ['genererad projektion','manifest.yaml','byte-identiska','A33']:
        if phrase not in text: return fail('builder doc missing '+phrase)
    print('A32 tests passed'); return 0

if __name__=='__main__': raise SystemExit(main())
