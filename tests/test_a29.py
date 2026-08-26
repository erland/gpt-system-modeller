#!/usr/bin/env python3
from pathlib import Path
import json,re,shutil,subprocess,tempfile,yaml
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print('FAIL:',m); return 1
def main():
    required=['metamodel/analysis.yaml','schemas/analysis.schema.json','docs/source-analysis.md','instructions/source-analysis.md','scripts/analyze.py','templates/system-project/sources/observations.yaml','examples/a29-analysis-result.yaml']
    for x in required:
        if not (ROOT/x).is_file(): return fail('missing '+x)
    schema=json.loads((ROOT/'schemas/analysis.schema.json').read_text())
    ex=yaml.safe_load((ROOT/'examples/a29-analysis-result.yaml').read_text())
    obs=ex['analysis_result']['observations'][0]
    # Validate through the full schema document so local $refs resolve correctly.
    from referencing import Registry, Resource
    reg=Registry().with_resource(schema['$id'],Resource.from_contents(schema))
    errs=list(Draft202012Validator({'$ref':schema['$id']+'#/$defs/analysisResult'},registry=reg).iter_errors(ex))
    if errs: return fail('analysis example invalid: '+errs[0].message)
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/'src'; src.mkdir();
        (src/'README.md').write_text('# Order service\nHandles orders.',encoding='utf-8')
        (src/'pom.xml').write_text('<project/>',encoding='utf-8')
        j=src/'src/main/java/example/OrderService.java'; j.parent.mkdir(parents=True); j.write_text('class OrderService {}',encoding='utf-8')
        k=src/'k8s/deployment.yaml'; k.parent.mkdir(); k.write_text('kind: Deployment',encoding='utf-8')
        r=subprocess.run(['python3',str(ROOT/'scripts/analyze.py'),'inventory',str(src)],text=True,capture_output=True)
        if r.returncode: return fail(r.stdout+r.stderr)
        packet=yaml.safe_load(r.stdout)['analysis_packet']; cats={f['path']:f['category'] for f in packet['files']}
        if cats.get('README.md')!='documentation' or cats.get('pom.xml')!='build' or cats.get('src/main/java/example/OrderService.java')!='source_code' or cats.get('k8s/deployment.yaml')!='deployment': return fail('inventory classification incorrect: '+str(cats))
        # Verify Observation is accepted by project validator with matching provenance.
        project=Path(td)/'project'; shutil.copytree(ROOT/'templates/system-project',project)
        def write(rel,data): (project/rel).write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding='utf-8')
        write('sources/sources.yaml',{'elements':[{'id':'SRC-000001','name':'OrderService.java','source_kind':'source_code'}],'relationships':[]})
        write('sources/references.yaml',{'elements':[{'id':'REF-000001','source':'SRC-000001','file':'OrderService.java'}],'relationships':[]})
        write('sources/observations.yaml',{'elements':[obs],'relationships':[]})
        vr=subprocess.run(['python3',str(ROOT/'scripts/validate.py'),str(project),'--format','json'],text=True,capture_output=True)
        if vr.returncode: return fail('validator rejects observation: '+vr.stdout+vr.stderr)
    docs=(ROOT/'docs/source-analysis.md').read_text(encoding='utf-8')
    for phrase in ('Source material','Observation','Class ≠ Component','Endpoint ≠ UseCase','DatabaseTable ≠ InformationObject','A30'):
        if phrase not in docs: return fail('docs missing '+phrase)
    v=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',v) or int(v.rsplit('.',1)[1])<29: return fail('version not A29 or later')
    print('A29 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
