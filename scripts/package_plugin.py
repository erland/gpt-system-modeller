#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, tempfile
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import versioning

FIXED_DATE=(2020,1,1,0,0,0)
RUNTIME_SCRIPTS=["context.py","validate.py","model.py","view.py","report.py","package_project.py","analyze.py"]
SUPPORT_SCRIPTS=["ids.py","report_profile.py","sequence_diagrams.py","view_split.py","diagram_complexity.py"]

def copy_file(src:Path,dst:Path)->None:
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)

def copy_tree(src:Path,dst:Path)->None:
    for p in sorted(src.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc",".pyo"}:
            copy_file(p,dst/p.relative_to(src))

def runtime_contract(version:str)->dict:
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    return {
      "schema_version":1,"runtime_id":"openai_plugin","version":version,
      "compatibility":"equivalent_runtime_dependent",
      "canonical_instruction":"skills/system-modeller/SKILL.md",
      "workspace_state":{"authority":"canonical_yaml","required_project_file":"project.yaml","persistent_workspace":"required","conversation_authoritative":False},
      "runtime_requirements":{
        "filesystem":{"read":"required","write":"required"},
        "code_execution":{"level":"required","languages":["python"],"fallback":"block"},
        "python_dependencies":{"level":"required","packages":["PyYAML","jsonschema"]},
        "project_packaging":{"level":"required"}
      },
      "tool_policy":{
        "mutation_sequence":["INSPECT","VALIDATE","PLAN","CHANGE","VALIDATE","DERIVE","PACKAGE"],
        "mutating_tool":"model","approval_required_for_mutation":True,"unrun_verification_may_pass":False
      },
      "tools":project["contracts"]["tools"],
      "script_resources":{"runtime":RUNTIME_SCRIPTS,"support":SUPPORT_SCRIPTS,"mcp_required_for_resource_use":False}
    }

def build_tree(target:Path,version:str)->None:
    skill=target/"skills"/"system-modeller"; skill.mkdir(parents=True,exist_ok=True)
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    canonical=(ROOT/project["project"]["canonical_instruction"]).read_text(encoding="utf-8").strip()
    plugin={"$schema":"https://agent-plugins.org/schemas/1.0.0/plugin.schema.json","name":"system-modeller","version":version,"description":project["project"]["description"].strip()}
    (target/"plugin.json").write_text(json.dumps(plugin,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (target/"runtime-contract.json").write_text(json.dumps(runtime_contract(version),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    skill_text = """---
name: system-modeller
description: Build, maintain, validate, analyse and present traceable YAML system models with deterministic tools and explicit provenance.
metadata:
  source: generated-from-canonical-project
---

## Runtime requirements

- Filesystem read/write and a persistent writable workspace are required.
- Python code execution is required for canonical validation, mutation, deterministic derivation and packaging.
- Python packages PyYAML and jsonschema are required by the packaged runtime tools.
- Run packaged tools rather than simulating deterministic results.
- Never report an unrun validation or packaging operation as PASS.
- Canonical YAML in the target system project is authoritative; conversation history is not project state.
- Mutating model operations require explicit approval.
- Always preserve the canonical sequence INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE.

## Canonical behavior

""" + canonical + """

## Packaged tools

- scripts/context.py — inspect and establish deterministic project context.
- scripts/validate.py — validate canonical YAML before and after mutation.
- scripts/model.py — query/mutate canonical YAML; mutation requires approval.
- scripts/view.py — derive architecture views.
- scripts/report.py — generate the architecture report.
- scripts/package_project.py — build the portable project ZIP.
- scripts/analyze.py — inventory source material for modelling evidence.

The scripts are resources, not MCP wrappers. Use compatible host code execution directly when available.

## Runtime data

The skill packages schemas/ and metamodel/ because the deterministic tools resolve these resources relative to their runtime location.

## References

- references/modeling-principles.md
- references/source-analysis.md
"""
    (skill/"SKILL.md").write_text(skill_text,encoding="utf-8")
    for name in RUNTIME_SCRIPTS+SUPPORT_SCRIPTS: copy_file(ROOT/"scripts"/name,skill/"scripts"/name)
    copy_tree(ROOT/"schemas",skill/"schemas"); copy_tree(ROOT/"metamodel",skill/"metamodel")
    copy_file(ROOT/"docs/modeling-principles.md",skill/"references"/"modeling-principles.md")
    copy_file(ROOT/"instructions/source-analysis.md",skill/"references"/"source-analysis.md")
    (target/"README.md").write_text("# System Modeller – OpenAI Plugin\n\nSkills-first, equivalent-runtime-dependent distribution. Full canonical mutation, validation, derivation and packaging require a writable workspace and compatible Python execution.\n",encoding="utf-8")
    (target/"VERSION").write_text(version+"\n",encoding="utf-8")

def deterministic_zip(source:Path,out:Path)->Path:
    out=out.resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(source.rglob("*")):
            if p.is_file():
                info=ZipInfo(p.relative_to(source).as_posix(),FIXED_DATE); info.compress_type=ZIP_DEFLATED; info.external_attr=0o644<<16
                zf.writestr(info,p.read_bytes())
    return out

def build(out:Path,distribution_version:str|None=None)->Path:
    version=distribution_version or (ROOT/"VERSION").read_text(encoding="utf-8").strip()
    with tempfile.TemporaryDirectory(prefix="system-modeller-plugin-") as td:
        root=Path(td)/"system-modeller-plugin"; build_tree(root,version); return deterministic_zip(root,out)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); ap.add_argument("--release-version")
    ns=ap.parse_args(); info=versioning.resolve(explicit=ns.release_version)
    out=ns.output or ROOT/"distributions"/f"system-modeller-plugin-v{info.release_version}.zip"
    print(build(out,info.distribution_version)); return 0

if __name__=="__main__": raise SystemExit(main())
