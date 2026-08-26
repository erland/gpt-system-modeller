#!/usr/bin/env python3
from pathlib import Path
import json, re, yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
FILES=[ROOT/'schemas/common.schema.json',ROOT/'schemas/context.schema.json',ROOT/'schemas/functions.schema.json',ROOT/'schemas/use-cases.schema.json',ROOT/'schemas/information.schema.json']
def fail(m): print('FAIL:',m); return 1
def main():
    for p in FILES+[ROOT/'metamodel/information.yaml',ROOT/'docs/information-model.md',ROOT/'examples/a08-information-model.yaml']:
        if not p.is_file(): return fail(f'missing A8 artifact: {p.relative_to(ROOT)}')
    schemas=[json.loads(p.read_text()) for p in FILES]
    for s in schemas: Draft202012Validator.check_schema(s)
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    v=Draft202012Validator(schemas[-1],registry=reg)
    ex=yaml.safe_load((ROOT/'examples/a08-information-model.yaml').read_text())
    errs=list(v.iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    bad={'elements':[{'id':'SYS-000001','type':'System','name':'S','abstraction_level':'conceptual'},{'id':'INFO-000001','type':'InformationObject','name':'I','abstraction_level':'implementation'}],'relationships':[]}
    if v.is_valid(bad): return fail('InformationObject accepted implementation abstraction level')
    meta=yaml.safe_load((ROOT/'metamodel/information.yaml').read_text())
    io=meta['element_types'].get('InformationObject',{})
    if io.get('id_prefix')!='INFO' or io.get('abstraction_level')!='conceptual': return fail('InformationObject contract incorrect')
    for rel in ('contains_information','references_information','relates_to_information','derived_from_information'):
        if ['InformationObject','InformationObject'] not in meta['relationship_types'].get(rel,{}).get('allowed_pairs',[]): return fail(f'missing relationship {rel}')
    doc=(ROOT/'docs/information-model.md').read_text()
    for phrase in ('Table = InformationObject','vilken information systemet hanterar','Informationsrelationer'):
        if phrase not in doc: return fail(f'documentation missing {phrase}')
    prefix=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['registry']['reserved']
    if prefix.get('INFO')!='InformationObject': return fail('INFO prefix incorrect')
    uc=json.loads((ROOT/'schemas/use-cases.schema.json').read_text())
    ri=uc['$defs']['useCase']['allOf'][1]['properties']['related_information']['items']
    if ri.get('pattern')!='^INFO-[0-9]{6}$': return fail('UseCase.related_information not narrowed to INFO')
    version=(ROOT/'VERSION').read_text().strip()
    m=re.fullmatch(r'0\.1\.0-dev\.(\d+)',version)
    if not m or int(m.group(1))<8: return fail(f'expected version >= dev.8, got {version}')
    st=(ROOT/'STATUS.md').read_text()
    sm=re.search(r'Completed: A1[–-]A(\d+) / A30',st)
    if not sm or int(sm.group(1))<8: return fail('STATUS not advanced')
    print('A8 information model tests OK'); return 0
if __name__=='__main__': raise SystemExit(main())
