#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import tempfile
import zipfile
import yaml
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import versioning


def fail(msg):
    print('FAIL:', msg)
    return 1


def main():
    if versioning.normalize_release('v2.3.4') != '2.3.4': return fail('tag normalization failed')
    for bad in ['v1.2', 'release-1.2.3', 'v1.2.3-beta']:
        try: versioning.normalize_release(bad)
        except ValueError: pass
        else: return fail('invalid release tag accepted: '+bad)

    repo = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    fallback = versioning.resolve(env={})
    if fallback.repository_version != repo or fallback.distribution_version != repo:
        return fail('VERSION fallback changed')

    tag = versioning.resolve(env={'GITHUB_REF_TYPE':'tag','GITHUB_REF_NAME':'v2.3.4'})
    if (tag.release_version, tag.distribution_version, tag.source) != ('2.3.4','2.3.4','github_tag'):
        return fail('GitHub tag is not authoritative')

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        env=os.environ.copy(); env['GITHUB_REF_TYPE']='tag'; env['GITHUB_REF_NAME']='v2.3.4'
        subprocess.run(['python3',str(ROOT/'scripts/ci_build.py'),'--output-dir',str(td)],cwd=ROOT,env=env,check=True)
        chat=td/'system-modeller-chat-v2.3.4.zip'
        custom=td/'system-modeller-custom-gpt-v2.3.4.zip'
        if not chat.is_file() or not custom.is_file(): return fail('tag did not control ZIP filenames')
        with zipfile.ZipFile(chat) as zf:
            if zf.read('system-modeller/VERSION').decode().strip() != '2.3.4':
                return fail('tag did not control embedded Chat VERSION')
        with zipfile.ZipFile(custom) as zf:
            manifest=yaml.safe_load(zf.read('system-modeller-custom-gpt/manifest.yaml'))
            inst=zf.read('system-modeller-custom-gpt/instructions.md').decode('utf-8')
            if manifest.get('version') != '2.3.4': return fail('tag did not control Custom manifest')
            if 'Version: **2.3.4**' not in inst: return fail('tag did not control Custom instructions')
        bm=yaml.safe_load((td/'build-manifest.yaml').read_text(encoding='utf-8'))
        if bm.get('release_version')!='2.3.4' or bm.get('distribution_version')!='2.3.4':
            return fail('tag did not control build manifest')
        if bm.get('version_source')!='github_tag' or bm.get('release_tag')!='v2.3.4':
            return fail('build manifest does not record tag source')
        subprocess.run(['python3',str(ROOT/'scripts/validate_custom_gpt.py'),'--custom',str(custom),'--chat',str(chat),'--expected-version','2.3.4'],cwd=ROOT,env=env,check=True)

    # A36 introduced tag-authoritative version resolution. A37 may evolve the
    # workflow trigger from tag push to release.published, so keep this
    # regression focused on the resolver/build behavior rather than old YAML.
    wf=(ROOT/'.github/workflows/build-distributions.yml').read_text(encoding='utf-8')
    if 'versioning' not in (ROOT/'scripts/ci_build.py').read_text(encoding='utf-8'):
        return fail('CI builder no longer uses shared version resolver')
    if 'build' not in wf.lower():
        return fail('distribution workflow unexpectedly missing build behavior')

    print('A36 tests passed')
    return 0

if __name__=='__main__': raise SystemExit(main())
