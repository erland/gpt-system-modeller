#!/usr/bin/env python3
from pathlib import Path
import hashlib
import subprocess
import tempfile
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]

def fail(msg): print('FAIL:',msg); return 1

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    wf=ROOT/'.github/workflows/build-distributions.yml'
    builder=ROOT/'scripts/ci_build.py'
    req=ROOT/'requirements-ci.txt'
    doc=ROOT/'docs/github-actions.md'
    for p in [wf,builder,req,doc]:
        if not p.is_file(): return fail('missing A34 artifact '+str(p.relative_to(ROOT)))
    raw=wf.read_text(encoding='utf-8')
    for phrase in ['actions/checkout@v7','actions/setup-python@v7','actions/upload-artifact@v7','bash scripts/test.sh','scripts/ci_build.py','scripts/validate_custom_gpt.py','permissions:','contents: read','workflow_dispatch']:
        if phrase not in raw: return fail('workflow missing '+phrase)
    if 'contents: write' in raw: return fail('A34 workflow must not write repository contents')
    for dep in ['PyYAML','jsonschema','referencing']:
        if dep not in req.read_text(encoding='utf-8'): return fail('CI requirements missing '+dep)
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    release=version.split('-dev.',1)[0]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        out1=td/'one'; out2=td/'two'
        subprocess.run(['python3',str(builder),'--output-dir',str(out1)],cwd=ROOT,check=True)
        subprocess.run(['python3',str(builder),'--output-dir',str(out2)],cwd=ROOT,check=True)
        expected=[f'system-modeller-chat-v{release}.zip',f'system-modeller-custom-gpt-v{release}.zip','build-manifest.yaml']
        for name in expected:
            if not (out1/name).is_file(): return fail('CI builder missing '+name)
            if digest(out1/name)!=digest(out2/name): return fail('CI output not deterministic '+name)
        manifest=yaml.safe_load((out1/'build-manifest.yaml').read_text(encoding='utf-8'))
        if manifest.get('repository_version')!=version or manifest.get('release_version')!=release: return fail('build manifest version mismatch')
        arts={x['type']:x for x in manifest.get('artifacts',[])}
        for typ,name in [('chat',expected[0]),('custom_gpt',expected[1])]:
            if arts.get(typ,{}).get('file')!=name: return fail('manifest artifact mismatch '+typ)
            if arts[typ].get('sha256')!=digest(out1/name): return fail('manifest sha mismatch '+typ)
        subprocess.run(['python3',str(ROOT/'scripts/validate_custom_gpt.py'),'--custom',str(out1/expected[1]),'--chat',str(out1/expected[0])],cwd=ROOT,check=True)
    # A36 may route version resolution through a shared helper; it must remain non-hard-coded.
    chat_text=(ROOT/'scripts/package_chat.py').read_text(encoding='utf-8')
    if 'versioning.resolve' not in chat_text and "split('-dev.'" not in chat_text: return fail('Chat builder is not dynamically version-derived')
    if 'A34' not in doc.read_text(encoding='utf-8'): return fail('A34 documentation marker missing')
    print('A34 tests passed'); return 0

if __name__=='__main__': raise SystemExit(main())
