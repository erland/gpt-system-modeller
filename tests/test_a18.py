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
    ex=yaml.safe_load((ROOT/'examples/a18-deployment-context.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/deployment.yaml').read_text())
    env=meta['element_types'].get('Environment'); node=meta['element_types'].get('DeploymentNode')
    if not env or env.get('id_prefix')!='ENV' or env.get('abstraction_level')!='runtime': return fail('Environment invalid')
    if not node or node.get('id_prefix')!='NODE' or node.get('abstraction_level')!='runtime': return fail('DeploymentNode invalid')
    if set(env.get('environment_kinds',[])) != {'development','test','staging','production','other'}: return fail('environment kinds invalid')
    expected={'client_device','server','virtual_machine','container_platform','cloud_service','database_platform','external_platform'}
    if set(node.get('node_kinds',[])) != expected: return fail('node kinds invalid')
    planned=meta.get('planned_relationship_types',{})
    active=meta.get('relationship_types',{})
    for rel in ('deployed_on','belongs_to'):
        if rel not in planned and rel not in active: return fail(f'{rel} neither reserved nor active')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('Environment')!='ENV' or prefixes.get('DeploymentNode')!='NODE': return fail('deployment prefixes missing')
    elems=ex['elements']
    if len([e for e in elems if e['type']=='Environment'])!=1: return fail('environment example invalid')
    if len([e for e in elems if e['type']=='DeploymentNode'])<3: return fail('deployment node examples missing')
    doc=(ROOT/'docs/deployment-context.md').read_text()
    for phrase in ('Environment','DeploymentNode','RuntimeUnit','deployed_on','belongs_to','övergripande deploymentvy'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<18: return fail('version not A18 or later')
    print('A18 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
