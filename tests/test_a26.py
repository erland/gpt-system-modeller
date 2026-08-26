#!/usr/bin/env python3
from pathlib import Path
import json,re,shutil,subprocess,tempfile,yaml
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False),encoding='utf-8')
def run(project,*args): return subprocess.run(['python3',str(ROOT/'scripts/view.py'),str(project),*args],cwd=ROOT,text=True,capture_output=True)
def main():
    for p in [ROOT/'metamodel/views.yaml',ROOT/'schemas/views.schema.json',ROOT/'docs/views.md',ROOT/'scripts/view.py',ROOT/'examples/a26-views.yaml']:
        if not p.is_file(): return fail(f'missing A26 artifact {p.relative_to(ROOT)}')
    for fn in ('system-context.yaml','functional-overview.yaml','use-case-overview.yaml','information-overview.yaml','functional-information.yaml','logical-component.yaml'):
        vp=ROOT/'templates/system-project/views'/fn
        if not vp.is_file(): return fail(f'missing core view template {fn}')
        vd=yaml.safe_load(vp.read_text(encoding='utf-8'))
        if list(Draft202012Validator(json.loads((ROOT/'schemas/views.schema.json').read_text())).iter_errors(vd)): return fail(f'invalid core view template {fn}')
    schema=json.loads((ROOT/'schemas/views.schema.json').read_text())
    sample={'id':'VIEW-000123','name':'Test','type':'system_context','detail_level':'overview','notation':'neutral'}
    if list(Draft202012Validator(schema).iter_errors(sample)): return fail('valid view definition rejected')
    bad=dict(sample); bad['type']='state_machine'
    if not list(Draft202012Validator(schema).iter_errors(bad)): return fail('unsupported future view type accepted')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'project'; shutil.copytree(ROOT/'templates/system-project',p)
        write(p/'model/context.yaml',{'elements':[
          {'id':'SYS-000001','type':'System','name':'Order System','abstraction_level':'conceptual'},
          {'id':'ACT-000001','type':'Actor','name':'Kund','abstraction_level':'conceptual','actor_kind':'role'},
          {'id':'EXT-000001','type':'ExternalSystem','name':'Betaltjänst','abstraction_level':'conceptual'}],
          'relationships':[{'id':'REL-000001','type':'uses','source':'ACT-000001','target':'SYS-000001'}]})
        write(p/'model/functions.yaml',{'elements':[{'id':'RSP-000001','type':'Responsibility','name':'Orderhantering','abstraction_level':'conceptual'}],
          'relationships':[{'id':'REL-000002','type':'has_responsibility','source':'SYS-000001','target':'RSP-000001'}]})
        write(p/'model/use-cases.yaml',{'elements':[{'id':'UC-000001','type':'UseCase','name':'Registrera order','abstraction_level':'conceptual','primary_actor':'ACT-000001','responsibility':'RSP-000001','outcome':'Order skapad','related_information':['INFO-000001']}], 'relationships':[]})
        write(p/'model/information.yaml',{'elements':[{'id':'INFO-000001','type':'InformationObject','name':'Order','abstraction_level':'conceptual'}],
          'relationships':[{'id':'REL-000003','type':'creates_information','source':'UC-000001','target':'INFO-000001'}]})
        write(p/'model/structure.yaml',{'elements':[
          {'id':'SUB-000001','type':'Subsystem','name':'Orderdomän','abstraction_level':'logical'},
          {'id':'CMP-000001','type':'Component','name':'Order Management','abstraction_level':'logical'},
          {'id':'SVC-000001','type':'Service','name':'Order Service','abstraction_level':'logical'}],
          'relationships':[{'id':'REL-000004','type':'contains','source':'SUB-000001','target':'CMP-000001'},{'id':'REL-000005','type':'provides','source':'CMP-000001','target':'SVC-000001'}]})
        r=run(p,'--type','system_context','--format','json')
        if r.returncode: return fail(f'system context failed: {r.stdout} {r.stderr}')
        data=json.loads(r.stdout)
        if {e['type'] for e in data['elements']} != {'System','Actor','ExternalSystem'}: return fail('system context element selection wrong')
        r=run(p,'--type','use_case_overview','--format','json'); data=json.loads(r.stdout)
        if not any(x['type']=='performs' and x.get('derived') for x in data['links']): return fail('derived primary_actor link missing')
        if not any(x['type']=='groups_use_case' and x.get('derived') for x in data['links']): return fail('derived responsibility link missing')
        r=run(p,'--type','functional_information','--format','json'); data=json.loads(r.stdout)
        if not any(x['type']=='creates_information' and not x.get('derived') for x in data['links']): return fail('explicit information link missing')
        r=run(p,'--type','logical_component','--format','json'); data=json.loads(r.stdout)
        if {e['type'] for e in data['elements']} != {'Subsystem','Component','Service'}: return fail('logical view element selection wrong')
        # Definition-file path should work.
        r=run(p,'--definition',p/'views/system-context.yaml','--format','json')
        if r.returncode: return fail(f'definition materialization failed: {r.stdout}')
    docs=(ROOT/'docs/views.md').read_text(encoding='utf-8')
    for phrase in ('projektion av den kanoniska YAML-modellen','System Context','Functional–Information View','Logical Component View','A27'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    v=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',v) or int(v.rsplit('.',1)[1])<26: return fail('version not A26 or later')
    print('A26 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
