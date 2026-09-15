#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import diagram_complexity
import report_profile


def fail(message):
    print('FAIL:', message)
    return 1


def synthetic(view_type, elements, links, sequences=None):
    result = {
        'view': {'type': view_type},
        'elements': [{'id': f'E-{i}'} for i in range(elements)],
        'links': [{'id': f'R-{i}'} for i in range(links)],
        'summary': {'element_count': elements, 'link_count': links},
    }
    if sequences is not None:
        result['sequences'] = sequences
    return result


def main():
    profile = report_profile.load_standard_profile()
    policy = diagram_complexity.diagram_policy(profile)

    expected = {
        'preferred_max_elements': 12,
        'hard_max_elements': 20,
        'preferred_max_relationships': 18,
        'hard_max_relationships': 30,
    }
    for key, value in expected.items():
        if int(policy.get(key, -1)) != value:
            return fail(f'wrong B6 budget {key}')

    cases = [
        (12, 18, 'within_preferred'),
        (13, 18, 'above_preferred'),
        (12, 19, 'above_preferred'),
        (21, 1, 'above_hard'),
        (1, 31, 'above_hard'),
    ]
    for elements, links, expected_class in cases:
        measured = diagram_complexity.measure_result(synthetic('logical_component', elements, links), policy)
        if measured['classification'] != expected_class:
            return fail(f'classification mismatch for {elements}/{links}: {measured["classification"]}')
        if measured['split_recommended'] != (expected_class != 'within_preferred'):
            return fail('split recommendation does not follow profile budget')

    seq = synthetic('sequence', 4, 0, [
        {
            'participants': [{'ref': 'ACT-1'}, {'ref': 'CMP-1'}],
            'messages': [{'id': 'M-1'}, {'id': 'M-2'}],
        },
        {
            'participants': [{'ref': 'CMP-1'}, {'ref': 'EXT-1'}],
            'messages': [{'id': 'M-3'}],
        },
    ])
    measured_seq = diagram_complexity.measure_result(seq, policy)
    if measured_seq.get('sequence') != {'interaction_count': 2, 'participant_count': 3, 'message_count': 3}:
        return fail('sequence participant/message metrics incorrect')

    reference = ROOT / 'examples/reference-order-system/project'
    report = diagram_complexity.measure_project(reference)
    types = [v['view_type'] for v in report['views']]
    expected_types = diagram_complexity.profile_view_types(profile)
    if types != expected_types:
        return fail('profile view order not preserved')
    if not report['views'] or any('classification' not in v for v in report['views']):
        return fail('reference view metrics missing')
    sequence = [v for v in report['views'] if v['view_type'] == 'sequence']
    if len(sequence) != 1 or 'sequence' not in sequence[0]:
        return fail('reference sequence metrics missing')

    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    m = re.fullmatch(r'0\.1\.0-dev\.(\d+)', version)
    if not m or int(m.group(1)) < 44:
        return fail(f'expected version >= dev.44, got {version}')

    status = (ROOT / 'STATUS.md').read_text(encoding='utf-8')
    progress = re.search(r'Plan B progress: B(\d+) / B12', status)
    if not progress or int(progress.group(1)) < 6:
        return fail('STATUS not advanced to B6 or later')

    print('B6 tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
