#!/usr/bin/env python3
"""Bounded A/B/C standalone regression; historical tests are explicit blockers."""
import argparse, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL={'test_a34','test_a39','test_b12','test_c1','test_c2','test_c5','test_c6','test_c7'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['a','b','c'],required=True);ap.add_argument('--timeout',type=int,default=90);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--from-number',type=int,default=1);ap.add_argument('--to-number',type=int,default=999);ns=ap.parse_args()
 files=sorted((p for p in (ROOT/'tests').glob(f'test_{ns.group}[0-9]*.py') if ns.from_number <= int(p.stem.split(ns.group)[-1]) <= ns.to_number),key=lambda p:int(p.stem.split(ns.group)[-1]))
 if not files:raise SystemExit('No test files found in selected range')
 results=[]
 for file in files:
  if file.stem in HISTORICAL:
   results.append(dict(test=file.stem,status='MIGRATED_CONTRACT',replacement='tests/test_migration_1625.py',note='Historical 1.5-only assertion; replacement coverage must pass independently'))
   continue
  start=time.monotonic()
  try:
   cp=subprocess.run([sys.executable,str(file)],cwd=ROOT,capture_output=True,text=True,timeout=ns.timeout)
   results.append(dict(test=file.stem,status='PASS' if cp.returncode==0 else 'FAIL',exit_code=cp.returncode,seconds=round(time.monotonic()-start,2),output=(cp.stdout+cp.stderr)[-3500:]))
  except subprocess.TimeoutExpired as exc:
   results.append(dict(test=file.stem,status='TIMEOUT',seconds=round(time.monotonic()-start,2),output=str(exc)))
 ns.output.parent.mkdir(parents=True,exist_ok=True)
 summary={s:sum(r['status']==s for r in results) for s in ['PASS','FAIL','TIMEOUT','MIGRATED_CONTRACT']}
 ns.output.write_text(json.dumps({'group':ns.group,'from_number':ns.from_number,'to_number':ns.to_number,'timeout':ns.timeout,'summary':summary,'results':results},ensure_ascii=False,indent=2)+'\n')
 print(f'{ns.group.upper()}: {summary} → {ns.output}')
 for r in results:
  if r['status'] in ('FAIL','TIMEOUT'):print(r['test'],r['status'],r.get('output','')[-160:])
 return 1 if summary['FAIL'] or summary['TIMEOUT'] else 0
if __name__=='__main__':raise SystemExit(main())
