#!/usr/bin/env python3
from pathlib import Path
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]

def fail(msg):
    print('FAIL:', msg)
    return 1

def main():
    required = [
        ROOT/'scripts/release_check.py',
        ROOT/'docs/release-readiness.md',
        ROOT/'RELEASE-NOTES-v0.1.0.md',
    ]
    for p in required:
        if not p.is_file():
            return fail('missing A35 artifact '+str(p.relative_to(ROOT)))
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    if '-dev.' not in version:
        return fail('A35 regression expects a development VERSION fallback')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        proc=subprocess.run(['python3',str(ROOT/'scripts/release_check.py'),'--output-dir',str(td)],cwd=ROOT,text=True,capture_output=True)
        if proc.returncode != 0:
            print(proc.stdout); print(proc.stderr)
            return fail('release_check.py failed')
        report=yaml.safe_load((td/'release-readiness.yaml').read_text(encoding='utf-8'))
        if report.get('status') != 'READY': return fail('release readiness is not READY')
        if report.get('github_actions_runtime_verified') is not False: return fail('local A35 must not claim hosted GitHub verification')
        for name in ['system-modeller-chat-v0.1.0.zip','system-modeller-custom-gpt-v0.1.0.zip','build-manifest.yaml']:
            if not (td/name).is_file(): return fail('missing release output '+name)
        checks=report.get('local_checks',{})
        if not all(checks.values()): return fail('not all local checks passed')
    doc=(ROOT/'docs/release-readiness.md').read_text(encoding='utf-8')
    for phrase in ['GitHub Actions runtime verification','release-readiness.yaml']:
        if phrase not in doc: return fail('release readiness documentation missing '+phrase)
    print('A35 tests passed')
    return 0

if __name__=='__main__': raise SystemExit(main())
