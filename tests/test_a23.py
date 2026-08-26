#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1

def main():
    required=[ROOT/'metamodel/project-format.yaml',ROOT/'schemas/project.schema.json',ROOT/'docs/system-project-format.md',ROOT/'templates/system-project/project.yaml',ROOT/'examples/reference-order-system/project/project.yaml']
    for p in required:
        if not p.is_file(): return fail(f'missing A23 artifact: {p.relative_to(ROOT)}')
    schema=json.loads((ROOT/'schemas/project.schema.json').read_text())
    validator=Draft202012Validator(schema)
    for manifest in [ROOT/'templates/system-project/project.yaml',ROOT/'examples/reference-order-system/project/project.yaml']:
        data=yaml.safe_load(manifest.read_text())
        errs=list(validator.iter_errors(data))
        if errs:
            for e in errs: print('FAIL:',manifest.relative_to(ROOT),list(e.path),e.message)
            return 1
    bad=yaml.safe_load((ROOT/'templates/system-project/project.yaml').read_text())
    bad['format']='other'
    if validator.is_valid(bad): return fail('invalid project format accepted')
    bad2=yaml.safe_load((ROOT/'templates/system-project/project.yaml').read_text())
    bad2['project']['schema_version']='v1'
    if validator.is_valid(bad2): return fail('invalid schema_version accepted')
    template=ROOT/'templates/system-project'
    expected_dirs=['model','interactions','implementation','sources','views','reports','issues','exports']
    for d in expected_dirs:
        if not (template/d).is_dir(): return fail(f'missing template directory {d}')
    expected_shards=['context.yaml','functions.yaml','use-cases.yaml','information.yaml','structure.yaml','integrations.yaml','data-stores.yaml','deployment.yaml','decisions.yaml','relationships.yaml']
    for f in expected_shards:
        p=template/'model'/f
        if not p.is_file(): return fail(f'missing model shard {f}')
        y=yaml.safe_load(p.read_text())
        if not isinstance(y,dict) or 'elements' not in y or 'relationships' not in y: return fail(f'bad shard structure {f}')
    meta=yaml.safe_load((ROOT/'metamodel/project-format.yaml').read_text())
    if meta.get('manifest',{}).get('path')!='project.yaml': return fail('project manifest path not canonical')
    if 'model/' not in meta.get('required_paths',[]): return fail('model/ not required')
    docs=(ROOT/'docs/system-project-format.md').read_text()
    for phrase in ('system-project/','project.yaml','exports/','Shards och global identitet','Separation från GPT-paketet'):
        if phrase not in docs: return fail(f'doc missing {phrase}')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',version) or int(version.rsplit('.',1)[1])<23: return fail('version not A23 or later')
    print('A23 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
