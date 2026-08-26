#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1

def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json','runtime.schema.json','deployment.schema.json','decisions.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a20-decisions-constraints.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/decisions.yaml').read_text())
    ets=meta.get('element_types',{})
    for t in ('ArchitectureDecision','Constraint'):
        if t not in ets: return fail(f'missing {t}')
    if ets['ArchitectureDecision']['id_prefix']!='ADR': return fail('ADR prefix invalid')
    if ets['Constraint']['id_prefix']!='CON': return fail('CON prefix invalid')
    if 'affects' not in meta.get('relationship_types',{}): return fail('affects missing')
    adr=next(e for e in ex['elements'] if e['type']=='ArchitectureDecision')
    con=next(e for e in ex['elements'] if e['type']=='Constraint')
    for k in ('context','decision','rationale','decision_status'):
        if not adr.get(k): return fail(f'ADR missing {k}')
    if not con.get('statement'): return fail('Constraint statement missing')
    if not adr.get('affected_elements') or not con.get('affected_elements'): return fail('affected_elements missing')
    doc=(ROOT/'docs/architecture-decisions-and-constraints.md').read_text()
    for phrase in ('ArchitectureDecision','Constraint','affects','affected_elements','varför arkitekturen ser ut som den gör'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text()).get('prefixes',{})
    if prefixes.get('ArchitectureDecision')!='ADR' or prefixes.get('Constraint')!='CON': return fail('active prefixes missing')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<20: return fail('version not A20 or later')
    print('A20 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
