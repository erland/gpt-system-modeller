#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1

def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json','runtime.schema.json','deployment.schema.json','decisions.schema.json','provenance.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a21-provenance-evidence.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/provenance.yaml').read_text())
    for t in ('Source','SourceReference','Evidence'):
        if t not in meta.get('record_types',{}): return fail(f'missing {t}')
    ev=meta['record_types']['Evidence']
    for status in ('source_confirmed','user_confirmed','inferred','assumed','unresolved'):
        if status not in ev['status_values']: return fail(f'missing evidence status {status}')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text()).get('prefixes',{})
    if prefixes.get('Source')!='SRC' or prefixes.get('SourceReference')!='REF' or prefixes.get('Evidence')!='EVD': return fail('provenance prefixes not active')
    ids={e['id'] for e in ex['evidence']}
    if not any(set(x.get('evidence',[])) & ids for x in ex['elements']): return fail('no model element references evidence')
    if not any(set(x.get('evidence',[])) & ids for x in ex['relationships']): return fail('no relationship references evidence')
    src_ids={x['id'] for x in ex['sources']}; ref_ids={x['id'] for x in ex['source_references']}
    if not all(r['source'] in src_ids for r in ex['source_references']): return fail('broken source reference')
    if not all(all(r in ref_ids for r in e.get('source_refs',[])) for e in ex['evidence']): return fail('broken evidence source_refs')
    inferred=next(e for e in ex['evidence'] if e['status']=='inferred')
    if not inferred.get('reason'): return fail('inferred evidence lacks reason')
    doc=(ROOT/'docs/provenance-and-evidence.md').read_text()
    for phrase in ('SourceReference','source_confirmed','user_confirmed','inferred','assumed','unresolved','declared','observed'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<21: return fail('version not A21 or later')
    print('A21 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
