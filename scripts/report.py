#!/usr/bin/env python3
"""Generate the System Modeller A28 MVP architecture description in Markdown."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import yaml
import view as view_engine

SECTIONS = [
    'Syfte och omfattning','Systemets sammanhang','Funktionell översikt',
    'Aktörer och use cases','Informationsarkitektur','Logisk arkitektur',
    'Integrationsarkitektur','Viktiga scenarier','Runtime och deployment',
    'Arkitekturbeslut och constraints','Kända osäkerheter','Källor och evidens'
]
VIEW_BY_SECTION = {
    'Systemets sammanhang':'system_context',
    'Funktionell översikt':'functional_overview',
    'Aktörer och use cases':'use_case_overview',
    'Informationsarkitektur':'information_overview',
    'Logisk arkitektur':'logical_component',
    'Integrationsarkitektur':'integration',
    'Viktiga scenarier':'sequence',
    'Runtime och deployment':'deployment',
}

def esc(v: Any) -> str:
    return str(v if v is not None else '').replace('|','\\|').replace('\n',' ').strip()

def load_manifest(project: Path) -> dict:
    p=project/'project.yaml'
    return yaml.safe_load(p.read_text(encoding='utf-8')) or {} if p.is_file() else {}

def origins(e: dict) -> list[str]:
    o=e.get('origin') or []
    return [o] if isinstance(o,str) else list(o)

def evidence_refs(e: dict) -> list[str]:
    ev=e.get('evidence') or []
    return [ev] if isinstance(ev,str) else list(ev)

def by_type(elements):
    d=defaultdict(list)
    for e in elements.values(): d[e.get('type','Unknown')].append(e)
    for xs in d.values(): xs.sort(key=lambda x:(x.get('name',''),x.get('id','')))
    return d

def table(headers, rows):
    if not rows: return '_Ingen information modellerad._\n'
    out=['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']
    out += ['| '+' | '.join(esc(c) for c in row)+' |' for row in rows]
    return '\n'.join(out)+'\n'

def render_view(project, typ):
    try:
        result=view_engine.materialize(project, view_engine.default_definition(typ))
        if result['summary'].get('element_count',0)==0: return None
        return view_engine.mermaid(result).rstrip()
    except Exception:
        return None

def relation_index(rels):
    out=defaultdict(list); inc=defaultdict(list)
    for r in rels:
        out[r.get('source')].append(r); inc[r.get('target')].append(r)
    return out,inc

def architecture_description(project: Path, include_diagrams=True) -> str:
    manifest=load_manifest(project)
    elements, rels=view_engine.load_project(project)
    typed=by_type(elements); outgoing,incoming=relation_index(rels)
    proj=manifest.get('project') or manifest
    title=proj.get('name') or 'Systemarkitektur'
    description=proj.get('description') or ''
    lines=[f'# Arkitekturbeskrivning – {title}','',
           '> Genererad från System Modellers kanoniska YAML-modell. Diagram och sammanställningar är härledda vyer och utgör inte separat sanningskälla.','']
    lines += ['## 1. Syfte och omfattning','']
    systems=typed['System']
    purpose=(systems[0].get('description') if systems else '') or description
    lines.append(purpose or 'Syfte och omfattning är ännu inte beskrivet i modellen.')
    if systems:
        lines += ['',table(['System','Beskrivning'],[(e.get('name'),e.get('description','')) for e in systems]).rstrip()]

    # Context
    lines += ['','## 2. Systemets sammanhang','']
    actors=typed['Actor']; exts=typed['ExternalSystem']
    lines.append(f'Modellen innehåller **{len(actors)} aktör(er)** och **{len(exts)} externt system/systemtjänst(er)** i systemkontexten.')
    lines += ['',table(['Typ','Namn','Beskrivning'], [('Aktör',e.get('name'),e.get('description','')) for e in actors]+[('Externt system',e.get('name'),e.get('description','')) for e in exts]).rstrip()]
    if include_diagrams:
        d=render_view(project,'system_context')
        if d: lines += ['','```mermaid',d,'```']

    # Functional
    lines += ['','## 3. Funktionell översikt','']
    rs=typed['Responsibility']
    lines.append('Systemets modellerade funktionella ansvar sammanfattas nedan.')
    lines += ['',table(['Ansvar','Beskrivning'],[(e.get('name'),e.get('description','')) for e in rs]).rstrip()]
    if include_diagrams:
        d=render_view(project,'functional_overview')
        if d: lines += ['','```mermaid',d,'```']

    # Actors/use cases
    lines += ['','## 4. Aktörer och use cases','']
    ucs=typed['UseCase']
    rows=[]
    for u in ucs:
        a=elements.get(u.get('primary_actor'),{}).get('name',u.get('primary_actor',''))
        r=elements.get(u.get('responsibility'),{}).get('name',u.get('responsibility',''))
        rows.append((u.get('name'),a,r,u.get('outcome','')))
    lines += [table(['Use case','Primär aktör','Ansvar','Utfall'],rows).rstrip()]
    if include_diagrams:
        d=render_view(project,'use_case_overview')
        if d: lines += ['','```mermaid',d,'```']

    # Information
    lines += ['','## 5. Informationsarkitektur','']
    infos=typed['InformationObject']
    rows=[]
    for e in infos:
        owner=elements.get(e.get('owner'),{}).get('name',e.get('owner','')) if e.get('owner') else ''
        rows.append((e.get('name'),e.get('description',''),owner,e.get('classification','')))
    lines += [table(['Informationsobjekt','Beskrivning','Ägare','Klassificering'],rows).rstrip()]
    if include_diagrams:
        d=render_view(project,'information_overview')
        if d: lines += ['','```mermaid',d,'```']
        d=render_view(project,'functional_information')
        if d: lines += ['','### Funktion och information','', '```mermaid',d,'```']

    # Logical
    lines += ['','## 6. Logisk arkitektur','']
    logical=[]
    for t in ('Subsystem','Component','Service','DataStore'):
        for e in typed[t]: logical.append((t,e.get('name'),e.get('description','')))
    lines += [table(['Typ','Namn','Ansvar/beskrivning'],logical).rstrip()]
    if include_diagrams:
        d=render_view(project,'logical_component')
        if d: lines += ['','```mermaid',d,'```']

    # Integration
    lines += ['','## 7. Integrationsarkitektur','']
    ints=[]
    for t in ('Interface','API','Message','Event'):
        for e in typed[t]:
            provider=e.get('provider') or e.get('producer') or ''
            pname=elements.get(provider,{}).get('name',provider) if provider else ''
            consumers=', '.join(elements.get(x,{}).get('name',x) for x in (e.get('consumers') or []))
            ints.append((t,e.get('name'),pname,consumers,e.get('protocol','') or e.get('communication_mode','')))
    lines += [table(['Typ','Namn','Producent/provider','Konsumenter','Protokoll/läge'],ints).rstrip()]
    if include_diagrams:
        d=render_view(project,'integration')
        if d: lines += ['','```mermaid',d,'```']

    # Scenarios
    lines += ['','## 8. Viktiga scenarier','']
    scenarios=typed['Scenario']
    lines += [table(['Scenario','Use case','Utfall'],[(e.get('name'),elements.get(e.get('use_case'),{}).get('name',e.get('use_case','')),e.get('outcome','')) for e in scenarios]).rstrip()]
    if include_diagrams:
        d=render_view(project,'sequence')
        if d: lines += ['','```mermaid',d,'```']

    # Runtime/deployment
    lines += ['','## 9. Runtime och deployment','']
    deploy=[]
    for t in ('Environment','DeploymentNode','RuntimeUnit'):
        for e in typed[t]: deploy.append((t,e.get('name'),e.get('environment_kind','') or e.get('node_kind','') or e.get('runtime_kind',''),e.get('technology','') or e.get('platform','')))
    lines += [table(['Typ','Namn','Slag','Teknik/plattform'],deploy).rstrip()]
    if include_diagrams:
        d=render_view(project,'deployment')
        if d: lines += ['','```mermaid',d,'```']

    # Decisions
    lines += ['','## 10. Arkitekturbeslut och constraints','']
    dec_rows=[]
    for e in typed['ArchitectureDecision']:
        dec_rows.append(('Beslut',e.get('name') or e.get('title'),e.get('decision',''),e.get('rationale','')))
    for e in typed['Constraint']:
        dec_rows.append(('Constraint',e.get('name'),e.get('statement',''),e.get('rationale','')))
    lines += [table(['Typ','Namn','Beslut/regel','Motiv'],dec_rows).rstrip()]

    # Unknowns
    lines += ['','## 11. Kända osäkerheter','']
    uncertain=[]
    for e in elements.values():
        os=origins(e)
        if 'inferred' in os or 'unresolved' in os or not evidence_refs(e):
            reason='infererad' if 'inferred' in os else ('olöst' if 'unresolved' in os else 'saknar evidensreferens')
            uncertain.append((e.get('id'),e.get('type'),e.get('name'),reason))
    for r in rels:
        os=origins(r)
        if 'inferred' in os or 'unresolved' in os or not evidence_refs(r):
            reason='infererad' if 'inferred' in os else ('olöst' if 'unresolved' in os else 'saknar evidensreferens')
            uncertain.append((r.get('id'),'Relationship',r.get('type'),reason))
    if uncertain:
        lines.append('Följande delar bör verifieras eller kompletteras med evidens. Att något listas här betyder inte automatiskt att det är fel.')
    lines += ['',table(['ID','Typ','Namn/relation','Orsak'],uncertain).rstrip()]

    # Sources/evidence
    lines += ['','## 12. Källor och evidens','']
    sources=typed['Source']; refs=typed['SourceReference']; evid=typed['Evidence']
    lines.append(f'Modellen innehåller **{len(sources)} källa/källor**, **{len(refs)} källreferens(er)** och **{len(evid)} evidenspost(er)**.')
    src_rows=[]
    for s in sources:
        src_rows.append((s.get('id'),s.get('name'),s.get('source_kind') or s.get('kind',''),s.get('location','') or s.get('path','')))
    lines += ['',table(['ID','Källa','Typ','Plats'],src_rows).rstrip()]

    # Metadata footer
    counts=Counter(e.get('type') for e in elements.values())
    lines += ['','---','',f'_Genererad av System Modeller {read_version()} från {len(elements)} modelelement och {len(rels)} relationer._','']
    return '\n'.join(lines)

def read_version():
    return (Path(__file__).resolve().parents[1]/'VERSION').read_text(encoding='utf-8').strip()

def main():
    ap=argparse.ArgumentParser(description='Generate the MVP architecture description from a System Modeller project.')
    ap.add_argument('project',type=Path)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--no-diagrams',action='store_true')
    ns=ap.parse_args()
    try:
        text=architecture_description(ns.project,not ns.no_diagrams)
    except Exception as e:
        print(f'ERROR: {e}'); return 2
    if ns.output:
        ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(text,encoding='utf-8')
    else:
        print(text,end='')
    return 0
if __name__=='__main__': raise SystemExit(main())
