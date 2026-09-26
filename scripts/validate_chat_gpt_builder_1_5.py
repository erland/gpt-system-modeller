#!/usr/bin/env python3
from pathlib import Path
import argparse
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]

def member(zf,suffix):
    matches=[n for n in zf.namelist() if n.endswith("/"+suffix) or n==suffix]
    if len(matches)!=1:
        raise ValueError(f"expected one {suffix}, found {matches}")
    return matches[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",required=True)
    a=ap.parse_args()
    artifact=Path(a.artifact)
    if not artifact.is_absolute():
        artifact=ROOT/artifact

    errors=[]
    normalized=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))
    canonical=(ROOT/"instructions/chat-runtime.md").read_text(encoding="utf-8")

    if not artifact.is_file():
        print(f"FAILED: missing Chat ZIP: {artifact}")
        return 1

    with zipfile.ZipFile(artifact) as zf:
        if zf.testzip():
            errors.append("Chat ZIP is corrupt")
        names=[n for n in zf.namelist() if not n.endswith("/")]
        roots={n.split("/")[0] for n in names}
        if roots!={"system-modeller"}:
            errors.append(f"unexpected Chat ZIP root(s): {sorted(roots)}")

        required=[
            "SYSTEM-MODELLER-CHAT.md",
            "instructions/chat-runtime.md",
            "instructions/source-analysis.md",
            "scripts/context.py",
            "scripts/validate.py",
            "scripts/model.py",
            "scripts/view.py",
            "scripts/report.py",
            "scripts/package_project.py",
            "scripts/analyze.py",
            "schemas/system-project.schema.json",
            "templates/system-project/project.yaml",
        ]
        for req in required:
            try:
                member(zf,req)
            except ValueError as exc:
                errors.append(str(exc))

        try:
            packaged=zf.read(member(zf,"instructions/chat-runtime.md")).decode("utf-8")
            if packaged!=canonical:
                errors.append("packaged Chat canonical instruction is not byte-identical")
            folded=packaged.casefold()
            for marker in [
                "kanoniska yaml-modellen",
                "påstå aldrig att ett verktyg har körts",
                "validering inte kan utföras",
                "inspect → validate → plan → change → validate → derive → package",
            ]:
                if marker.casefold() not in folded:
                    errors.append(f"Chat instruction missing invariant: {marker}")
        except ValueError as exc:
            errors.append(str(exc))

        try:
            bootstrap=zf.read(member(zf,"SYSTEM-MODELLER-CHAT.md")).decode("utf-8").casefold()
            for marker in [
                "instructions/chat-runtime.md",
                "inspect → validate → plan → change → validate → derive → package",
                "ett konkret systems projekt-zip är separat från detta gpt-paket",
                "mutera inte kanonisk modell före första valideringen",
            ]:
                if marker.casefold() not in bootstrap:
                    errors.append(f"Chat bootstrap missing marker: {marker}")
        except ValueError as exc:
            errors.append(str(exc))

        forbidden_prefixes=["tests/","distributions/"]
        for prefix in forbidden_prefixes:
            if any(("/"+prefix) in ("/"+n) for n in names):
                errors.append(f"Chat ZIP contains development-only content: {prefix}")

    state=normalized["contracts"]["state"]
    if state["authority"]!="canonical_yaml":
        errors.append("Chat state authority must remain canonical_yaml")
    if state["required_project_file"]!="project.yaml":
        errors.append("Chat must require project.yaml")
    if state["conversation_authoritative"] is not False:
        errors.append("conversation must not be authoritative state")
    if state["mutation_policy"]!="validate_before_and_after":
        errors.append("Chat mutation policy mismatch")

    if errors:
        print("FAILED: Chat ZIP GPT Builder 1.5 verification")
        for e in errors: print("-",e)
        return 1

    print("OK: Chat ZIP GPT Builder 1.5 verification")
    print("Canonical instruction, runtime flow, tools and project/workspace authority preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
