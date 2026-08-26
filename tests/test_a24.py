#!/usr/bin/env python3
from pathlib import Path
import shutil, subprocess, tempfile, yaml, re
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1

def run(*args):
    return subprocess.run(["python3", *map(str,args)], cwd=ROOT, text=True, capture_output=True)

def main():
    for p in [ROOT/'scripts/ids.py',ROOT/'scripts/model.py',ROOT/'docs/model-operations.md']:
        if not p.is_file(): return fail(f'missing A24 artifact: {p.relative_to(ROOT)}')
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'project'; shutil.copytree(ROOT/'templates/system-project',project)
        r=run(ROOT/'scripts/ids.py',project,'--type','Component')
        if r.returncode or r.stdout.strip()!='CMP-000001': return fail(f'bad initial component ID: {r.stdout} {r.stderr}')
        r=run(ROOT/'scripts/model.py',project,'add','--json','{"type":"Component","name":"Order Management","abstraction_level":"logical"}')
        if r.returncode or 'CMP-000001' not in r.stdout: return fail(f'add failed: {r.stdout} {r.stderr}')
        r=run(ROOT/'scripts/ids.py',project,'--type','Component')
        if r.stdout.strip()!='CMP-000002': return fail('ID allocation did not advance')
        r=run(ROOT/'scripts/model.py',project,'update','CMP-000001','--json','{"name":"Order Core"}')
        if r.returncode or 'Order Core' not in r.stdout: return fail('update failed')
        r=run(ROOT/'scripts/model.py',project,'find','CMP-000001')
        if r.returncode or 'Order Core' not in r.stdout: return fail('find failed after rename')
        r=run(ROOT/'scripts/model.py',project,'update','CMP-000001','--json','{"id":"CMP-999999"}')
        if r.returncode==0: return fail('stable ID change was accepted')
        r=run(ROOT/'scripts/model.py',project,'add','--json','{"type":"Service","name":"Order Query","abstraction_level":"logical"}')
        if r.returncode: return fail('service add failed')
        r=run(ROOT/'scripts/model.py',project,'add-relation','--json','{"type":"provides","source":"CMP-000001","target":"SVC-000001"}')
        if r.returncode or 'REL-000001' not in r.stdout: return fail('relationship add failed')
        r=run(ROOT/'scripts/model.py',project,'delete','CMP-000001')
        if r.returncode==0: return fail('delete with referencing relationship should be blocked')
        r=run(ROOT/'scripts/model.py',project,'delete-relation','REL-000001')
        if r.returncode: return fail('delete relationship failed')
        r=run(ROOT/'scripts/model.py',project,'delete','CMP-000001')
        if r.returncode: return fail('delete element failed after relationship removal')
        r=run(ROOT/'scripts/model.py',project,'find','CMP-000001')
        if r.returncode!=2: return fail('deleted element still found')
        shard=yaml.safe_load((project/'model/structure.yaml').read_text())
        if any(e.get('id')=='CMP-000001' for e in shard['elements']): return fail('deleted component remains in shard')
    docs=(ROOT/'docs/model-operations.md').read_text()
    for phrase in ('Stabil identitet','Kanoniska shards','--force','A25'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<24: return fail('version not A24 or later')
    print('A24 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
