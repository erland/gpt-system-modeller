#!/usr/bin/env python3
from pathlib import Path
import json, re, shutil, subprocess, tempfile, yaml
ROOT=Path(__file__).resolve().parents[1]

def fail(m): print('FAIL:',m); return 1

def run(project,*extra):
    return subprocess.run(["python3",str(ROOT/'scripts/validate.py'),str(project),*extra],cwd=ROOT,text=True,capture_output=True)

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding='utf-8')

def main():
    for p in [ROOT/'scripts/validate.py',ROOT/'docs/validation.md']:
        if not p.is_file(): return fail(f'missing A25 artifact {p.relative_to(ROOT)}')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'project'; shutil.copytree(ROOT/'templates/system-project',p)
        # A valid minimal model: context + responsibility/use case + component + info usage + runtime/deployment.
        write(p/'model/context.yaml',{'elements':[
            {'id':'SYS-000001','type':'System','name':'Order System','description':'Test','abstraction_level':'conceptual'},
            {'id':'ACT-000001','type':'Actor','name':'Kund','abstraction_level':'conceptual','actor_kind':'role'}], 'relationships':[]})
        write(p/'model/functions.yaml',{'elements':[{'id':'RSP-000001','type':'Responsibility','name':'Orderhantering','abstraction_level':'conceptual'}], 'relationships':[{'id':'REL-000001','type':'has_responsibility','source':'SYS-000001','target':'RSP-000001'}]})
        write(p/'model/use-cases.yaml',{'elements':[{'id':'UC-000001','type':'UseCase','name':'Registrera order','abstraction_level':'conceptual','primary_actor':'ACT-000001','responsibility':'RSP-000001','outcome':'Order skapad','related_information':['INFO-000001'],'realized_by':['CMP-000001']}], 'relationships':[]})
        write(p/'model/information.yaml',{'elements':[{'id':'INFO-000001','type':'InformationObject','name':'Order','abstraction_level':'conceptual'}], 'relationships':[{'id':'REL-000002','type':'creates_information','source':'UC-000001','target':'INFO-000001'}]})
        write(p/'model/structure.yaml',{'elements':[{'id':'CMP-000001','type':'Component','name':'Order Management','abstraction_level':'logical'}], 'relationships':[{'id':'REL-000003','type':'realized_by','source':'RSP-000001','target':'CMP-000001'}]})
        write(p/'model/deployment.yaml',{'elements':[
            {'id':'RUN-000001','type':'RuntimeUnit','name':'Order API','abstraction_level':'runtime','runtime_kind':'application_service'},
            {'id':'NODE-000001','type':'DeploymentNode','name':'App Platform','abstraction_level':'runtime','node_kind':'container_platform'},
            {'id':'ENV-000001','type':'Environment','name':'Production','abstraction_level':'runtime','environment_kind':'production'}], 'relationships':[
            {'id':'REL-000004','type':'deployed_on','source':'RUN-000001','target':'NODE-000001'},
            {'id':'REL-000005','type':'belongs_to','source':'NODE-000001','target':'ENV-000001'}]})
        r=run(p)
        if r.returncode!=0: return fail(f'valid project failed: {r.stdout}\n{r.stderr}')
        if 'VALIDATION_OK' not in r.stdout: return fail('success finding missing')
        rj=run(p,'--format','json')
        try: arr=json.loads(rj.stdout)
        except Exception as e: return fail(f'json output invalid: {e}: {rj.stdout}')
        if not any(x['code']=='VALIDATION_OK' for x in arr): return fail('json success finding missing')

        # Broken reference must block.
        uc=yaml.safe_load((p/'model/use-cases.yaml').read_text()); uc['elements'][0]['primary_actor']='ACT-999999'; write(p/'model/use-cases.yaml',uc)
        r=run(p)
        if r.returncode==0 or 'BROKEN_REFERENCE' not in r.stdout: return fail('broken reference not rejected')
        uc['elements'][0]['primary_actor']='ACT-000001'; write(p/'model/use-cases.yaml',uc)

        # Invalid relationship pair must block.
        rel=yaml.safe_load((p/'model/relationships.yaml').read_text()); rel['relationships']=[{'id':'REL-000010','type':'deployed_on','source':'ACT-000001','target':'NODE-000001'}]; write(p/'model/relationships.yaml',rel)
        r=run(p)
        if r.returncode==0 or 'INVALID_RELATIONSHIP_PAIR' not in r.stdout: return fail(f'invalid pair not rejected: {r.stdout}')
        rel['relationships']=[]; write(p/'model/relationships.yaml',rel)

        # Semantic warnings do not block.
        dep=yaml.safe_load((p/'model/deployment.yaml').read_text()); dep['relationships']=[x for x in dep['relationships'] if x['type']!='deployed_on']; write(p/'model/deployment.yaml',dep)
        r=run(p)
        if r.returncode!=0 or 'RUNTIME_NOT_DEPLOYED' not in r.stdout: return fail('runtime warning behavior wrong')

        # Duplicate IDs must block.
        ctx=yaml.safe_load((p/'model/context.yaml').read_text()); ctx['elements'].append({'id':'ACT-000001','type':'Actor','name':'Dublett','abstraction_level':'conceptual','actor_kind':'role'}); write(p/'model/context.yaml',ctx)
        r=run(p)
        if r.returncode==0 or 'DUPLICATE_ID' not in r.stdout: return fail('duplicate ID not rejected')

    docs=(ROOT/'docs/validation.md').read_text()
    for phrase in ('Teknisk grundvalidering','Enkel semantisk validering','WARNING','A25'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    v=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',v) or int(v.rsplit('.',1)[1])<25: return fail('version not A25 or later')
    print('A25 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
