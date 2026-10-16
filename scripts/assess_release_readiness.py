#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path
import yaml

def gate(status,message=None):
    d={'status':status}
    if message: d['message']=message
    return d

def run_json(cmd,cwd):
    r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
    try: return r.returncode,json.loads(r.stdout)
    except Exception: return r.returncode,None

def assess(root, include_build_state=False):
    cfg=yaml.safe_load((root/'gpt-project.yaml').read_text(encoding='utf-8'))
    st=yaml.safe_load((root/'project-status.yaml').read_text(encoding='utf-8'))
    gates={}; warnings=[]; blockers=[]

    bis=st.get('blocking_issues') or st.get('blockers') or []
    if bis:
        gates['project_status']=gate('blocked'); blockers += [str(x) for x in bis]
    else:
        gates['project_status']=gate('pass')

    _,lint=run_json([sys.executable,str(root/'scripts'/'lint_gpt_project.py'),'--project-root',str(root),'--json'],root)
    if lint is None or lint.get('summary',{}).get('errors',0):
        gates['lint']=gate('blocked','Lint errors or unavailable.'); blockers.append('Lint is not clean.')
    else:
        lint_warnings=[f for f in lint.get('findings',[]) if f.get('severity')=='warning']
        if include_build_state:
            lint_warnings=[f for f in lint_warnings if f.get('code')!='GP202']
        if lint_warnings:
            gates['lint']=gate('warning'); warnings.append('Lint warnings remain.')
        else:
            gates['lint']=gate('pass')

    _,hyg=run_json([sys.executable,str(root/'scripts'/'project_hygiene.py'),'--project-root',str(root),'--mode','final','--json'],root)
    if hyg is None or hyg.get('result')=='blocked':
        gates['final_hygiene']=gate('blocked'); blockers.append('Final hygiene is blocked.')
    else:
        hyg_findings=hyg.get('findings',[])
        if include_build_state:
            hyg_findings=[f for f in hyg_findings if f.get('code')!='HY100']
        if any(f.get('severity')=='blocked' for f in hyg_findings):
            gates['final_hygiene']=gate('blocked'); blockers.append('Final hygiene is blocked.')
        elif hyg_findings:
            gates['final_hygiene']=gate('warning'); warnings.append('Final hygiene has warnings.')
        else:
            gates['final_hygiene']=gate('pass')

    gates['test_model']=gate('pass' if cfg.get('testing') else 'warning')
    if not cfg.get('testing'): warnings.append('Testing configuration missing.')

    runtime_targets=cfg.get('build_system',{}).get('runtime_targets') or {}
    gates['runtime_parity']=gate('not_run' if cfg.get('runtime_parity') else 'not_applicable')
    custom_enabled=bool(cfg.get('runtime',{}).get('custom_gpt',{}).get('enabled'))
    gates['custom_gpt_platform_validation']=gate('not_run' if custom_enabled and cfg.get('platform_validation') else 'not_applicable')

    if include_build_state:
        dist=root/'dist'
        manifest_path=dist/'DELIVERY-MANIFEST.json'
        version=None
        if manifest_path.exists():
            try:
                version=json.loads(manifest_path.read_text(encoding='utf-8')).get('version')
            except Exception:
                version=None
        if version:
            r=subprocess.run([
                sys.executable,
                str(root/'scripts'/'verify_distribution_outputs.py'),
                '--project-root',str(root),
                '--version',str(version)
            ],cwd=root,capture_output=True,text=True)
            if r.returncode==0:
                gates['build']=gate('pass')
            else:
                gates['build']=gate('blocked','Expected build artifacts missing or incomplete.'); blockers.append('Build artifacts are missing or incomplete.')
        else:
            gates['build']=gate('blocked','Delivery manifest/version missing.'); blockers.append('Delivery manifest/version is missing.')

        r=subprocess.run([sys.executable,str(root/'scripts'/'validate_distributions.py'),'--project-root',str(root)],cwd=root,capture_output=True,text=True)
        if r.returncode==0:
            gates['distribution_validation']=gate('pass')
        else:
            gates['distribution_validation']=gate('blocked'); blockers.append('Distribution validation failed.')
    else:
        gates['build']=gate('not_run'); gates['distribution_validation']=gate('not_run')

    result='blocked' if blockers else ('ready_with_warnings' if warnings else 'ready')
    dstate='blocked' if blockers else ('ready_with_warnings' if warnings else 'ready')
    distributions={'project_zip':dstate}
    for target_cfg in runtime_targets.values():
        artifact_type=target_cfg.get('artifact_type')
        runtime_key=target_cfg.get('runtime_key')
        if not artifact_type:
            continue
        enabled=bool(cfg.get('runtime',{}).get(runtime_key,{}).get('enabled'))
        distributions[artifact_type]=dstate if enabled else 'not_applicable'

    return {'schema_version':1,'result':result,'gates':gates,
            'distributions':distributions,
            'warnings':sorted(set(warnings)),'blockers':sorted(set(blockers))}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--json',action='store_true'); ap.add_argument('--include-build-state',action='store_true')
    args=ap.parse_args(); result=assess(Path(args.project_root).resolve(),args.include_build_state)
    if args.json: print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print('Release readiness:',result['result'].upper())
        for k,v in result['distributions'].items(): print(f'- {k}: {v}')
    return 1 if result['result']=='blocked' else 0
if __name__=='__main__': raise SystemExit(main())
