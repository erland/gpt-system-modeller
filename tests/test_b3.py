#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def fail(m):
    print('FAIL:',m); return 1

def main():
    runtime=ROOT/'instructions/chat-runtime.md'
    bootstrap=ROOT/'SYSTEM-MODELLER-CHAT.md'
    for p in (runtime,bootstrap):
        if not p.is_file(): return fail(f'missing B3 artifact {p.relative_to(ROOT)}')

    text=runtime.read_text(encoding='utf-8')
    flow='INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE'
    if flow not in text: return fail('explicit runtime flow missing')

    headings=['### 1. INSPECT','### 2. VALIDATE','### 3. PLAN','### 4. CHANGE','### 5. VALIDATE','### 6. DERIVE','### 7. PACKAGE']
    positions=[]
    for h in headings:
        p=text.find(h)
        if p<0: return fail(f'missing operation heading {h}')
        positions.append(p)
    if positions!=sorted(positions): return fail('runtime operations out of order')

    required=[
        'scripts/context.py',
        '--focus <text>',
        'scripts/validate.py',
        'scripts/model.py',
        'scripts/ids.py',
        'scripts/view.py',
        'scripts/report.py',
        'scripts/package_project.py',
        'Gör inte modelländringar före den första `VALIDATE`',
        'Gå inte vidare till `DERIVE` eller `PACKAGE` om nya valideringsfel har introducerats',
        'Skapa inte ett nytt element när ett befintligt element har samma semantiska innebörd',
        'context.py` är arbetskontext, inte sanningskälla',
    ]
    for phrase in required:
        if phrase not in text: return fail(f'runtime contract missing: {phrase}')

    bootstrap_text=bootstrap.read_text(encoding='utf-8')
    for phrase in (flow,'scripts/context.py','Mutera inte kanonisk modell före första valideringen'):
        if phrase not in bootstrap_text: return fail(f'bootstrap missing B3 contract: {phrase}')

    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    m=re.fullmatch(r'0\.1\.0-dev\.(\d+)',version)
    if not m or int(m.group(1))<41: return fail(f'expected version >= dev.41, got {version}')

    status=(ROOT/'STATUS.md').read_text(encoding='utf-8')
    if 'Plan B progress: B3 / B12' not in status: return fail('STATUS not advanced to B3')
    if 'B4' not in status: return fail('next Plan B step missing')

    print('B3 tests passed'); return 0

if __name__=='__main__': raise SystemExit(main())
