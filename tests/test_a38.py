#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import versioning


def fail(msg):
    print('FAIL:', msg)
    return 1


def main():
    # Reproduce the A36 failure mode: a branch/main build carries dev version.
    dev = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if versioning.normalize_distribution_version(dev) != dev:
        return fail('development distribution version rejected')
    if versioning.normalize_distribution_version('1.2.3') != '1.2.3':
        return fail('release distribution version rejected')

    # Release/tag parsing remains strict and must not accept development suffixes.
    try:
        versioning.normalize_release(dev)
    except ValueError:
        pass
    else:
        return fail('normalize_release accepted a development version')

    for bad in ['v1.2.3-dev.4', '1.2', '1.2.3-beta', 'release-1.2.3']:
        try:
            versioning.normalize_distribution_version(bad)
        except ValueError:
            pass
        else:
            return fail('invalid distribution version accepted: ' + bad)

    # Build and validate exactly as the main/workflow_dispatch build-check does.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        env = os.environ.copy()
        for key in ['GITHUB_EVENT_NAME', 'GITHUB_EVENT_RELEASE_TAG_NAME', 'GITHUB_REF_TYPE', 'GITHUB_REF_NAME', 'GITHUB_REF', 'SYSTEM_MODELLER_RELEASE_VERSION']:
            env.pop(key, None)
        subprocess.run(['python3', str(ROOT/'scripts/ci_build.py'), '--output-dir', str(td)], cwd=ROOT, env=env, check=True)
        info = versioning.resolve(env={})
        chat = td / f'system-modeller-chat-v{info.release_version}.zip'
        custom = td / f'system-modeller-custom-gpt-v{info.release_version}.zip'
        subprocess.run([
            'python3', str(ROOT/'scripts/validate_custom_gpt.py'),
            '--custom', str(custom), '--chat', str(chat),
            '--expected-version', info.distribution_version,
        ], cwd=ROOT, env=env, check=True)

    # Release path must still validate a plain semver.
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        env = os.environ.copy()
        env.update({'GITHUB_EVENT_NAME':'release','GITHUB_EVENT_RELEASE_TAG_NAME':'v4.5.6'})
        subprocess.run(['python3', str(ROOT/'scripts/ci_build.py'), '--output-dir', str(td)], cwd=ROOT, env=env, check=True)
        subprocess.run([
            'python3', str(ROOT/'scripts/validate_custom_gpt.py'),
            '--custom', str(td/'system-modeller-custom-gpt-v4.5.6.zip'),
            '--chat', str(td/'system-modeller-chat-v4.5.6.zip'),
            '--expected-version', '4.5.6',
        ], cwd=ROOT, env=env, check=True)

    wf=(ROOT/'.github/workflows/build-distributions.yml').read_text(encoding='utf-8')
    if '--expected-version "${DIST_VERSION}"' not in wf:
        return fail('workflow no longer tests resolved development distribution version')

    print('A38 tests passed')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
