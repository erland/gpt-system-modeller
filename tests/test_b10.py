#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import evaluate_report_regression


def fail(message):
    print('FAIL:', message)
    return 1


def main():
    required = [
        ROOT/'evals/report-regression/cases.yaml',
        ROOT/'scripts/evaluate_report_regression.py',
        ROOT/'docs/report-regression.md',
    ]
    for path in required:
        if not path.is_file():
            return fail(f'missing B10 artifact {path.relative_to(ROOT)}')

    first = evaluate_report_regression.run()
    second = evaluate_report_regression.run()
    if first != second:
        return fail('B10 report regression is not deterministic')
    if not first.get('passed') or first.get('case_count') != 3:
        return fail(f'B10 suite failed: {first}')

    results = {r['id']: r for r in first['results']}
    if set(results) != {'small', 'medium', 'dense'}:
        return fail('B10 cases must be small, medium and dense')
    if results['small']['split_view_count'] != 0:
        return fail('small case should not require automatic splitting')
    if results['medium']['split_view_count'] < 3:
        return fail('medium case does not exercise enough B7 split paths')
    if results['dense']['split_view_count'] < 4:
        return fail('dense case must exercise all B7 split view types')
    if not (results['small']['report_length'] < results['medium']['report_length'] < results['dense']['report_length']):
        return fail('report levels do not increase in representative density')
    for case_id, expected in [('small',1),('medium',2),('dense',4)]:
        if results[case_id]['sequence_diagram_count'] != expected:
            return fail(f'{case_id}: wrong B8 sequence diagram count')
        for view in results[case_id]['view_results']:
            if view['elements'] <= 0:
                return fail(f'{case_id}: empty regression view {view["type"]}')

    doc = (ROOT/'docs/report-regression.md').read_text(encoding='utf-8')
    for phrase in ('small', 'medium', 'dense', 'preferred', 'canonical facts', 'B11'):
        if phrase not in doc:
            return fail(f'B10 documentation missing {phrase}')

    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    m = re.fullmatch(r'0\.1\.0-dev\.(\d+)', version)
    if not m or int(m.group(1)) < 48:
        return fail(f'expected version >= dev.48, got {version}')
    status = (ROOT/'STATUS.md').read_text(encoding='utf-8')
    progress = re.search(r'Plan B progress: B(\d+) / B12', status)
    if not progress or int(progress.group(1)) < 10:
        return fail('STATUS not advanced to B10 or later')

    print('B10 end-to-end report regression tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
