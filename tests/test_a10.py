#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    v=Draft202012Validator(schemas[-1],registry=reg)
    ex=yaml.safe_load((ROOT/'examples/a10-logical-architecture.yaml').read_text())
    errs=list(v.iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/logical-structure.yaml').read_text())
    for typ,prefix in [('Subsystem','SUB'),('Component','CMP'),('Service','SVC')]:
        spec=meta['element_types'].get(typ)
        if not spec or spec.get('id_prefix')!=prefix or spec.get('abstraction_level')!='logical': return fail(f'{typ} definition invalid')
    rels=meta['relationship_types']
    expected=('contains','part_of','depends_on','uses','provides','realized_by','realizes')
    for rel in expected:
        if rel not in rels: return fail(f'missing {rel}')
    if ['Responsibility','Component'] not in rels['realized_by']['allowed_pairs']: return fail('realized_by pair missing')
    if ['Component','Service'] not in rels['provides']['allowed_pairs']: return fail('provides pair missing')
    info=yaml.safe_load((ROOT/'metamodel/information-usage.yaml').read_text())
    for rel in ('creates_information','reads_information','updates_information','deletes_information','owns_information','masters_information','stores_information','exchanges_information'):
        pairs=info['relationship_types'][rel].get('allowed_pairs',[])
        if ['Component','InformationObject'] not in pairs: return fail(f'{rel} missing Component pair')
        if ['Service','InformationObject'] not in pairs: return fail(f'{rel} missing Service pair')
    doc=(ROOT/'docs/logical-architecture.md').read_text()
    for phrase in ('Subsystem','Component','Service','Responsibility (conceptual)','Class = Component','RuntimeUnit'):
        if phrase not in doc: return fail(f'documentation missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip(); m=re.fullmatch(r'0\.1\.0-dev\.(\d+)',version)
    if not m or int(m.group(1))<10: return fail(f'expected version >= dev.10, got {version}')
    st=(ROOT/'STATUS.md').read_text(); sm=re.search(r'Completed: A1[–-]A(\d+) / A30',st)
    if not sm or int(sm.group(1))<10: return fail('STATUS not advanced')
    print('A10 logical architecture tests OK'); return 0
if __name__=='__main__': raise SystemExit(main())
