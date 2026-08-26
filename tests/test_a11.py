#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    v=Draft202012Validator(schemas[-1],registry=reg)
    ex=yaml.safe_load((ROOT/'examples/a11-interfaces-api.yaml').read_text())
    errs=list(v.iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/interfaces.yaml').read_text())
    for typ,prefix in [('Interface','IF'),('API','API')]:
        spec=meta['element_types'].get(typ)
        if not spec or spec.get('id_prefix')!=prefix or spec.get('abstraction_level')!='logical': return fail(f'{typ} invalid')
    for rel in ('exposes','consumes_interface','provides_interface'):
        if rel not in meta['relationship_types']: return fail(f'missing {rel}')
    api=next(e for e in ex['elements'] if e['type']=='API')
    if api['provider']!='CMP-000001' or api['consumers']!=['CMP-000002']: return fail('provider/consumer example invalid')
    if api['exchanged_information']!=['INFO-000001']: return fail('information exchange invalid')
    doc=(ROOT/'docs/interfaces-and-apis.md').read_text()
    for phrase in ('logical','provider','consumers','REST','GraphQL','endpoint','InformationObject'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('Interface')!='IF' or prefixes.get('API')!='API': return fail('prefix registry not updated')
    version=(ROOT/'VERSION').read_text().strip(); m=re.fullmatch(r'0\.1\.0-dev\.(\d+)',version)
    if not m or int(m.group(1))<11: return fail(f'expected >= dev.11 got {version}')
    st=(ROOT/'STATUS.md').read_text(); sm=re.search(r'Completed: A1[–-]A(\d+) / A30',st)
    if not sm or int(sm.group(1))<11: return fail('STATUS not advanced')
    print('A11 interface/API tests OK'); return 0
if __name__=='__main__': raise SystemExit(main())
