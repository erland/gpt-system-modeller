#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1

def main():
    required=[ROOT/'metamodel/origin.yaml',ROOT/'schemas/origin.schema.json',ROOT/'docs/origin-declared-observed-inferred.md',ROOT/'examples/a22-origin.yaml']
    for p in required:
        if not p.is_file(): return fail(f'missing A22 artifact: {p.relative_to(ROOT)}')
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json','runtime.schema.json','deployment.schema.json','decisions.schema.json','provenance.schema.json','origin.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a22-origin.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    common=schemas[0]
    kinds=common['$defs']['originKind']['enum']
    expected=['declared','observed','inferred','user_confirmed','unresolved']
    if kinds!=expected: return fail(f'origin kinds differ: {kinds}')
    elem_validator=Draft202012Validator({'$schema':common['$schema'],'$defs':common['$defs'],'$ref':'#/$defs/modelElement'})
    good={'id':'CMP-000001','type':'Component','name':'Order','abstraction_level':'logical','origin':['declared','observed']}
    if not elem_validator.is_valid(good): return fail('declared+observed should be valid')
    bad=dict(good); bad['origin']=['guessed']
    if elem_validator.is_valid(bad): return fail('unknown origin accepted')
    bad2=dict(good); bad2['origin']=['declared','declared']
    if elem_validator.is_valid(bad2): return fail('duplicate origin accepted')
    all_origins=[o for e in ex.get('elements',[]) for o in e.get('origin',[])]+[o for r in ex.get('relationships',[]) for o in r.get('origin',[])]
    for k in ('declared','observed','inferred'):
        if k not in all_origins: return fail(f'example lacks {k}')
    if not any(set(e.get('origin',[]))=={'declared','observed'} for e in ex.get('elements',[])+ex.get('relationships',[])):
        return fail('example lacks declared+observed')
    meta=yaml.safe_load((ROOT/'metamodel/origin.yaml').read_text())
    if set(meta.get('origin_values',{}))!=set(expected): return fail('origin metamodel missing values')
    docs=(ROOT/'docs/origin-declared-observed-inferred.md').read_text()
    for phrase in ('Origin är inte Evidence.status','declared','observed','inferred','user_confirmed','unresolved'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<22: return fail('version not A22 or later')
    print('A22 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
