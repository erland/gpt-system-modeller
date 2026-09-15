#!/usr/bin/env python3
from pathlib import Path
import subprocess, yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'evaluate_small_model.py'
SUITE = ROOT / 'evals' / 'small-model' / 'suite.yaml'
PASS = ROOT / 'tests' / 'fixtures' / 'small-model-pass.yaml'
FAIL = ROOT / 'tests' / 'fixtures' / 'small-model-critical-fail.yaml'


def fail(msg):
    print('FAIL:', msg)
    return 1


def run(*args):
    return subprocess.run(['python3', str(SCRIPT), *map(str, args)], cwd=ROOT, text=True, capture_output=True)


def main():
    for p in (SCRIPT, SUITE, PASS, FAIL):
        if not p.is_file():
            return fail(f'missing B4 artifact {p.relative_to(ROOT)}')

    r = run('--suite', SUITE)
    if r.returncode != 0 or '6 cases, 4 dimensions' not in r.stdout:
        return fail('suite validation failed: ' + r.stdout + r.stderr)

    r = run('--suite', SUITE, '--results', PASS, '--format', 'yaml')
    if r.returncode != 0:
        return fail('passing fixture did not pass: ' + r.stdout + r.stderr)
    summary = yaml.safe_load(r.stdout)
    expected_dimensions = {'instruction_adherence', 'model_quality', 'provenance_uncertainty', 'deterministic_tools'}
    if set(summary.get('dimensions', {})) != expected_dimensions:
        return fail('dimension separation missing')
    if not summary['overall']['passed'] or not summary['canonical_mutation_allowed']:
        return fail('passing fixture unexpectedly blocked')
    if summary['critical_failures']:
        return fail('passing fixture has critical failures')

    r = run('--suite', SUITE, '--results', FAIL, '--format', 'yaml')
    if r.returncode != 1:
        return fail('critical-failure fixture should return exit code 1')
    summary = yaml.safe_load(r.stdout)
    if summary['overall']['passed']:
        return fail('critical-failure fixture marked overall pass')
    if summary['canonical_mutation_allowed']:
        return fail('critical failure did not block canonical mutation')
    if 'runtime-order-001' not in summary['critical_failures']:
        return fail('expected critical case not reported')
    if summary['dimensions']['instruction_adherence']['passed']:
        return fail('instruction adherence dimension should fail')
    for dimension in ('model_quality', 'provenance_uncertainty', 'deterministic_tools'):
        if not summary['dimensions'][dimension]['passed']:
            return fail(f'unrelated dimension {dimension} should still pass')

    readme = (ROOT / 'evals' / 'small-model' / 'README.md').read_text(encoding='utf-8')
    for phrase in ('evaluate_small_model.py', 'small_local', 'canonical_mutation_allowed'):
        if phrase not in readme:
            return fail(f'B4 documentation missing {phrase}')

    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if version != '0.1.0-dev.42':
        return fail(f'expected B4 version 0.1.0-dev.42, got {version}')
    status = (ROOT / 'STATUS.md').read_text(encoding='utf-8')
    if 'Plan B progress: B4 / B12' not in status or 'Next: B5' not in status:
        return fail('STATUS not advanced to B4/B5')

    print('B4 small-model regression tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
