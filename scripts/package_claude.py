#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tempfile
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import versioning
SPEC=ROOT/"templates/claude-project-distribution.yaml"
FIXED_DATE=(2020,1,1,0,0,0)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def load_spec():
    return yaml.safe_load(SPEC.read_text(encoding="utf-8"))

def build_tree(target:Path, distribution_version:str|None=None):
    spec=load_spec(); version=distribution_version or (ROOT/"VERSION").read_text().strip()
    target.mkdir(parents=True,exist_ok=True)
    (target/"knowledge").mkdir(exist_ok=True)
    (target/"project").mkdir(exist_ok=True)
    canonical=(ROOT/"instructions/chat-runtime.md").read_text(encoding="utf-8").strip()
    instructions=f"""# System Modeller – Claude Project Instructions

Version: **{version}**

Följ det canonical System Modeller-beteendet nedan.

Claude Project har ingen lokal exekvering av repositoryts Python-scripts. Påstå därför aldrig att scripts har körts. Om tillförlitlig validering inte kan utföras ska canonical mutation stoppas. Read-only analys får göras manuellt när resultatet hålls spårbart mot canonical YAML.

{canonical}
"""
    (target/"project-instructions.md").write_text(instructions,encoding="utf-8")
    source_hashes={}
    for rel in spec["canonical_sources"]["instructions"]:
        p=ROOT/rel; source_hashes[rel]=sha(p)
    for rel in spec["canonical_sources"]["knowledge"]:
        p=ROOT/rel; source_hashes[rel]=sha(p)
        text=p.read_text(encoding="utf-8")
        (target/"knowledge"/Path(rel).name).write_text(text,encoding="utf-8")
    contract={
      "schema_version":"1.0","runtime":"claude_project","version":version,
      "canonical_instruction":"project-instructions.md",
      "workspace_state":"reduced",
      "tools":{"local_script_execution":"unavailable","canonical_mutation_requires_reliable_validation":True},
      "runtime_sequence":["INSPECT","VALIDATE","PLAN","CHANGE","VALIDATE","DERIVE","PACKAGE"]
    }
    (target/"project/runtime-contract.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (target/"README.md").write_text("# System Modeller – Claude Project\n\nImportera Project Instructions och Knowledge-filerna i ett Claude Project. Lokala Python-verktyg ingår inte som körbara verktyg i denna runtime.\n",encoding="utf-8")
    (target/"VERSION").write_text(version+"\n",encoding="utf-8")
    generated={}
    for p in sorted(target.rglob("*")):
        if p.is_file():
            rel=p.relative_to(target).as_posix(); generated[rel]={"sha256":sha(p),"bytes":p.stat().st_size}
    manifest={"schema_version":1,"id":spec["id"],"distribution_type":"claude_project","version":version,"generator":"scripts/package_claude.py","source_hashes":dict(sorted(source_hashes.items())),"generated":generated}
    (target/"manifest.yaml").write_text(yaml.safe_dump(manifest,sort_keys=False,allow_unicode=True),encoding="utf-8")
    return manifest

def deterministic_zip(source:Path,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(source.rglob("*")):
            if not p.is_file(): continue
            rel=p.relative_to(source).as_posix()
            info=ZipInfo(f"system-modeller-claude/{rel}",FIXED_DATE); info.compress_type=ZIP_DEFLATED; info.external_attr=0o644<<16
            zf.writestr(info,p.read_bytes())
    return out

def build(out:Path,directory:Path|None=None,distribution_version:str|None=None):
    if directory is not None:
        if directory.exists():
            for p in sorted(directory.rglob("*"),reverse=True):
                if p.is_file(): p.unlink()
                elif p.is_dir(): p.rmdir()
        directory.mkdir(parents=True,exist_ok=True)
        build_tree(directory,distribution_version); return deterministic_zip(directory,out)
    with tempfile.TemporaryDirectory(prefix="system-modeller-claude-") as td:
        root=Path(td)/"system-modeller-claude"; build_tree(root,distribution_version); return deterministic_zip(root,out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); ap.add_argument("--directory",type=Path); ap.add_argument("--release-version")
    ns=ap.parse_args(); info=versioning.resolve(explicit=ns.release_version)
    out=ns.output or ROOT/"distributions"/f"system-modeller-claude-v{info.release_version}.zip"
    print(build(out,ns.directory,info.distribution_version)); return 0
if __name__=="__main__": raise SystemExit(main())
