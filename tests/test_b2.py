#!/usr/bin/env python3
from pathlib import Path
import json, shutil, subprocess, tempfile, yaml
ROOT=Path(__file__).resolve().parents[1]

def fail(m):
    print('FAIL:',m); return 1

def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False),encoding='utf-8')

def main():
    required=(ROOT/'scripts/context.py',ROOT/'docs/context-summary.md')
    for p in required:
        if not p.is_file(): return fail(f'missing B2 artifact {p.relative_to(ROOT)}')
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'project'
        shutil.copytree(ROOT/'templates/system-project',project)
        manifest=yaml.safe_load((project/'project.yaml').read_text(encoding='utf-8'))
        manifest['project']['name']='Context Test'
        write(project/'project.yaml',manifest)
        write(project/'model/context.yaml',{'elements':[
            {'id':'SYS-000001','type':'System','name':'Context Test','description':'Testsystem','abstraction_level':'conceptual','origin':['declared'],'evidence':['EVD-000001']},
            {'id':'ACT-000001','type':'Actor','name':'Kund','abstraction_level':'conceptual','actor_kind':'role','origin':['declared'],'evidence':['EVD-000001']}
        ],'relationships':[]})
        write(project/'model/structure.yaml',{'elements':[
            {'id':'CMP-000001','type':'Component','name':'Order API','abstraction_level':'logical','origin':['inferred']},
            {'id':'CMP-000002','type':'Component','name':'Order API','abstraction_level':'logical','origin':['unresolved']}
        ],'relationships':[]})
        write(project/'sources/sources.yaml',{'elements':[{'id':'SRC-000001','type':'Source','name':'User input','source_kind':'user_input','location':'chat'}],'relationships':[]})
        write(project/'sources/references.yaml',{'elements':[{'id':'REF-000001','type':'SourceReference','name':'User statement','source':'SRC-000001','locator':'chat'}],'relationships':[]})
        write(project/'sources/evidence.yaml',{'elements':[{'id':'EVD-000001','type':'Evidence','name':'User evidence','source_ref':'REF-000001','status':'user_confirmed','confidence':'high'}],'relationships':[]})
        r=subprocess.run(['python3',str(ROOT/'scripts/context.py'),str(project),'--format','json','--focus','Order'],cwd=ROOT,text=True,capture_output=True)
        if r.returncode not in (0,1): return fail(r.stdout+r.stderr)
        data=json.loads(r.stdout)
        if data.get('context_format')!='system-modeller-working-context-v1': return fail('wrong context format')
        if data['project']['name']!='Context Test': return fail('project metadata missing')
        if data['summary']['element_types'].get('Component')!=2: return fail('component count wrong')
        if not any(x['path']=='model/structure.yaml' for x in data['canonical_files']): return fail('canonical file inventory missing')
        if not any(x['id']=='CMP-000001' for x in data['focus']['matches']): return fail('focus match missing')
        if not data['duplicate_name_candidates']: return fail('duplicate candidate missing')
        counts=data['uncertainty']['counts']
        if counts.get('inferred',0)<1 or counts.get('unresolved',0)<1 or counts.get('no_evidence',0)<1: return fail('uncertainty summary incomplete')
        expected=['INSPECT','VALIDATE','PLAN','CHANGE','VALIDATE','DERIVE','PACKAGE']
        if data['runtime_contract']['next_operations']!=expected: return fail('runtime order missing')
        r2=subprocess.run(['python3',str(ROOT/'scripts/context.py'),str(project),'--format','json','--focus','Order'],cwd=ROOT,text=True,capture_output=True)
        if r.stdout!=r2.stdout: return fail('context output is not deterministic')
    print('B2 tests passed'); return 0

if __name__=='__main__': raise SystemExit(main())
