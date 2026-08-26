#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a15-interactions.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/interactions.yaml').read_text())
    inter=meta['element_types'].get('Interaction')
    if not inter or inter.get('id_prefix')!='INT' or inter.get('abstraction_level')!='logical': return fail('Interaction invalid')
    part=meta.get('embedded_types',{}).get('Participant')
    allowed={'Actor','System','ExternalSystem','Component','Service','DataStore'}
    if not part or set(part.get('allowed_element_types',[]))!=allowed: return fail('Participant allowed types invalid')
    for rel in ('realizes_scenario','has_participant'):
        if rel not in meta['relationship_types']: return fail(f'missing {rel}')
    i=next(e for e in ex['elements'] if e['type']=='Interaction')
    if i.get('scenario')!='SCN-000001' or len(i.get('participants',[]))<2: return fail('Interaction refs invalid')
    refs=[p['ref'] for p in i['participants']]
    if 'ACT-000001' not in refs or 'CMP-000001' not in refs or 'DS-000001' not in refs: return fail('expected participants missing')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('Interaction')!='INT': return fail('Interaction prefix missing')
    doc=(ROOT/'docs/interactions.md').read_text()
    for phrase in ('Interaction','Participant','Scenario','logical','InteractionMessage','DataStore'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<15: return fail('version not A15 or later')
    print('A15 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
