#!/usr/bin/env python3
from pathlib import Path
import json,re,shutil,subprocess,tempfile,yaml
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False),encoding='utf-8')
def run(project,*args): return subprocess.run(['python3',str(ROOT/'scripts/view.py'),str(project),*args],cwd=ROOT,text=True,capture_output=True)
def main():
    required=[ROOT/'examples/a27-views.yaml',ROOT/'docs/views.md',ROOT/'scripts/view.py']
    for p in required:
        if not p.is_file(): return fail(f'missing A27 artifact {p.relative_to(ROOT)}')
    schema=json.loads((ROOT/'schemas/views.schema.json').read_text())
    for typ in ('use_case_realization','integration','sequence','deployment'):
        d={'id':'VIEW-000999','name':'X','type':typ,'detail_level':'logical','notation':'neutral'}
        if list(Draft202012Validator(schema).iter_errors(d)): return fail(f'{typ} rejected by schema')
    for fn in ('use-case-realization.yaml','integration.yaml','sequence.yaml','deployment.yaml'):
        p=ROOT/'templates/system-project/views'/fn
        if not p.is_file(): return fail(f'missing A27 template {fn}')
        if list(Draft202012Validator(schema).iter_errors(yaml.safe_load(p.read_text()))): return fail(f'invalid A27 template {fn}')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'project'; shutil.copytree(ROOT/'templates/system-project',p)
        write(p/'model/context.yaml',{'elements':[
          {'id':'SYS-000001','type':'System','name':'Order System','abstraction_level':'conceptual'},
          {'id':'ACT-000001','type':'Actor','name':'Kund','abstraction_level':'conceptual','actor_kind':'role'},
          {'id':'EXT-000001','type':'ExternalSystem','name':'Payment','abstraction_level':'conceptual'}], 'relationships':[]})
        write(p/'model/functions.yaml',{'elements':[{'id':'RSP-000001','type':'Responsibility','name':'Orderhantering','abstraction_level':'conceptual'}], 'relationships':[]})
        write(p/'model/use-cases.yaml',{'elements':[{'id':'UC-000001','type':'UseCase','name':'Registrera order','abstraction_level':'conceptual','primary_actor':'ACT-000001','responsibility':'RSP-000001','outcome':'Order skapad','related_information':['INFO-000001'],'realized_by':['CMP-000001']}], 'relationships':[]})
        write(p/'model/information.yaml',{'elements':[{'id':'INFO-000001','type':'InformationObject','name':'Order','abstraction_level':'conceptual'}], 'relationships':[]})
        write(p/'model/structure.yaml',{'elements':[{'id':'CMP-000001','type':'Component','name':'Order Management','abstraction_level':'logical'},{'id':'SVC-000001','type':'Service','name':'Order Service','abstraction_level':'logical'}], 'relationships':[{'id':'REL-000001','type':'realized_by','source':'RSP-000001','target':'CMP-000001'},{'id':'REL-000002','type':'provides','source':'CMP-000001','target':'SVC-000001'}]})
        write(p/'model/integrations.yaml',{'elements':[
          {'id':'API-000001','type':'API','name':'Order API','abstraction_level':'logical','provider':'CMP-000001','consumers':['EXT-000001'],'api_style':'REST','exchanged_information':['INFO-000001']},
          {'id':'EVT-000001','type':'Event','name':'OrderCreated','abstraction_level':'logical','producer':'CMP-000001','consumers':['EXT-000001'],'communication_mode':'asynchronous','exchanged_information':['INFO-000001']}], 'relationships':[]})
        write(p/'model/data-stores.yaml',{'elements':[{'id':'DS-000001','type':'DataStore','name':'Order DB','abstraction_level':'logical','store_kind':'relational_database'}], 'relationships':[]})
        write(p/'model/deployment.yaml',{'elements':[
          {'id':'ENV-000001','type':'Environment','name':'Production','abstraction_level':'runtime','environment_kind':'production'},
          {'id':'NODE-000001','type':'DeploymentNode','name':'OpenShift','abstraction_level':'runtime','node_kind':'container_platform'},
          {'id':'RUN-000001','type':'RuntimeUnit','name':'Order API runtime','abstraction_level':'runtime','runtime_kind':'application_service'}],
          'relationships':[{'id':'REL-000010','type':'realized_as','source':'CMP-000001','target':'RUN-000001'},{'id':'REL-000011','type':'deployed_on','source':'RUN-000001','target':'NODE-000001'},{'id':'REL-000012','type':'belongs_to','source':'NODE-000001','target':'ENV-000001'},{'id':'REL-000013','type':'connects_to','source':'RUN-000001','target':'DS-000001','protocol':'JDBC'}]})
        write(p/'interactions/order.yaml',{'elements':[
          {'id':'SCN-000001','type':'Scenario','name':'Orderflöde','abstraction_level':'conceptual','use_case':'UC-000001','outcome':'Order skapad'},
          {'id':'INT-000001','type':'Interaction','name':'Registrera order','abstraction_level':'logical','scenario':'SCN-000001','participants':[{'ref':'ACT-000001'},{'ref':'CMP-000001'},{'ref':'DS-000001'}], 'messages':[{'id':'IM-000002','order':2,'sender':'CMP-000001','receiver':'DS-000001','label':'Persist order','communication_mode':'synchronous','information':['INFO-000001']},{'id':'IM-000001','order':1,'sender':'ACT-000001','receiver':'CMP-000001','label':'Submit order','communication_mode':'synchronous','information':['INFO-000001']}]}], 'relationships':[]})
        r=run(p,'--type','use_case_realization','--format','json');
        if r.returncode: return fail(r.stdout+r.stderr)
        d=json.loads(r.stdout)
        for typ in ('performs','groups_use_case','realized_by','related_information'):
            if not any(x['type']==typ for x in d['links']): return fail(f'use case realization missing {typ}')
        r=run(p,'--type','integration','--format','json'); d=json.loads(r.stdout)
        for typ in ('provides_interface','consumes_interface','publishes','subscribes','exchanges_information'):
            if not any(x['type']==typ for x in d['links']): return fail(f'integration missing {typ}')
        # Sequence must preserve message order and support filter definition.
        seqdef={'id':'VIEW-000009','name':'Seq','type':'sequence','filters':{'interaction_id':'INT-000001'}}
        write(p/'views/test-sequence.yaml',seqdef)
        r=run(p,'--definition',p/'views/test-sequence.yaml','--format','json'); d=json.loads(r.stdout)
        if [x['id'] for x in d['sequences'][0]['messages']] != ['IM-000001','IM-000002']: return fail('sequence order wrong')
        r=run(p,'--type','sequence','--format','mermaid')
        if r.returncode or 'sequenceDiagram' not in r.stdout or 'Submit order' not in r.stdout: return fail('Mermaid sequence render failed')
        r=run(p,'--type','sequence','--format','plantuml')
        if r.returncode or '@startuml' not in r.stdout or 'Submit order' not in r.stdout: return fail('PlantUML sequence render failed')
        r=run(p,'--type','deployment','--format','json'); d=json.loads(r.stdout)
        if not {'RuntimeUnit','DeploymentNode','Environment','DataStore','Component'} <= {e['type'] for e in d['elements']}: return fail('deployment elements incomplete')
        for typ in ('realized_as','deployed_on','belongs_to','connects_to'):
            if not any(x['type']==typ for x in d['links']): return fail(f'deployment missing {typ}')
        r=run(p,'--type','deployment','--format','mermaid')
        if r.returncode or 'flowchart LR' not in r.stdout or 'JDBC' not in r.stdout: return fail('Mermaid deployment render failed')
    docs=(ROOT/'docs/views.md').read_text(encoding='utf-8')
    for phrase in ('Use Case Realization View','Integration View','Sequence View','Deployment View','Mermaid','PlantUML','A28'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    v=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',v) or int(v.rsplit('.',1)[1])<27: return fail('version not A27 or later')
    print('A27 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
