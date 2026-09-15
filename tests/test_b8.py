#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import report
import sequence_diagrams


def fail(message):
    print('FAIL:', message)
    return 1


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')


def main():
    for path in (ROOT/'scripts/sequence_diagrams.py', ROOT/'docs/scenario-sequence-diagrams.md'):
        if not path.is_file():
            return fail(f'missing B8 artifact {path.relative_to(ROOT)}')

    with tempfile.TemporaryDirectory() as td:
        project = Path(td)/'project'
        shutil.copytree(ROOT/'templates/system-project', project)
        write(project/'model/context.yaml', {'elements':[
            {'id':'ACT-000001','type':'Actor','name':'Kund','abstraction_level':'conceptual','origin':['declared']},
            {'id':'CMP-000001','type':'Component','name':'Order','abstraction_level':'logical','origin':['declared']},
            {'id':'EXT-000001','type':'ExternalSystem','name':'Betalning','abstraction_level':'conceptual','origin':['declared']},
        ], 'relationships':[]})
        write(project/'interactions/scenarios.yaml', {'elements':[
            {'id':'SCN-000002','type':'Scenario','name':'Betala order','abstraction_level':'conceptual','origin':['declared']},
            {'id':'SCN-000001','type':'Scenario','name':'Registrera order','abstraction_level':'conceptual','origin':['declared']},
            {'id':'INT-000002','type':'Interaction','name':'Skicka betalning','abstraction_level':'logical','scenario':'SCN-000002','participants':[{'ref':'CMP-000001'},{'ref':'EXT-000001'}],'messages':[{'id':'IM-000002','order':1,'sender':'CMP-000001','receiver':'EXT-000001','label':'Pay','communication_mode':'synchronous'}],'origin':['declared']},
            {'id':'INT-000001','type':'Interaction','name':'Skapa order','abstraction_level':'logical','scenario':'SCN-000001','participants':[{'ref':'ACT-000001'},{'ref':'CMP-000001'}],'messages':[{'id':'IM-000001','order':1,'sender':'ACT-000001','receiver':'CMP-000001','label':'Create','communication_mode':'synchronous'}],'origin':['declared']},
        ], 'relationships':[]})

        diagrams = sequence_diagrams.materialize(project)
        if [d['interaction_id'] for d in diagrams] != ['INT-000002','INT-000001']:
            return fail('interaction ordering is not stable by scenario/name')
        if len(diagrams) != 2:
            return fail('expected one diagram per Interaction')
        for d in diagrams:
            seqs = d['result'].get('sequences') or []
            if len(seqs) != 1:
                return fail('diagram contains more than one Interaction')
            if seqs[0]['interaction']['id'] != d['interaction_id']:
                return fail('diagram contains wrong Interaction')
        if diagrams[0]['title'] != 'Betala order – Skicka betalning':
            return fail('scenario/interaction title incorrect')

        text = report.architecture_description(project, include_diagrams=True)
        for heading in ('### Betala order – Skicka betalning','### Registrera order – Skapa order'):
            if heading not in text:
                return fail(f'report missing {heading}')
        scenario_section = text.split('## 8. Viktiga scenarier',1)[1].split('## 9. Runtime och deployment',1)[0]
        if scenario_section.count('```mermaid') != 2:
            return fail('report must render exactly one Mermaid block per Interaction')
        first = scenario_section.index('Betala order – Skicka betalning')
        second = scenario_section.index('Registrera order – Skapa order')
        if first >= second:
            return fail('report sequence order is not deterministic')
        if 'participant EXT_000001' in scenario_section[second:]:
            return fail('unrelated participant leaked into second sequence diagram')

    doc = (ROOT/'docs/scenario-sequence-diagrams.md').read_text(encoding='utf-8')
    for phrase in ('one_interaction_per_diagram', 'filters.interaction_id', 'Scenario – Interaction'):
        if phrase not in doc:
            return fail(f'B8 documentation missing {phrase}')

    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    m = re.fullmatch(r'0\.1\.0-dev\.(\d+)', version)
    if not m or int(m.group(1)) < 46:
        return fail(f'expected version >= dev.46, got {version}')
    status = (ROOT/'STATUS.md').read_text(encoding='utf-8')
    progress = re.search(r'Plan B progress: B(\d+) / B12', status)
    if not progress or int(progress.group(1)) < 8:
        return fail('STATUS not advanced to B8 or later')

    print('B8 tests passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
