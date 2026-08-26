#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry,Resource
ROOT=Path(__file__).resolve().parents[1]
SCHEMA_NAMES=['common','context','functions','use-cases','information','information-usage']
def fail(m): print('FAIL:',m); return 1
def main():
    artifacts=[ROOT/'metamodel/information-usage.yaml',ROOT/'schemas/information-usage.schema.json',ROOT/'docs/information-usage.md',ROOT/'examples/a09-information-usage.yaml']
    for p in artifacts:
        if not p.is_file(): return fail(f'missing A9 artifact: {p.relative_to(ROOT)}')
    schemas=[]
    for n in SCHEMA_NAMES:
        p=ROOT/'schemas'/f'{n}.schema.json'; s=json.loads(p.read_text()); Draft202012Validator.check_schema(s); schemas.append(s)
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    v=Draft202012Validator(schemas[-1],registry=reg)
    ex=yaml.safe_load((ROOT/'examples/a09-information-usage.yaml').read_text())
    errs=list(v.iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/information-usage.yaml').read_text())
    expected=('creates_information','reads_information','updates_information','deletes_information','owns_information','masters_information','stores_information','exchanges_information')
    for rel in expected:
        spec=meta['relationship_types'].get(rel)
        if not spec: return fail(f'missing {rel}')
        if rel!='stores_information' and ['UseCase','InformationObject'] not in spec.get('allowed_pairs',[]): return fail(f'{rel} missing active UseCase pair')
    readspec=meta['relationship_types']['reads_information']
    active={tuple(x) for x in readspec.get('allowed_pairs',[])}
    planned={tuple(x['pair']):x['activate_in'] for x in readspec.get('planned_pairs',[])}
    if ('Component','InformationObject') not in active: return fail('Component pair should be active from A10')
    if ('API','InformationObject') not in active and planned.get(('API','InformationObject'))!='A11': return fail('API pair neither active nor planned')
    storespec=meta['relationship_types']['stores_information']
    storeactive={tuple(x) for x in storespec.get('allowed_pairs',[])}
    storeplanned={tuple(x['pair']):x['activate_in'] for x in storespec.get('planned_pairs',[])}
    if ('DataStore','InformationObject') not in storeactive and storeplanned.get(('DataStore','InformationObject'))!='A13': return fail('DataStore storage pair neither active nor planned')
    doc=(ROOT/'docs/information-usage.md').read_text()
    for phrase in ('Kanonisk riktning','creates_information','UseCase.related_information','verksamhetsmässig informationsanvändning'):
        if phrase not in doc: return fail(f'documentation missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip(); m=re.fullmatch(r'0\.1\.0-dev\.(\d+)',version)
    if not m or int(m.group(1))<9: return fail(f'expected version >= dev.9, got {version}')
    st=(ROOT/'STATUS.md').read_text()
    sm=re.search(r'Completed: A1[–-]A(\d+) / A30',st)
    if not sm or int(sm.group(1))<9: return fail('STATUS not advanced')
    print('A9 information usage tests OK'); return 0
if __name__=='__main__': raise SystemExit(main())
