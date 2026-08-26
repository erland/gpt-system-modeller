#!/usr/bin/env python3
from pathlib import Path
import re
import yaml
ROOT=Path(__file__).resolve().parents[1]

def fail(msg):
    print('FAIL:',msg); return 1

def main():
    spec=ROOT/'docs/custom-gpt-distribution.md'
    mapping=ROOT/'templates/custom-gpt-distribution.yaml'
    if not spec.is_file(): return fail('missing Custom GPT distribution specification')
    if not mapping.is_file(): return fail('missing declarative Custom GPT distribution map')
    cfg=yaml.safe_load(mapping.read_text(encoding='utf-8'))
    if cfg.get('version_source')!='VERSION': return fail('VERSION is not the sole declared version source')
    if cfg.get('distribution_type')!='custom_gpt': return fail('wrong distribution type')
    if cfg.get('output',{}).get('instructions')!='instructions.md': return fail('instructions output not defined')
    knowledge=cfg.get('knowledge',[])
    expected=[
        '01-modeling-core.md','02-metamodel-reference.md',
        '03-project-format-and-validation.md','04-views-and-architecture-description.md',
        '05-source-analysis-and-evidence.md','06-reference-example.md'
    ]
    if [x.get('output') for x in knowledge]!=expected: return fail('knowledge bundle/order differs from A31 contract')
    # Every explicit source in the map must exist already in the canonical repo.
    paths=[]
    paths.extend(cfg.get('instructions',{}).get('canonical_sources',[]))
    for item in knowledge:
        paths.extend(item.get('sources',[]))
        paths.extend(item.get('generated_inputs',[]))
    for rel in paths:
        if not (ROOT/rel).exists(): return fail('mapped canonical source missing: '+rel)
    shared=cfg.get('source_of_truth',{}).get('shared_runtime',[])
    if 'instructions/chat-runtime.md' not in shared or 'instructions/source-analysis.md' not in shared:
        return fail('shared runtime sources are incomplete')
    excludes=cfg.get('exclude_from_custom_gpt',[])
    for required in ['tests/','scripts/','distributions/']:
        if required not in excludes: return fail('missing Custom GPT exclusion '+required)
    text=spec.read_text(encoding='utf-8')
    for phrase in ['Source-of-truth-princip','genererad projektion','Funktionell paritet','VERSION','templates/custom-gpt-distribution.yaml','instructions.md','Knowledge']:
        if phrase not in text: return fail('distribution spec missing '+phrase)
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<31:
        return fail('version not A31 or later')
    status=(ROOT/'STATUS.md').read_text(encoding='utf-8')
    if 'A31' not in status or 'Custom GPT' not in status: return fail('status not updated for A31')
    print('A31 tests passed'); return 0

if __name__=='__main__': raise SystemExit(main())
