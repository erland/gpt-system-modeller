#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1

def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json','runtime.schema.json','deployment.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a19-deployment-relations.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/deployment.yaml').read_text())
    rels=meta.get('relationship_types',{})
    for r in ('deployed_on','belongs_to','connects_to'):
        if r not in rels: return fail(f'missing relationship {r}')
    if rels['deployed_on']['allowed_pairs'] != [['RuntimeUnit','DeploymentNode']]: return fail('deployed_on pair invalid')
    if rels['belongs_to']['allowed_pairs'] != [['DeploymentNode','Environment']]: return fail('belongs_to pair invalid')
    expected=[['RuntimeUnit','RuntimeUnit'],['RuntimeUnit','DataStore'],['RuntimeUnit','ExternalSystem']]
    if rels['connects_to']['allowed_pairs'] != expected: return fail('connects_to pairs invalid')
    if set(rels['connects_to'].get('direction_values',[])) != {'source_to_target','bidirectional'}: return fail('direction values invalid')
    relation_types={r['type'] for r in ex['relationships']}
    if not {'deployed_on','belongs_to','connects_to'} <= relation_types: return fail('example missing A19 relationships')
    connect=[r for r in ex['relationships'] if r['type']=='connects_to']
    if len(connect)<3: return fail('communication examples incomplete')
    if not any(r.get('target','').startswith('DS-') for r in connect): return fail('DataStore connection missing')
    if not any(r.get('target','').startswith('EXT-') for r in connect): return fail('ExternalSystem connection missing')
    if not all(r.get('direction') in {'source_to_target','bidirectional'} for r in connect): return fail('direction missing')
    if not any(r.get('exchanged_information') for r in connect): return fail('information exchange missing')
    doc=(ROOT/'docs/deployment-relations.md').read_text()
    for phrase in ('deployed_on','belongs_to','connects_to','protocol','direction','encryption','exchanged_information','Deployment-vyn i MVP'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<19: return fail('version not A19 or later')
    print('A19 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
