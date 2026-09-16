#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import report_profile


def fail(message):
    print('FAIL:', message)
    return 1


def expect_value_error(fn, phrase):
    try:
        fn()
    except ValueError as exc:
        if phrase not in str(exc):
            raise AssertionError(f'expected error containing {phrase!r}, got {exc!r}')
        return
    raise AssertionError(f'expected ValueError containing {phrase!r}')


def main():
    catalog_path = ROOT/'metamodel/report-profiles/catalog.yaml'
    doc_path = ROOT/'docs/report-profile-groundwork.md'
    for path in (catalog_path, doc_path):
        if not path.is_file():
            return fail(f'missing B11 artifact {path.relative_to(ROOT)}')

    catalog = report_profile.load_catalog()
    if catalog['default_profile'] != 'standard':
        return fail('standard must remain default profile')
    if catalog.get('user_selectable') is not False:
        return fail('profile selection must remain internal in B11')

    entries = report_profile.available_profiles(catalog)
    ids = [p['id'] for p in entries]
    if ids != ['overview', 'standard', 'detailed']:
        return fail(f'unexpected profile identities/order: {ids}')
    states = {p['id']:(p['status'],p['implemented'],p['user_selectable']) for p in entries}
    if states['standard'] != ('stable', True, False):
        return fail('standard lifecycle state incorrect')
    for pid in ('overview','detailed'):
        if states[pid] != ('planned', False, False):
            return fail(f'{pid} must remain planned and not selectable')

    default = report_profile.load()
    explicit = report_profile.load(profile='standard')
    if default != explicit or default.get('profile') != 'standard':
        return fail('default and explicit standard profile must resolve identically')
    if report_profile.resolve_profile_path('standard').name != 'standard.yaml':
        return fail('standard does not resolve to standard.yaml')

    try:
        expect_value_error(lambda: report_profile.load(profile='overview'), 'planned but not implemented')
        expect_value_error(lambda: report_profile.load(profile='detailed'), 'planned but not implemented')
        expect_value_error(lambda: report_profile.load(profile='missing'), 'unknown report profile')
        expect_value_error(lambda: report_profile.load(ROOT/'metamodel/report-profiles/standard.yaml', profile='standard'), 'either an explicit profile path or a named profile')
    except AssertionError as exc:
        return fail(str(exc))

    if (ROOT/'metamodel/report-profiles/overview.yaml').exists() or (ROOT/'metamodel/report-profiles/detailed.yaml').exists():
        return fail('B11 must not implement overview/detailed profile files yet')

    doc = doc_path.read_text(encoding='utf-8')
    for phrase in ('overview', 'standard', 'detailed', 'planned but not implemented', 'user_selectable: false'):
        if phrase not in doc:
            return fail(f'B11 documentation missing {phrase}')

    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    m = re.fullmatch(r'0\.1\.0-dev\.(\d+)', version)
    if not m or int(m.group(1)) < 49:
        return fail(f'expected version >= dev.49, got {version}')
    status = (ROOT/'STATUS.md').read_text(encoding='utf-8')
    progress = re.search(r'Plan B progress: B(\d+) / B12', status)
    if not progress or int(progress.group(1)) < 11:
        return fail('STATUS not advanced to B11 or later')
    if '### B11 result' not in status:
        return fail('STATUS missing B11 result history')

    print('B11 tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
