#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json','runtime.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a17-runtime-units.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/runtime.yaml').read_text())
    ru=meta['element_types'].get('RuntimeUnit')
    if not ru or ru.get('id_prefix')!='RUN' or ru.get('abstraction_level')!='runtime': return fail('RuntimeUnit invalid')
    expected={'web_application','application_service','background_service','batch_job','database','message_broker','function'}
    if set(ru.get('runtime_kinds',[]))!=expected: return fail('runtime kinds invalid')
    rel=meta['relationship_types'].get('realized_as')
    pairs={tuple(p) for p in rel.get('allowed_pairs',[])} if rel else set()
    for pair in [('Component','RuntimeUnit'),('Service','RuntimeUnit'),('DataStore','RuntimeUnit')]:
        if pair not in pairs: return fail(f'missing realized_as pair {pair}')
    run=[e for e in ex['elements'] if e['type']=='RuntimeUnit']
    if len(run)!=2 or not all(e['abstraction_level']=='runtime' for e in run): return fail('runtime example invalid')
    if not any(e['runtime_kind']=='application_service' for e in run): return fail('application service example missing')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('RuntimeUnit')!='RUN': return fail('RuntimeUnit prefix missing')
    doc=(ROOT/'docs/runtime-units.md').read_text()
    for phrase in ('RuntimeUnit','runtime','realized_as','Component','DeploymentNode','vad som faktiskt körs'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<17: return fail('version not A17 or later')
    print('A17 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
