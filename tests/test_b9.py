#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import pdf_contract
import report_profile


def fail(message):
    print('FAIL:', message)
    return 1


def main():
    for path in (ROOT/'scripts/pdf_contract.py', ROOT/'docs/pdf-presentation-contract.md'):
        if not path.is_file():
            return fail(f'missing B9 artifact {path.relative_to(ROOT)}')

    report = report_profile.load()
    pdf = report_profile.pdf_presentation(report)
    if pdf['page'] != {
        'size':'A4','orientation':'portrait','margin_top_mm':18,'margin_right_mm':16,
        'margin_bottom_mm':18,'margin_left_mm':16,
    }:
        return fail('unexpected PDF page contract')

    headings = pdf['headings']
    if [headings[k] for k in ('title_level','section_level','diagram_group_level','detail_diagram_level')] != [1,2,3,4]:
        return fail('unexpected PDF heading hierarchy')
    if headings.get('major_section_page_break_before') is not True or headings.get('keep_heading_with_next') is not True:
        return fail('PDF heading pagination contract missing')

    diagrams = pdf['diagrams']
    expected_diagrams = {
        'max_width_percent':92,
        'max_height_mm':155,
        'caption_position':'below',
        'caption_prefix':'Diagram',
    }
    for key, value in expected_diagrams.items():
        if diagrams.get(key) != value:
            return fail(f'unexpected PDF diagram rule {key}')
    if diagrams.get('keep_with_caption') is not True:
        return fail('diagram/caption keep rule missing')

    tables = pdf['tables']
    if not tables.get('repeat_header') or tables.get('allow_row_split') is not False or not tables.get('wrap_cells'):
        return fail('PDF table behavior incomplete')
    if float(tables.get('font_size_pt')) != 8.5:
        return fail('unexpected PDF table font size')

    contract = pdf_contract.build_contract()
    if contract.get('format') != 'system-modeller-pdf-presentation-v1':
        return fail('PDF contract format missing')
    if [x['id'] for x in contract['sections']] != report_profile.REQUIRED_SECTION_IDS:
        return fail('PDF contract section order diverges from report profile')
    policy = contract['diagram_policy']
    if policy.get('split_large_views') is not True or policy.get('one_interaction_per_sequence_diagram') is not True:
        return fail('B7/B8 diagram policy not propagated into PDF contract')

    with tempfile.TemporaryDirectory() as td:
        bad = yaml.safe_load((ROOT/'metamodel/report-profiles/standard.yaml').read_text(encoding='utf-8'))
        bad['architecture_report']['presentation']['pdf']['diagrams']['max_width_percent'] = 120
        p = Path(td)/'bad.yaml'
        p.write_text(yaml.safe_dump(bad, allow_unicode=True, sort_keys=False), encoding='utf-8')
        try:
            report_profile.load(p)
        except ValueError:
            pass
        else:
            return fail('invalid PDF width was accepted')

    doc = (ROOT/'docs/pdf-presentation-contract.md').read_text(encoding='utf-8')
    for phrase in ('A4 portrait', '155 mm', 'repeat their header', 'one Interaction per diagram', 'B10'):
        if phrase not in doc:
            return fail(f'B9 documentation missing {phrase}')

    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    m = re.fullmatch(r'0\.1\.0-dev\.(\d+)', version)
    if not m or int(m.group(1)) < 47:
        return fail(f'expected version >= dev.47, got {version}')
    status = (ROOT/'STATUS.md').read_text(encoding='utf-8')
    progress = re.search(r'Plan B progress: B(\d+) / B12', status)
    if not progress or int(progress.group(1)) < 9:
        return fail('STATUS not advanced to B9 or later')

    print('B9 tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
