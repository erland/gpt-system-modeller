#!/usr/bin/env python3
"""Materialize and render System Modeller A26/A27 views from a system project."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
VIEW_SCHEMA=json.loads((ROOT/'schemas/views.schema.json').read_text(encoding='utf-8'))
META=yaml.safe_load((ROOT/'metamodel/views.yaml').read_text(encoding='utf-8'))
CORE=META['core_views']

NAMES={
    'system_context':'System Context','functional_overview':'Functional Overview',
    'use_case_overview':'Use Case Overview','information_overview':'Information Overview',
    'functional_information':'Functional–Information View','logical_component':'Logical Component View',
    'use_case_realization':'Use Case Realization View','integration':'Integration View',
    'sequence':'Sequence View','deployment':'Deployment View'}

def load_project(project:Path):
    elements={}; rels=[]
    for folder in ('model','interactions','implementation','sources'):
        base=project/folder
        if not base.is_dir(): continue
        for path in sorted(list(base.rglob('*.yaml'))+list(base.rglob('*.yml'))):
            data=yaml.safe_load(path.read_text(encoding='utf-8')) or {}
            if not isinstance(data,dict): continue
            for e in data.get('elements') or []:
                if isinstance(e,dict) and e.get('id'): elements[e['id']]=e
            for r in data.get('relationships') or []:
                if isinstance(r,dict): rels.append(r)
    return elements,rels

def default_definition(view_type:str)->dict[str,Any]:
    if view_type not in CORE: raise ValueError(f'unsupported view type: {view_type}')
    spec=CORE[view_type]
    return {'id':'VIEW-000001','name':NAMES[view_type],'type':view_type,'purpose':spec['purpose'],
            'detail_level':spec['default_detail_level'],'notation':'neutral'}

def validate_definition(d):
    errs=sorted(Draft202012Validator(VIEW_SCHEMA).iter_errors(d),key=lambda e:list(e.path))
    if errs: raise ValueError('; '.join(f"{'.'.join(map(str,e.path))}: {e.message}" for e in errs))

def load_definition(path:Path)->dict:
    d=yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(d,dict): raise ValueError('view definition must be a mapping')
    validate_definition(d); return d

def derived_links(view_type, selected, elements, explicit_keys):
    links=[]; n=1
    def add(source,target,typ,extra=None):
        nonlocal n
        if source not in selected or target not in selected: return
        key=(typ,source,target)
        if key in explicit_keys: return
        x={'id':f'DERIVED-{n:06d}','type':typ,'source':source,'target':target,'derived':True}
        if extra: x.update(extra)
        links.append(x); n+=1
    if view_type in {'use_case_overview','functional_information','use_case_realization'}:
        for e in elements.values():
            if e.get('type')!='UseCase' or e.get('id') not in selected: continue
            uc=e['id']
            a=e.get('primary_actor')
            if a: add(a,uc,'performs')
            for a in e.get('supporting_actors') or []: add(a,uc,'supports_use_case')
            rsp=e.get('responsibility')
            if rsp: add(rsp,uc,'groups_use_case')
            if view_type in {'functional_information','use_case_realization'}:
                for info in e.get('related_information') or []: add(uc,info,'related_information')
            if view_type=='use_case_realization':
                for target in e.get('realized_by') or []: add(uc,target,'realized_by')
    if view_type=='integration':
        for e in elements.values():
            if e.get('id') not in selected or e.get('type') not in {'Interface','API','Message','Event'}: continue
            eid=e['id']; typ=e.get('type')
            provider=e.get('provider') or e.get('producer')
            if provider:
                add(provider,eid,'provides_interface' if typ in {'Interface','API'} else ('publishes' if typ=='Event' else 'sends'))
            for c in e.get('consumers') or []:
                add(c,eid,'consumes_interface' if typ in {'Interface','API'} else ('subscribes' if typ=='Event' else 'receives'))
            for info in e.get('exchanged_information') or []:
                add(eid,info,'exchanges_information')
    return links

def sequence_payload(d,elements):
    interaction_id=(d.get('filters') or {}).get('interaction_id')
    scenario_id=(d.get('filters') or {}).get('scenario_id')
    interactions=[]
    for e in elements.values():
        if e.get('type')!='Interaction': continue
        if interaction_id and e.get('id')!=interaction_id: continue
        if scenario_id and e.get('scenario')!=scenario_id: continue
        parts=[]
        for p in e.get('participants') or []:
            ref=p.get('ref') if isinstance(p,dict) else p
            if ref and ref in elements:
                parts.append({'ref':ref,'role':p.get('role') if isinstance(p,dict) else None,'element':elements[ref]})
        msgs=sorted([dict(m) for m in e.get('messages') or []],key=lambda x:(x.get('order',10**9),x.get('id','')))
        interactions.append({'interaction':e,'participants':parts,'messages':msgs})
    return interactions

def materialize(project:Path,d:dict)->dict:
    elements,rels=load_project(project)
    spec=CORE[d['type']]
    etypes=set(d.get('include_element_types') or spec['default_element_types'])
    rtypes=set(d.get('include_relation_types') or spec['default_relation_types'])
    selected={i:e for i,e in elements.items() if e.get('type') in etypes}
    # Sequence view narrows participants to selected interactions when filters are used.
    sequences=sequence_payload(d,elements) if d['type']=='sequence' else []
    if d['type']=='sequence' and sequences:
        keep=set()
        for seq in sequences:
            keep.add(seq['interaction']['id'])
            if seq['interaction'].get('scenario'): keep.add(seq['interaction']['scenario'])
            keep.update(p['ref'] for p in seq['participants'])
        selected={i:e for i,e in selected.items() if i in keep}
    links=[]; explicit=set()
    for r in rels:
        if r.get('type') in rtypes and r.get('source') in selected and r.get('target') in selected:
            x=dict(r); x['derived']=False; links.append(x)
            explicit.add((r.get('type'),r.get('source'),r.get('target')))
    links.extend(derived_links(d['type'],selected,elements,explicit))
    out_e=[selected[k] for k in sorted(selected)]
    links.sort(key=lambda r:(r.get('type',''),r.get('source',''),r.get('target',''),r.get('id','')))
    result={'view':d,'elements':out_e,'links':links,
            'summary':{'element_count':len(out_e),'link_count':len(links),'derived_link_count':sum(bool(x.get('derived')) for x in links)}}
    if d['type']=='sequence':
        result['sequences']=sequences
        result['summary']['interaction_count']=len(sequences)
        result['summary']['message_count']=sum(len(x['messages']) for x in sequences)
    return result

def safe_id(v): return re.sub(r'[^A-Za-z0-9_]', '_', v)
def q(s): return str(s or '').replace('"', "'").replace('\n',' ')

def mermaid(result):
    vt=result['view']['type']
    if vt=='sequence':
        lines=['sequenceDiagram']
        aliases={}
        for seq in result.get('sequences') or []:
            for p in seq['participants']:
                ref=p['ref']; alias=safe_id(ref); aliases[ref]=alias
                lines.append(f'    participant {alias} as {q(p["element"].get("name",ref))}')
            for m in seq['messages']:
                s=aliases.get(m.get('sender'),safe_id(m.get('sender','unknown'))); r=aliases.get(m.get('receiver'),safe_id(m.get('receiver','unknown')))
                arrow='-->>' if m.get('communication_mode')=='asynchronous' else '->>'
                label=q(m.get('label') or m.get('operation') or m.get('id'))
                if m.get('condition'): label=f'[{q(m["condition"])}] {label}'
                lines.append(f'    {s}{arrow}{r}: {label}')
        return '\n'.join(lines)+'\n'
    lines=['flowchart LR']
    byid={e['id']:e for e in result['elements']}
    for e in result['elements']:
        lines.append(f'    {safe_id(e["id"])}["{q(e.get("name",e["id"]))}<br/><small>{e.get("type","")}</small>"]')
    for r in result['links']:
        label=q(r.get('type',''))
        if r.get('protocol'): label += f' / {q(r["protocol"])}'
        lines.append(f'    {safe_id(r["source"])} -->|{label}| {safe_id(r["target"])}')
    return '\n'.join(lines)+'\n'

def plantuml(result):
    vt=result['view']['type']
    if vt=='sequence':
        lines=['@startuml']
        aliases={}
        for seq in result.get('sequences') or []:
            for p in seq['participants']:
                ref=p['ref']; alias=safe_id(ref); aliases[ref]=alias
                lines.append(f'participant "{q(p["element"].get("name",ref))}" as {alias}')
            for m in seq['messages']:
                s=aliases.get(m.get('sender'),safe_id(m.get('sender','unknown'))); r=aliases.get(m.get('receiver'),safe_id(m.get('receiver','unknown')))
                arrow='->>' if m.get('communication_mode')=='asynchronous' else '->'
                label=q(m.get('label') or m.get('operation') or m.get('id'))
                if m.get('condition'): label=f'[{q(m["condition"])}] {label}'
                lines.append(f'{s} {arrow} {r} : {label}')
        lines.append('@enduml'); return '\n'.join(lines)+'\n'
    lines=['@startuml','left to right direction']
    for e in result['elements']:
        kind=e.get('type')
        keyword='component'
        if kind=='Actor': keyword='actor'
        elif kind in {'System','ExternalSystem','Subsystem','DeploymentNode','Environment'}: keyword='rectangle'
        elif kind=='DataStore': keyword='database'
        elif kind in {'Interface','API'}: keyword='interface'
        elif kind=='UseCase': keyword='usecase'
        alias=safe_id(e['id'])
        lines.append(f'{keyword} "{q(e.get("name",e["id"]))}" as {alias}')
    for r in result['links']:
        label=q(r.get('type',''))
        if r.get('protocol'): label += f' / {q(r["protocol"])}'
        lines.append(f'{safe_id(r["source"])} --> {safe_id(r["target"])} : {label}')
    lines.append('@enduml'); return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('project',type=Path)
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--type',choices=sorted(CORE))
    g.add_argument('--definition',type=Path)
    ap.add_argument('--format',choices=['yaml','json','mermaid','plantuml'],default='yaml')
    ap.add_argument('--output',type=Path)
    ns=ap.parse_args()
    try:
        d=default_definition(ns.type) if ns.type else load_definition(ns.definition)
        validate_definition(d)
        result=materialize(ns.project,d)
    except Exception as e:
        print(f'ERROR: {e}'); return 2
    if ns.format=='json': text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    elif ns.format=='yaml': text=yaml.safe_dump(result,allow_unicode=True,sort_keys=False)
    elif ns.format=='mermaid': text=mermaid(result)
    else: text=plantuml(result)
    if ns.output:
        ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(text,encoding='utf-8')
    else: print(text,end='')
    return 0
if __name__=='__main__': raise SystemExit(main())
