#!/usr/bin/env python3
"""Run standalone A/B/C scripts explicitly; pytest alone does not execute their main()."""
import argparse, concurrent.futures, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEGACY={
 'test_a34':'Requires old scripts/ci_build.py CI contract',
 'test_a39':'Requires old isolated runner convention',
 'test_b12':'Requires old PR distribution workflow',
 'test_c1':'Requires 1.5 runtimes/custom_gpt structure',
 'test_c2':'Requires 1.5 parity/build keys',
 'test_c5':'Requires retired Custom GPT distribution and old packaging names',
 'test_c6':'Requires old scripts/ci_build.py release workflow',
 'test_c7':'Requires retired Custom GPT release checks',
}
def run(p,seconds):
 t=time.monotonic()
 try:
  cp=subprocess.run([sys.executable,str(p)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=seconds)
  return {'test':p.stem,'status':'PASS' if cp.returncode==0 else 'FAIL','exit_code':cp.returncode,'seconds':round(time.monotonic()-t,2),'detail':(cp.stdout+cp.stderr)[-3000:]}
 except subprocess.TimeoutExpired as e:
  return {'test':p.stem,'status':'TIMEOUT','seconds':round(time.monotonic()-t,2),'detail':str(e)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--timeout',type=int,default=35);ap.add_argument('--workers',type=int,default=4);ap.add_argument('--output',default='abc-results.json');args=ap.parse_args()
 files=sorted(ROOT.glob('tests/test_[abc][0-9]*.py'))
 historical=[{'test':p.stem,'status':'LEGACY_INCOMPATIBLE','reason':LEGACY[p.stem]} for p in files if p.stem in LEGACY]
 active=[p for p in files if p.stem not in LEGACY]
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  results=list(pool.map(lambda p:run(p,args.timeout),active))
 results=sorted(results+historical,key=lambda x:x['test'])
 out=Path(args.output);out.write_text(json.dumps({'policy':{'workers':args.workers,'per_test_timeout_seconds':args.timeout,'legacy_exclusions_need_replacement_tests':True},'results':results},ensure_ascii=False,indent=2)+'\n')
 from collections import Counter
 counts=Counter(r['status'] for r in results)
 print(f'{len(files)} scripts: '+', '.join(f'{k}={v}' for k,v in sorted(counts.items())))
 for r in results:
  if r['status'] not in ('PASS','LEGACY_INCOMPATIBLE'):print(r['test'],r['status'],r.get('detail','')[-170:].replace('\n',' '))
 return 1 if counts['FAIL'] or counts['TIMEOUT'] or counts['LEGACY_INCOMPATIBLE'] else 0
if __name__=='__main__':raise SystemExit(main())
