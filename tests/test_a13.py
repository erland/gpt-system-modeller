#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json','data-stores.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    v=Draft202012Validator(schemas[-1],registry=reg)
    ex=yaml.safe_load((ROOT/'examples/a13-data-stores.yaml').read_text())
    errs=list(v.iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/data-stores.yaml').read_text())
    ds=meta['element_types'].get('DataStore')
    if not ds or ds.get('id_prefix')!='DS' or ds.get('abstraction_level')!='logical': return fail('DataStore invalid')
    for rel in ('stores_information','accesses','owns_data_store'):
        if rel not in meta['relationship_types']: return fail(f'missing {rel}')
    store=next(e for e in ex['elements'] if e['type']=='DataStore')
    if store['store_kind']!='relational_database' or store.get('technology')!='PostgreSQL': return fail('store fields invalid')
    if store.get('authoritative_for')!=['INFO-000001']: return fail('authoritative_for invalid')
    rels={(r['type'],r['source'],r['target']) for r in ex['relationships']}
    if ('stores_information','DS-000001','INFO-000001') not in rels: return fail('stores_information missing')
    if ('accesses','CMP-000001','DS-000001') not in rels: return fail('accesses missing')
    if ('owns_data_store','CMP-000001','DS-000001') not in rels: return fail('owns_data_store missing')
    info=yaml.safe_load((ROOT/'metamodel/information-usage.yaml').read_text())
    for rn in ('creates_information','reads_information','updates_information','deletes_information','owns_information','masters_information','stores_information','exchanges_information'):
        spec=info['relationship_types'][rn]
        if ['DataStore','InformationObject'] not in spec.get('allowed_pairs',[]): return fail(f'DataStore pair not active for {rn}')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('DataStore')!='DS': return fail('DataStore prefix missing')
    doc=(ROOT/'docs/data-stores.md').read_text()
    for phrase in ('DataStore','InformationObject','stores_information','accesses','owns_data_store','DatabaseTable','runtime'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<13: return fail('version not A13 or later')
    print('A13 tests passed')
    return 0
if __name__=='__main__': raise SystemExit(main())
