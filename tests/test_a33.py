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
    validator=ROOT/'scripts/validate_custom_gpt.py'
    doc=ROOT/'docs/custom-gpt-validation.md'
    if not validator.is_file(): return fail('missing A33 validator')
    if not doc.is_file(): return fail('missing A33 documentation')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        custom=td/'custom.zip'; chat=td/'chat.zip'; tree=td/'custom-tree'
        subprocess.run(['python3',str(ROOT/'scripts/package_custom_gpt.py'),'--output',str(custom),'--directory',str(tree)],check=True,cwd=ROOT)
        subprocess.run(['python3',str(ROOT/'scripts/package_chat.py'),'--output',str(chat)],check=True,cwd=ROOT)
        subprocess.run(['python3',str(validator),'--custom',str(custom),'--chat',str(chat)],check=True,cwd=ROOT)
        inst=(tree/'instructions.md').read_text(encoding='utf-8')
        if len(inst)>8000: return fail('instruction exceeds A33 budget')
        manifest=yaml.safe_load((tree/'manifest.yaml').read_text(encoding='utf-8'))
        for base in ['metamodel','schemas']:
            for p in sorted((ROOT/base).glob('*')):
                if p.is_file():
                    rel=p.relative_to(ROOT).as_posix()
                    if rel not in manifest.get('source_hashes',{}): return fail('parity source missing '+rel)
        # Tampering with a generated file must fail.
        bad=td/'bad.zip'
        with zipfile.ZipFile(custom) as zin, zipfile.ZipFile(bad,'w') as zout:
            for info in zin.infolist():
                data=zin.read(info.filename)
                if info.filename.endswith('/instructions.md'):
                    data += b'\nTAMPERED\n'
                zout.writestr(info,data)
        rc=subprocess.run(['python3',str(validator),'--custom',str(bad),'--chat',str(chat)],cwd=ROOT,stdout=subprocess.DEVNULL).returncode
        if rc==0: return fail('tampered Custom GPT unexpectedly validated')
        # Chat metamodel tampering must also fail parity.
        badchat=td/'bad-chat.zip'
        with zipfile.ZipFile(chat) as zin, zipfile.ZipFile(badchat,'w') as zout:
            changed=False
            for info in zin.infolist():
                data=zin.read(info.filename)
                if not changed and '/metamodel/' in info.filename and info.filename.endswith('.yaml'):
                    data += b'\n# tampered\n'; changed=True
                zout.writestr(info,data)
        rc=subprocess.run(['python3',str(validator),'--custom',str(custom),'--chat',str(badchat)],cwd=ROOT,stdout=subprocess.DEVNULL).returncode
        if rc==0: return fail('tampered Chat parity unexpectedly validated')
    text=doc.read_text(encoding='utf-8')
    for phrase in ['8 000','metamodel/','schemas/','SHA-256','shared_capabilities']:
        if phrase not in text: return fail('A33 doc missing '+phrase)
    print('A33 tests passed'); return 0

if __name__=='__main__': raise SystemExit(main())
