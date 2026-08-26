#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    files=['common.schema.json','context.schema.json','functions.schema.json','use-cases.schema.json','information.schema.json','logical-structure.schema.json','data-stores.schema.json','scenarios.schema.json','interactions.schema.json']
    schemas=[json.loads((ROOT/'schemas'/x).read_text()) for x in files]
    reg=Registry()
    for s in schemas[:-1]: reg=reg.with_resource(s['$id'],Resource.from_contents(s))
    ex=yaml.safe_load((ROOT/'examples/a16-interaction-messages.yaml').read_text())
    errs=list(Draft202012Validator(schemas[-1],registry=reg).iter_errors(ex))
    if errs:
        for e in errs: print('FAIL:',list(e.path),e.message)
        return 1
    meta=yaml.safe_load((ROOT/'metamodel/interactions.yaml').read_text())
    im=meta.get('embedded_types',{}).get('InteractionMessage')
    if not im or im.get('id_prefix')!='IM': return fail('InteractionMessage invalid')
    if set(im.get('communication_modes',[]))!={'synchronous','asynchronous'}: return fail('communication modes invalid')
    inter=next(e for e in ex['elements'] if e['type']=='Interaction')
    msgs=inter.get('messages',[])
    if len(msgs)<4: return fail('expected interaction messages missing')
    orders=[m['order'] for m in msgs]
    if len(orders)!=len(set(orders)) or orders!=sorted(orders): return fail('orders not unique/sorted in example')
    participant_refs={p['ref'] for p in inter['participants']}
    for m in msgs:
        if m['sender'] not in participant_refs or m['receiver'] not in participant_refs:
            return fail('sender/receiver must be participants')
        for info in m.get('information',[]):
            if not re.fullmatch(r'INFO-[0-9]{6}',info): return fail('invalid information ref')
    if not any(m['communication_mode']=='asynchronous' for m in msgs): return fail('async example missing')
    prefixes=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())
    if prefixes['registry']['reserved'].get('IM')!='InteractionMessage': return fail('reserved IM prefix missing')
    prefixes.setdefault('prefixes',{})['InteractionMessage']='IM'
    # The actual registry should activate IM at A16, not only reserve it.
    actual=yaml.safe_load((ROOT/'metamodel/id-prefixes.yaml').read_text())['prefixes']
    if actual.get('InteractionMessage')!='IM': return fail('InteractionMessage active prefix missing')
    doc=(ROOT/'docs/interactions.md').read_text()
    for phrase in ('InteractionMessage','sender','receiver','order','synchronous','asynchronous','message_ref','InformationObject'):
        if phrase not in doc: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<16: return fail('version not A16 or later')
    print('A16 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
