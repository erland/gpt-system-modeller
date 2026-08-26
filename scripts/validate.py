#!/usr/bin/env python3
"""Validate a System Modeller system project.

A25 validator: project/YAML/schema integrity plus lightweight semantic findings.
Exit code 0 = no errors (warnings/info may exist), 1 = validation errors, 2 = usage/internal failure.
"""
from __future__ import annotations
import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
METAMODEL = ROOT / "metamodel"
ID_RE = re.compile(r"^[A-Z][A-Z0-9]{0,9}-[0-9]{6}$")

# Type -> (schema filename, $defs key). Implementation types intentionally come later.
ELEMENT_SCHEMAS = {
    "System": ("context.schema.json", "system"),
    "ExternalSystem": ("context.schema.json", "externalSystem"),
    "Actor": ("context.schema.json", "actor"),
    "Responsibility": ("functions.schema.json", "responsibility"),
    "UseCase": ("use-cases.schema.json", "useCase"),
    "InformationObject": ("information.schema.json", "informationObject"),
    "Subsystem": ("logical-structure.schema.json", "subsystem"),
    "Component": ("logical-structure.schema.json", "component"),
    "Service": ("logical-structure.schema.json", "service"),
    "Interface": ("interfaces.schema.json", "interface"),
    "API": ("interfaces.schema.json", "api"),
    "Message": ("messaging.schema.json", "message"),
    "Event": ("messaging.schema.json", "event"),
    "DataStore": ("data-stores.schema.json", "dataStore"),
    "Scenario": ("scenarios.schema.json", "scenario"),
    "Interaction": ("interactions.schema.json", "interaction"),
    "RuntimeUnit": ("runtime.schema.json", "runtimeUnit"),
    "Environment": ("deployment.schema.json", "environment"),
    "DeploymentNode": ("deployment.schema.json", "deploymentNode"),
    "ArchitectureDecision": ("decisions.schema.json", "architectureDecision"),
    "Constraint": ("decisions.schema.json", "constraint"),
    "Source": ("provenance.schema.json", "source"),
    "SourceReference": ("provenance.schema.json", "sourceReference"),
    "Evidence": ("provenance.schema.json", "evidenceRecord"),
    "Observation": ("analysis.schema.json", "observation"),
}

# Fields whose values are model IDs. Used for cross-file reference integrity.
REFERENCE_FIELDS = {
    "primary_actor", "supporting_actors", "responsibility", "related_information", "realized_by",
    "owner", "master", "authoritative_source", "authoritative_for", "provider", "consumers",
    "exchanged_information", "producer", "use_case", "actors", "information", "components",
    "external_systems", "scenario", "participants", "element", "source_ref", "source_refs",
    "evidence", "affected_elements", "message_ref",
}

@dataclass
class Finding:
    severity: str
    code: str
    message: str
    location: str | None = None


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ValueError(f"invalid YAML: {e}") from e


def project_yaml_files(project: Path) -> list[Path]:
    files: list[Path] = []
    for folder in ("model", "interactions", "implementation", "sources"):
        base = project / folder
        if base.is_dir():
            files.extend(sorted(base.rglob("*.yaml")))
            files.extend(sorted(base.rglob("*.yml")))
    return sorted(set(files))


def schema_store() -> dict[str, dict[str, Any]]:
    store = {}
    for path in SCHEMAS.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "$id" in data:
            store[data["$id"]] = data
    return store


def validate_against(schema_file: str, def_key: str, obj: dict[str, Any], store: dict[str, Any]) -> list[str]:
    schema_doc = json.loads((SCHEMAS / schema_file).read_text(encoding="utf-8"))
    schema = {"$ref": f"{schema_doc['$id']}#/$defs/{def_key}"}
    resolver = RefResolver.from_schema(schema_doc, store=store)
    validator = Draft202012Validator(schema, resolver=resolver)
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    result=[]
    for err in errors:
        path=".".join(str(p) for p in err.path)
        result.append(f"{path + ': ' if path else ''}{err.message}")
    return result


def collect_relationship_rules() -> dict[str, set[tuple[str, str]]]:
    rules: dict[str, set[tuple[str, str]]] = {}
    for path in sorted(METAMODEL.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for name, spec in (data.get("relationship_types") or {}).items():
            pairs = spec.get("allowed_pairs") or []
            rules.setdefault(name, set()).update(tuple(p) for p in pairs if isinstance(p, list) and len(p)==2)
        # Some earlier metamodel files document relations activated in later steps as direction only.
        for name, spec in (data.get("active_relationships_from_later_steps") or {}).items():
            direction=spec.get("direction")
            if isinstance(direction,list) and len(direction)==2:
                rules.setdefault(name,set()).add(tuple(direction))
    return rules


def iter_ref_values(obj: Any, field: str | None = None) -> Iterable[tuple[str, str]]:
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k in REFERENCE_FIELDS:
                if isinstance(v,str) and ID_RE.fullmatch(v): yield k,v
                elif isinstance(v,list):
                    for x in v:
                        if isinstance(x,str) and ID_RE.fullmatch(x): yield k,x
            # nested evidence/source constructs may contain reference fields
            if isinstance(v,(dict,list)):
                yield from iter_ref_values(v,k)
    elif isinstance(obj,list):
        for v in obj: yield from iter_ref_values(v,field)


def validate(project: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not project.is_dir():
        return [Finding("ERROR","PROJECT_NOT_FOUND",f"Project directory does not exist: {project}")]

    manifest = project / "project.yaml"
    if not manifest.is_file():
        findings.append(Finding("ERROR","MANIFEST_MISSING","project.yaml is required","project.yaml"))
    else:
        try:
            m=load_yaml(manifest)
            schema=json.loads((SCHEMAS/"project.schema.json").read_text(encoding="utf-8"))
            for err in Draft202012Validator(schema).iter_errors(m):
                findings.append(Finding("ERROR","PROJECT_SCHEMA",err.message,"project.yaml"))
        except (ValueError,json.JSONDecodeError) as e:
            findings.append(Finding("ERROR","PROJECT_YAML",str(e),"project.yaml"))

    records: list[tuple[Path,str,dict[str,Any]]] = []
    for path in project_yaml_files(project):
        rel=str(path.relative_to(project))
        try: data=load_yaml(path)
        except ValueError as e:
            findings.append(Finding("ERROR","YAML_SYNTAX",str(e),rel)); continue
        if data is None: data={"elements":[],"relationships":[]}
        if not isinstance(data,dict):
            findings.append(Finding("ERROR","SHARD_SHAPE","YAML shard must be a mapping",rel)); continue
        for section in ("elements","relationships"):
            values=data.get(section,[])
            if not isinstance(values,list):
                findings.append(Finding("ERROR","SHARD_SHAPE",f"{section} must be a list",rel)); continue
            for idx,obj in enumerate(values):
                if not isinstance(obj,dict):
                    findings.append(Finding("ERROR","RECORD_SHAPE",f"{section}[{idx}] must be a mapping",rel)); continue
                records.append((path,section,obj))

    ids: dict[str,tuple[Path,str,dict[str,Any]]] = {}
    for path,section,obj in records:
        oid=obj.get("id"); loc=f"{path.relative_to(project)}:{section}:{oid or '?'}"
        if not isinstance(oid,str) or not ID_RE.fullmatch(oid):
            findings.append(Finding("ERROR","INVALID_ID",f"Invalid or missing stable ID: {oid!r}",loc)); continue
        if oid in ids:
            findings.append(Finding("ERROR","DUPLICATE_ID",f"ID {oid} occurs more than once",loc))
        else: ids[oid]=(path,section,obj)

    store=schema_store()
    for path,section,obj in records:
        loc=f"{path.relative_to(project)}:{section}:{obj.get('id','?')}"
        if section=="elements":
            typ=obj.get("type")
            if typ is None:
                oid=obj.get("id", "")
                if isinstance(oid, str):
                    if oid.startswith("SRC-"): typ="Source"
                    elif oid.startswith("REF-"): typ="SourceReference"
                    elif oid.startswith("EVD-"): typ="Evidence"
            entry=ELEMENT_SCHEMAS.get(typ)
            if not entry:
                findings.append(Finding("ERROR","UNKNOWN_ELEMENT_TYPE",f"Unknown/unsupported MVP element type: {typ!r}",loc)); continue
            for msg in validate_against(*entry,obj,store):
                findings.append(Finding("ERROR","ELEMENT_SCHEMA",msg,loc))
        else:
            common=json.loads((SCHEMAS/"common.schema.json").read_text(encoding="utf-8"))
            schema={"$ref":f"{common['$id']}#/$defs/relationship"}
            resolver=RefResolver.from_schema(common,store=store)
            for err in Draft202012Validator(schema,resolver=resolver).iter_errors(obj):
                findings.append(Finding("ERROR","RELATIONSHIP_SCHEMA",err.message,loc))

    # Cross-file reference integrity for explicit relationships and known ref fields.
    for path,section,obj in records:
        loc=f"{path.relative_to(project)}:{section}:{obj.get('id','?')}"
        if section=="relationships":
            for fld in ("source","target"):
                ref=obj.get(fld)
                if isinstance(ref,str) and ref not in ids:
                    findings.append(Finding("ERROR","BROKEN_REFERENCE",f"{fld} references unknown ID {ref}",loc))
        for fld,ref in iter_ref_values(obj):
            if ref not in ids:
                findings.append(Finding("ERROR","BROKEN_REFERENCE",f"{fld} references unknown ID {ref}",loc))

    # Relationship type and source/target type compatibility.
    rel_rules=collect_relationship_rules()
    for path,section,obj in records:
        if section!="relationships": continue
        loc=f"{path.relative_to(project)}:relationships:{obj.get('id','?')}"
        rtype=obj.get("type")
        if rtype not in rel_rules:
            findings.append(Finding("ERROR","UNKNOWN_RELATIONSHIP_TYPE",f"Unknown relationship type {rtype!r}",loc)); continue
        s=ids.get(obj.get("source")); t=ids.get(obj.get("target"))
        if not s or not t: continue
        pair=(s[2].get("type"),t[2].get("type"))
        if rel_rules[rtype] and pair not in rel_rules[rtype]:
            findings.append(Finding("ERROR","INVALID_RELATIONSHIP_PAIR",f"{rtype} does not allow {pair[0]} -> {pair[1]}",loc))

    elements={oid:rec[2] for oid,rec in ids.items() if rec[1]=="elements"}
    relationships=[obj for _,section,obj in records if section=="relationships"]

    # A25 semantic MVP checks (warnings unless structurally invalid).
    for oid,e in elements.items():
        typ=e.get("type")
        loc=f"element:{oid}"
        if typ=="UseCase":
            if not e.get("primary_actor"):
                findings.append(Finding("ERROR","UC_PRIMARY_ACTOR","UseCase requires primary_actor",loc))
            if not e.get("responsibility"):
                findings.append(Finding("ERROR","UC_RESPONSIBILITY","UseCase requires responsibility",loc))
        elif typ=="Component":
            connected=any((r.get("type") in {"realized_by","realizes"}) and (r.get("source")==oid or r.get("target")==oid) for r in relationships)
            referenced=any(oid in (u.get("realized_by") or []) for u in elements.values() if u.get("type")=="UseCase")
            if not connected and not referenced:
                findings.append(Finding("WARNING","COMPONENT_WITHOUT_RESPONSIBILITY","Component has no modeled Responsibility/UseCase realization",loc))
        elif typ in {"API","Interface"} and not e.get("provider"):
            findings.append(Finding("ERROR","INTERFACE_WITHOUT_PROVIDER",f"{typ} requires provider",loc))
        elif typ=="RuntimeUnit":
            deployed=any(r.get("type")=="deployed_on" and r.get("source")==oid for r in relationships)
            if not deployed:
                findings.append(Finding("WARNING","RUNTIME_NOT_DEPLOYED","RuntimeUnit has no deployed_on relation",loc))
        elif typ=="InformationObject":
            used=False
            info_rel_types={"creates_information","reads_information","updates_information","deletes_information","owns_information","masters_information","stores_information","exchanges_information","involves_information"}
            if any(r.get("type") in info_rel_types and (r.get("source")==oid or r.get("target")==oid) for r in relationships): used=True
            if any(oid in list(iter_values) for x in elements.values() for iter_values in [x.get("related_information") or [], x.get("exchanged_information") or [], x.get("information") or []] if isinstance(iter_values,list)): used=True
            if not used:
                findings.append(Finding("WARNING","INFORMATION_UNUSED","InformationObject has no modeled usage",loc))

    if not any(f.severity=="ERROR" for f in findings):
        findings.append(Finding("INFO","VALIDATION_OK","Project passed A25 structural and semantic validation"))
    return findings


def main() -> int:
    ap=argparse.ArgumentParser(description="Validate a System Modeller project")
    ap.add_argument("project",type=Path)
    ap.add_argument("--format",choices=("text","json"),default="text")
    args=ap.parse_args()
    try: findings=validate(args.project.resolve())
    except Exception as e:
        print(f"ERROR VALIDATOR_INTERNAL: {e}")
        return 2
    if args.format=="json":
        print(json.dumps([asdict(f) for f in findings],ensure_ascii=False,indent=2))
    else:
        order={"ERROR":0,"WARNING":1,"INFO":2}
        for f in sorted(findings,key=lambda x:(order.get(x.severity,9),x.code,x.location or "")):
            where=f" [{f.location}]" if f.location else ""
            print(f"{f.severity} {f.code}{where}: {f.message}")
        counts={s:sum(f.severity==s for f in findings) for s in ("ERROR","WARNING","INFO")}
        print(f"Summary: {counts['ERROR']} error(s), {counts['WARNING']} warning(s), {counts['INFO']} info finding(s)")
    return 1 if any(f.severity=="ERROR" for f in findings) else 0

if __name__=="__main__":
    raise SystemExit(main())
