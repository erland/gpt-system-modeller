#!/usr/bin/env python3
from pathlib import Path
import re,shutil,subprocess,tempfile,yaml
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False),encoding='utf-8')
def main():
    for p in (ROOT/'scripts/report.py',ROOT/'docs/architecture-description.md',ROOT/'templates/system-project/reports/architecture-description.yaml'):
        if not p.is_file(): return fail(f'missing A28 artifact {p.relative_to(ROOT)}')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'project'; shutil.copytree(ROOT/'templates/system-project',p)
        manifest=yaml.safe_load((p/'project.yaml').read_text()); manifest['project']['name']='Order System'; manifest['project']['description']='Hanterar kundorder från registrering till lagring.'; write(p/'project.yaml',manifest)
        write(p/'model/context.yaml',{'elements':[
          {'id':'SYS-000001','type':'System','name':'Order System','description':'Hanterar kundorder.','abstraction_level':'conceptual','origin':['declared']},
          {'id':'ACT-000001','type':'Actor','name':'Kund','abstraction_level':'conceptual','actor_kind':'role','origin':['declared']},
          {'id':'EXT-000001','type':'ExternalSystem','name':'Payment','abstraction_level':'conceptual','origin':['declared']}], 'relationships':[]})
        write(p/'model/functions.yaml',{'elements':[{'id':'RSP-000001','type':'Responsibility','name':'Orderhantering','description':'Ansvarar för orderns livscykel.','abstraction_level':'conceptual','origin':['declared']}], 'relationships':[]})
        write(p/'model/use-cases.yaml',{'elements':[{'id':'UC-000001','type':'UseCase','name':'Registrera order','abstraction_level':'conceptual','primary_actor':'ACT-000001','responsibility':'RSP-000001','outcome':'Order skapad','related_information':['INFO-000001'],'realized_by':['CMP-000001'],'origin':['declared']}], 'relationships':[]})
        write(p/'model/information.yaml',{'elements':[{'id':'INFO-000001','type':'InformationObject','name':'Order','description':'Kundens beställning.','abstraction_level':'conceptual','origin':['declared']}], 'relationships':[]})
        write(p/'model/structure.yaml',{'elements':[{'id':'CMP-000001','type':'Component','name':'Order Management','description':'Realiserar orderhantering.','abstraction_level':'logical','origin':['inferred']}], 'relationships':[{'id':'REL-000001','type':'realized_by','source':'RSP-000001','target':'CMP-000001','origin':['inferred']}]})
        write(p/'model/integrations.yaml',{'elements':[{'id':'API-000001','type':'API','name':'Order API','abstraction_level':'logical','provider':'CMP-000001','consumers':['EXT-000001'],'api_style':'REST','protocol':'HTTPS','exchanged_information':['INFO-000001'],'origin':['observed']}], 'relationships':[]})
        write(p/'model/data-stores.yaml',{'elements':[{'id':'DS-000001','type':'DataStore','name':'Order DB','abstraction_level':'logical','store_kind':'relational_database','origin':['observed']}], 'relationships':[]})
        write(p/'model/deployment.yaml',{'elements':[{'id':'ENV-000001','type':'Environment','name':'Production','abstraction_level':'runtime','environment_kind':'production','origin':['declared']},{'id':'NODE-000001','type':'DeploymentNode','name':'OpenShift','abstraction_level':'runtime','node_kind':'container_platform','origin':['declared']},{'id':'RUN-000001','type':'RuntimeUnit','name':'Order runtime','abstraction_level':'runtime','runtime_kind':'application_service','origin':['observed']}], 'relationships':[{'id':'REL-000010','type':'realized_as','source':'CMP-000001','target':'RUN-000001'},{'id':'REL-000011','type':'deployed_on','source':'RUN-000001','target':'NODE-000001'},{'id':'REL-000012','type':'belongs_to','source':'NODE-000001','target':'ENV-000001'},{'id':'REL-000013','type':'connects_to','source':'RUN-000001','target':'DS-000001','protocol':'JDBC'}]})
        write(p/'model/decisions.yaml',{'elements':[{'id':'ADR-000001','type':'ArchitectureDecision','name':'Använd OpenShift','abstraction_level':'logical','status':'accepted','decision':'Kör applikationen på OpenShift.','rationale':'Gemensam plattform.','origin':['declared']},{'id':'CON-000001','type':'Constraint','name':'TLS externt','abstraction_level':'conceptual','statement':'Extern trafik ska använda TLS.','origin':['declared']}], 'relationships':[]})
        write(p/'interactions/order.yaml',{'elements':[{'id':'SCN-000001','type':'Scenario','name':'Orderflöde','abstraction_level':'conceptual','use_case':'UC-000001','outcome':'Order skapad'},{'id':'INT-000001','type':'Interaction','name':'Registrera order','abstraction_level':'logical','scenario':'SCN-000001','participants':[{'ref':'ACT-000001'},{'ref':'CMP-000001'},{'ref':'DS-000001'}],'messages':[{'id':'IM-000001','order':1,'sender':'ACT-000001','receiver':'CMP-000001','label':'Submit order','communication_mode':'synchronous','information':['INFO-000001']}]}], 'relationships':[]})
        r=subprocess.run(['python3',str(ROOT/'scripts/report.py'),str(p)],cwd=ROOT,text=True,capture_output=True)
        if r.returncode: return fail(r.stdout+r.stderr)
        text=r.stdout
        required=['# Arkitekturbeskrivning – Order System','## 1. Syfte och omfattning','## 12. Källor och evidens','Registrera order','Order Management','Order API','Orderflöde','OpenShift','Använd OpenShift','```mermaid','Kända osäkerheter']
        for x in required:
            if x not in text: return fail(f'report missing {x}')
        if 'CMP-000001' not in text or 'infererad' not in text: return fail('uncertainty listing missing inferred component')
        out=p/'exports/architecture-description.md'
        r=subprocess.run(['python3',str(ROOT/'scripts/report.py'),str(p),'--output',str(out),'--no-diagrams'],cwd=ROOT,text=True,capture_output=True)
        if r.returncode or not out.is_file(): return fail('file output failed')
        if '```mermaid' in out.read_text(): return fail('--no-diagrams ignored')
    docs=(ROOT/'docs/architecture-description.md').read_text(encoding='utf-8')
    for phrase in ('Syfte och omfattning','Runtime och deployment','Kända osäkerheter','A29'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    v=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',v) or int(v.rsplit('.',1)[1])<28: return fail('version not A28 or later')
    print('A28 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
