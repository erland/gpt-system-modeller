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
    release_env = {
        'GITHUB_EVENT_NAME': 'release',
        'GITHUB_EVENT_RELEASE_TAG_NAME': 'v3.4.5',
    }
    info = versioning.resolve(env=release_env)
    if (info.release_version, info.distribution_version, info.source, info.tag) != ('3.4.5','3.4.5','github_release','v3.4.5'):
        return fail(f'GitHub Release tag is not authoritative: {info}')

    # Release context must win over a conflicting generic tag context.
    conflict = dict(release_env, GITHUB_REF_TYPE='tag', GITHUB_REF_NAME='v9.9.9')
    info2 = versioning.resolve(env=conflict)
    if info2.release_version != '3.4.5' or info2.source != 'github_release':
        return fail('release event did not take precedence over generic tag context')

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        env = os.environ.copy(); env.update(release_env)
        subprocess.run(['python3', str(ROOT/'scripts/ci_build.py'), '--output-dir', str(td)], cwd=ROOT, env=env, check=True)
        chat = td/'system-modeller-chat-v3.4.5.zip'
        custom = td/'system-modeller-custom-gpt-v3.4.5.zip'
        if not chat.is_file() or not custom.is_file():
            return fail('release event did not control artifact filenames')
        with zipfile.ZipFile(chat) as zf:
            if zf.read('system-modeller/VERSION').decode().strip() != '3.4.5':
                return fail('release event did not control embedded Chat VERSION')
        with zipfile.ZipFile(custom) as zf:
            manifest = yaml.safe_load(zf.read('system-modeller-custom-gpt/manifest.yaml'))
            if manifest.get('version') != '3.4.5':
                return fail('release event did not control Custom GPT manifest')
        bm = yaml.safe_load((td/'build-manifest.yaml').read_text(encoding='utf-8'))
        if bm.get('version_source') != 'github_release' or bm.get('release_tag') != 'v3.4.5':
            return fail('build manifest does not record github_release source')

    wf = (ROOT/'.github/workflows/build-distributions.yml').read_text(encoding='utf-8')
    required = [
        'release:',
        'types: [published]',
        'pull_request:',
        'branches: [main]',
        'name: Verify repository',
        'name: Build and validate distributions',
        'name: Build and publish release assets',
        'contents: write',
        'github.event.release.tag_name',
        'gh release upload',
        '--clobber',
    ]
    for phrase in required:
        if phrase not in wf:
            return fail('workflow missing A37 behavior: '+phrase)
    if "tags: ['v*.*.*']" in wf:
        return fail('legacy tag-push trigger still present')

    doc = (ROOT/'docs/github-actions.md').read_text(encoding='utf-8')
    for phrase in ['pull_request', 'release', 'published', 'Actions artifact', 'GitHub Release-sidan', 'github_release']:
        if phrase not in doc:
            return fail('A37 documentation missing: '+phrase)

    print('A37 tests passed')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
