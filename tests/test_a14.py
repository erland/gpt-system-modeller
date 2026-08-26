#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','scenarios.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(yaml.safe_load((ROOT/'examples/a14-scenarios.yaml').read_text())))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/scenarios.yaml').read_text())
    sc=meta['element_types'].get('Scenario')
    if not sc or sc.get('id_prefix')!='SCN' or sc.get('abstraction_level')!='conceptual': return fail('Scenario invalid')
    for rel in ('scenario_for','involves','involves_information'):
        if rel not in meta['relationship_types']: return fail(f'missing {rel}')
    ex=yaml.safe_load((ROOT/'examples/a14-scenarios.yaml').read_text())
    s=next(e for e in ex['elements'] if e['type']=='Scenario')
    if s.get('use_case')!='UC-000001' or 'CMP-000001' not in s.get('components',[]): return fail('scenario refs invalid')
    if not s.get('outcome'): return fail('outcome missing')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('Scenario')!='SCN': return fail('Scenario prefix missing')
    doc=(ROOT/'docs/scenarios.md').read_text()
    for phrase in ('Scenario','end-to-end','UseCase','InformationObject','Component','ExternalSystem','Interaction'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<14: return fail('version not A14 or later')
    print('A14 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
