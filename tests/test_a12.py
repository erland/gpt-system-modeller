#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','interfaces.schema.json','messaging.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    v=Draft202012Validator(schemas[-1],registry=reg)
    ex=yaml.safe_load((ROOT/'examples/a12-messages-events.yaml').read_text())
    errs=list(v.iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/messaging.yaml').read_text())
    for typ,prefix in [('Message','MSG'),('Event','EVT')]:
        spec=meta['element_types'].get(typ)
        if not spec or spec.get('id_prefix')!=prefix or spec.get('abstraction_level')!='logical': return fail(f'{typ} invalid')
    for rel in ('sends','receives','publishes','subscribes'):
        if rel not in meta['relationship_types']: return fail(f'missing {rel}')
    msg=next(e for e in ex['elements'] if e['type']=='Message')
    evt=next(e for e in ex['elements'] if e['type']=='Event')
    if msg['communication_mode']!='synchronous' or msg['producer']!='CMP-000001': return fail('message semantics invalid')
    if evt.get('communication_mode')!='asynchronous' or evt.get('topic')!='order-events': return fail('event semantics invalid')
    if 'INFO-000001' not in evt.get('exchanged_information',[]): return fail('event information missing')
    doc=(ROOT/'docs/messages-and-events.md').read_text()
    for phrase in ('Message','Event','producer','consumers','asynchronous','InformationObject','channel','topic'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if prefixes.get('Message')!='MSG' or prefixes.get('Event')!='EVT': return fail('prefix registry not updated')
    version=(ROOT/'VERSION').read_text().strip(); m=re.fullmatch(r'0\.1\.0-dev\.(\d+)',version)
    if not m or int(m.group(1))<12: return fail(f'expected >= dev.12 got {version}')
    st=(ROOT/'STATUS.md').read_text(); sm=re.search(r'Completed: A1[–-]A(\d+) / A30',st)
    if not sm or int(sm.group(1))<12: return fail('STATUS not advanced')
    print('A12 messaging tests OK'); return 0
if __name__=='__main__': raise SystemExit(main())
