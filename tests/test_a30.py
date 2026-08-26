#!/usr/bin/env python3
from pathlib import Path
import re, sys, tempfile, zipfile
import yaml
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'examples/reference-order-system'
sys.path.insert(0,str(ROOT/'scripts'))
import analyze, package_chat, package_project, report, validate, view
TYPES=['system_context','functional_overview','use_case_overview','information_overview','functional_information','logical_component','use_case_realization','integration','sequence','deployment']
def fail(m): print('FAIL:',m); return 1
def same(a,b): return Path(a).read_bytes()==Path(b).read_bytes()
def main():
    required=[ROOT/'SYSTEM-MODELLER-CHAT.md',ROOT/'instructions/chat-runtime.md',ROOT/'scripts/package_project.py',ROOT/'scripts/package_chat.py',ROOT/'docs/mvp-reference-test.md',REF/'project/project.yaml',REF/'golden/architecture-description.md']
    for p in required:
        if not p.is_file(): return fail('missing A30 artifact '+str(p.relative_to(ROOT)))
    findings=validate.validate(REF/'project')
    bad=[f for f in findings if f.severity in {'ERROR','WARNING'}]
    if bad: return fail('reference project has findings: '+str([(f.severity,f.code) for f in bad]))
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        packet=analyze.inventory((REF/'input').resolve())
        inv=td/'inventory.yaml'; inv.write_text(yaml.safe_dump(packet,allow_unicode=True,sort_keys=False),encoding='utf-8')
        if not same(inv,REF/'golden/source-inventory.yaml'): return fail('source inventory differs from golden')
        for typ in TYPES:
            result=view.materialize(REF/'project',view.default_definition(typ))
            y=td/f'{typ}.yaml'; y.write_text(yaml.safe_dump(result,allow_unicode=True,sort_keys=False),encoding='utf-8')
            m=td/f'{typ}.mmd'; m.write_text(view.mermaid(result),encoding='utf-8')
            if not same(y,REF/'golden/views'/f'{typ}.yaml'): return fail('golden YAML view mismatch '+typ)
            if not same(m,REF/'golden/views'/f'{typ}.mmd'): return fail('golden Mermaid view mismatch '+typ)
        text=report.architecture_description(REF/'project',include_diagrams=True)
        rp=td/'architecture-description.md'; rp.write_text(text,encoding='utf-8')
        # The golden report captures A30 content; later development versions may only
        # change the generated-by footer. Normalize that version before comparison.
        golden=(REF/'golden/architecture-description.md').read_text(encoding='utf-8')
        norm=lambda t: re.sub(r'(Genererad av System Modeller )0\.1\.0-dev\.\d+',r'\g<1>0.1.0-dev.X',t)
        if norm(text)!=norm(golden): return fail('architecture report differs from golden beyond version footer')
        z=td/'reference-order-system.zip'; z2=td/'reference-order-system-2.zip'
        package_project.build(REF/'project',z); package_project.build(REF/'project',z2)
        if not same(z,z2): return fail('project ZIP is not deterministic')
        unpack=td/'unpack'; unpack.mkdir()
        with zipfile.ZipFile(z) as zf: zf.extractall(unpack)
        unpacked=unpack/'project'
        if any(f.severity=='ERROR' for f in validate.validate(unpacked)): return fail('unpacked project ZIP invalid')
        c1=td/'chat1.zip'; c2=td/'chat2.zip'; package_chat.build(c1); package_chat.build(c2)
        if not same(c1,c2): return fail('Chat-ZIP is not deterministic')
        with zipfile.ZipFile(c1) as zf: names=set(zf.namelist())
        for name in ['system-modeller/SYSTEM-MODELLER-CHAT.md','system-modeller/instructions/chat-runtime.md','system-modeller/instructions/source-analysis.md','system-modeller/scripts/validate.py','system-modeller/scripts/view.py','system-modeller/scripts/report.py','system-modeller/metamodel/README.md','system-modeller/schemas/project.schema.json','system-modeller/examples/reference-order-system/project/project.yaml']:
            if name not in names: return fail('Chat-ZIP missing '+name)
    v=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'0\.1\.0-dev\.(\d+)',v) or int(v.rsplit('.',1)[1])<30: return fail('version not A30 or later')
    status=(ROOT/'STATUS.md').read_text(encoding='utf-8')
    if 'A1–A30 / A30' not in status or 'Plan A complete' not in status: return fail('status not complete')
    print('A30 tests passed'); return 0
if __name__=='__main__': raise SystemExit(main())
