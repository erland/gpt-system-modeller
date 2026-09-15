#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import report_profile
import view_split


def fail(message):
    print('FAIL:', message)
    return 1


def logical_fixture():
    elements = []
    links = []
    for s in range(2):
        sid = f'SUB-{s+1:06d}'
        elements.append({'id': sid, 'type': 'Subsystem', 'name': f'Domain {s+1}'})
        for i in range(13):
            cid = f'CMP-{s*20+i+1:06d}'
            elements.append({'id': cid, 'type': 'Component', 'name': f'Component {s+1}-{i+1}'})
            links.append({'id': f'R-{s}-{i}', 'type': 'part_of', 'source': cid, 'target': sid})
    return {
        'view': {'type': 'logical_component', 'name': 'Logical Component View'},
        'elements': elements,
        'links': links,
        'summary': {'element_count': len(elements), 'link_count': len(links)},
    }


def fallback_fixture():
    elements = [{'id': f'API-{i:06d}', 'type': 'API', 'name': f'API {i}'} for i in range(1, 23)]
    links = [
        {'id': f'R-{i}', 'type': 'exchanges_information', 'source': elements[i]['id'], 'target': elements[i+1]['id']}
        for i in range(len(elements)-1)
    ]
    return {
        'view': {'type': 'integration', 'name': 'Integration View'},
        'elements': elements,
        'links': links,
        'summary': {'element_count': len(elements), 'link_count': len(links)},
    }


def main():
    profile = report_profile.load()
    policy = profile['diagrams']

    result = logical_fixture()
    split = view_split.split_result(result, policy)
    if not split['split'] or split.get('strategy') != 'semantic_anchors':
        return fail('logical view did not use semantic anchor splitting')
    if split.get('anchors') != ['SUB-000001', 'SUB-000002']:
        return fail(f'unexpected logical anchors {split.get("anchors")}')
    if not split['parts'] or split['parts'][0]['split']['role'] != 'overview':
        return fail('overview must be first')

    detail = [p for p in split['parts'] if p['split']['role'] == 'detail']
    covered = {e['id'] for p in detail for e in p['elements']}
    expected = {e['id'] for e in result['elements']}
    if covered != expected:
        return fail('detail views do not cover every original element')
    for part in split['parts']:
        if part['summary']['element_count'] > policy['preferred_max_elements']:
            return fail('split part exceeds preferred element budget')
        if part['summary']['link_count'] > policy['preferred_max_relationships']:
            return fail('split part exceeds preferred relationship budget')

    again = view_split.split_result(result, policy)
    if split != again:
        return fail('view splitting is not deterministic')

    fallback = view_split.split_result(fallback_fixture(), policy)
    if not fallback['split'] or fallback.get('strategy') != 'stable_id_fallback':
        return fail('fallback split strategy missing')
    if not all(p['summary']['element_count'] <= policy['preferred_max_elements'] for p in fallback['parts']):
        return fail('fallback part exceeds preferred element budget')

    small = {
        'view': {'type': 'logical_component'},
        'elements': [{'id': 'SUB-000001', 'type': 'Subsystem', 'name': 'Small'}],
        'links': [],
        'summary': {'element_count': 1, 'link_count': 0},
    }
    unchanged = view_split.split_result(small, policy)
    if unchanged['split'] or unchanged['parts'][0] is not small:
        return fail('small view should remain unsplit')

    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    m = re.fullmatch(r'0\.1\.0-dev\.(\d+)', version)
    if not m or int(m.group(1)) < 45:
        return fail(f'expected version >= dev.45, got {version}')
    status = (ROOT / 'STATUS.md').read_text(encoding='utf-8')
    progress = re.search(r'Plan B progress: B(\d+) / B12', status)
    if not progress or int(progress.group(1)) < 7:
        return fail('STATUS not advanced to B7 or later')

    print('B7 tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
