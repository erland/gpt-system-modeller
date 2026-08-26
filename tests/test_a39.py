#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def fail(msg):
    print('FAIL:', msg)
    return 1


def release_env():
    env = os.environ.copy()
    env.update({
        'GITHUB_EVENT_NAME': 'release',
        'GITHUB_EVENT_RELEASE_TAG_NAME': 'v9.8.7',
        'GITHUB_REF_TYPE': 'tag',
        'GITHUB_REF_NAME': 'v9.8.7',
        'GITHUB_REF': 'refs/tags/v9.8.7',
        'SYSTEM_MODELLER_RELEASE_VERSION': 'v9.8.7',
    })
    return env


def main():
    runner = ROOT / 'scripts/run_test_isolated.sh'
    suite = ROOT / 'scripts/test.sh'
    doc = ROOT / 'docs/test-environment-isolation.md'
    for p in [runner, suite, doc]:
        if not p.is_file():
            return fail('missing A39 artifact ' + str(p.relative_to(ROOT)))

    text = runner.read_text(encoding='utf-8')
    for var in [
        'GITHUB_EVENT_NAME', 'GITHUB_EVENT_RELEASE_TAG_NAME',
        'GITHUB_REF_TYPE', 'GITHUB_REF_NAME', 'GITHUB_REF',
        'SYSTEM_MODELLER_RELEASE_VERSION'
    ]:
        if f'-u {var}' not in text:
            return fail('isolation runner does not clear ' + var)

    suite_text = suite.read_text(encoding='utf-8')
    if 'run_test_isolated.sh' not in suite_text:
        return fail('test suite does not use isolated runner')

    # Reproduce the real hosted-release failure context. These historical
    # tests expect VERSION fallback and must remain unaffected by outer CI env.
    env = release_env()
    for test in ['tests/test_a32.py', 'tests/test_a34.py', 'tests/test_a35.py']:
        proc = subprocess.run(
            ['bash', str(runner), test], cwd=ROOT, env=env,
            text=True, capture_output=True
        )
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr)
            return fail(f'{test} is not isolated from release environment')

    # Release semantics themselves remain explicitly tested and must still pass.
    for test in ['tests/test_a36.py', 'tests/test_a37.py', 'tests/test_a38.py']:
        proc = subprocess.run(
            ['bash', str(runner), test], cwd=ROOT, env=env,
            text=True, capture_output=True
        )
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr)
            return fail(f'{test} lost explicit release/tag coverage')

    print('A39 tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
