#!/usr/bin/env python3
"""Build the deterministic System Modeller Custom GPT distribution.

The distribution is a generated projection of canonical repository sources
according to templates/custom-gpt-distribution.yaml. No generated Custom GPT
file is a source of truth.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import tempfile
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import versioning
SPEC = ROOT / "templates" / "custom-gpt-distribution.yaml"
FIXED_DATE = (2020, 1, 1, 0, 0, 0)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt", ".java", ".ts", ".tsx", ".js", ".sql"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_spec() -> dict:
    data = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Custom GPT distribution spec must be a mapping")
    return data


def source_files_for_glob(pattern: str) -> list[Path]:
    # Path.glob handles the patterns currently declared in the A31 contract.
    return sorted(p for p in ROOT.glob(pattern) if p.is_file())


def recursive_text_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(
        p for p in path.rglob("*")
        if p.is_file()
        and p.suffix.lower() in TEXT_SUFFIXES
        and "__pycache__" not in p.parts
        and p.name != ".DS_Store"
    )


def render_source_section(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace").rstrip()
    return f"\n\n---\n\n## Källa: `{rel}`\n\n{text}\n"


def render_instructions(spec: dict, version: str) -> str:
    cfg = spec["instructions"]
    sources = cfg.get("canonical_sources", [])
    required = cfg.get("required_topics", [])
    # chat-runtime is already the compact normative runtime. Source-analysis is
    # appended because it contains operational rules that need to remain in the
    # instruction layer. The other declared sources are referenced as canonical
    # Knowledge guidance and hashed in the manifest, avoiding a huge instruction.
    primary = ROOT / "instructions" / "chat-runtime.md"
    analysis = ROOT / "instructions" / "source-analysis.md"
    body = primary.read_text(encoding="utf-8").strip()
    analysis_text = analysis.read_text(encoding="utf-8").strip()
    refs = "\n".join(f"- `{src}`" for src in sources if src not in {
        "instructions/chat-runtime.md", "instructions/source-analysis.md"
    })
    topics = ", ".join(required)
    return (
        f"# System Modeller – Custom GPT instructions\n\n"
        f"Version: **{version}**\n\n"
        f"> Genererad fil. Ändra inte denna fil manuellt; källorna anges i "
        f"`templates/custom-gpt-distribution.yaml`.\n\n"
        f"{body}\n\n"
        f"## Källanalys – operativa regler\n\n{analysis_text}\n\n"
        f"## Kanonisk Knowledge-vägledning\n\n"
        f"Fördjupade modellerings-, provenance- och originregler finns i de "
        f"genererade Knowledge-filerna och härleds från:\n\n{refs}\n\n"
        f"## Obligatorisk täckning\n\n"
        f"Buildern verifierar följande ämneskontrakt: {topics}.\n"
    )


def knowledge_sources(item: dict) -> list[Path]:
    result: list[Path] = []
    for rel in item.get("sources", []):
        p = ROOT / rel
        if not p.exists():
            raise FileNotFoundError(rel)
        result.extend(recursive_text_files(p))
    for pattern in item.get("source_globs", []):
        matches = source_files_for_glob(pattern)
        if not matches:
            raise FileNotFoundError(f"glob matched no files: {pattern}")
        result.extend(matches)
    for rel in item.get("generated_inputs", []):
        p = ROOT / rel
        if not p.exists():
            raise FileNotFoundError(rel)
        result.extend(recursive_text_files(p))
    # Stable unique paths preserving sorted order.
    return sorted(set(result), key=lambda p: p.relative_to(ROOT).as_posix())


def render_knowledge(item: dict, version: str) -> tuple[str, list[Path]]:
    paths = knowledge_sources(item)
    title = Path(item["output"]).stem.replace("-", " ").title()
    header = (
        f"# {title}\n\n"
        f"System Modeller {version}\n\n"
        f"**Syfte:** {item.get('purpose', '')}\n\n"
        f"> Genererad Knowledge-fil. Kanoniska källor finns i repositoryt; "
        f"ändra inte denna fil manuellt.\n"
    )
    content = header + "".join(render_source_section(p) for p in paths)
    return content.rstrip() + "\n", paths


def build_tree(target: Path, distribution_version: str | None = None) -> dict:
    spec = load_spec()
    version = distribution_version or (ROOT / spec.get("version_source", "VERSION")).read_text(encoding="utf-8").strip()
    out_cfg = spec["output"]
    target.mkdir(parents=True, exist_ok=True)
    knowledge_dir = target / out_cfg["knowledge_dir"]
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    instructions_text = render_instructions(spec, version)
    instructions_path = target / out_cfg["instructions"]
    instructions_path.write_text(instructions_text, encoding="utf-8")

    manifest_sources: dict[str, str] = {}
    generated: dict[str, dict] = {}
    for rel in spec["instructions"].get("canonical_sources", []):
        p = ROOT / rel
        manifest_sources[rel] = sha256_file(p)

    # A33 parity contract: hash every canonical shared model source even when
    # a source is not copied verbatim into Knowledge. This lets the validator
    # prove that Chat and Custom GPT were built against the same metamodel and
    # schemas without duplicating all schemas into Custom GPT Knowledge.
    for rel in spec.get("parity_contract", {}).get("shared_model_sources", []):
        p = ROOT / rel
        for source in recursive_text_files(p):
            source_rel = source.relative_to(ROOT).as_posix()
            manifest_sources[source_rel] = sha256_file(source)

    for item in spec.get("knowledge", []):
        text, paths = render_knowledge(item, version)
        dst = knowledge_dir / item["output"]
        dst.write_text(text, encoding="utf-8")
        for p in paths:
            rel = p.relative_to(ROOT).as_posix()
            manifest_sources[rel] = sha256_file(p)
        generated[f"knowledge/{item['output']}"] = {
            "sha256": sha256_file(dst),
            "bytes": dst.stat().st_size,
            "purpose": item.get("purpose", ""),
        }

    generated[out_cfg["instructions"]] = {
        "sha256": sha256_file(instructions_path),
        "bytes": instructions_path.stat().st_size,
    }
    manifest = {
        "schema_version": 1,
        "id": spec["id"],
        "display_name": spec["display_name"],
        "distribution_type": spec["distribution_type"],
        "version": version,
        "generated": generated,
        "source_hashes": dict(sorted(manifest_sources.items())),
        "parity_contract": spec.get("parity_contract", {}),
        "generator": "scripts/package_custom_gpt.py",
    }
    manifest_path = target / out_cfg["manifest"]
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return manifest


def deterministic_zip(source_dir: Path, out: Path) -> Path:
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(source_dir.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(source_dir).as_posix()
            info = ZipInfo(f"system-modeller-custom-gpt/{rel}", FIXED_DATE)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, p.read_bytes())
    return out


def build(out: Path, directory: Path | None = None, distribution_version: str | None = None) -> Path:
    if directory is not None:
        if directory.exists():
            for p in sorted(directory.rglob("*"), reverse=True):
                if p.is_file() or p.is_symlink():
                    p.unlink()
                elif p.is_dir():
                    p.rmdir()
        directory.mkdir(parents=True, exist_ok=True)
        build_tree(directory, distribution_version)
        return deterministic_zip(directory, out)
    with tempfile.TemporaryDirectory(prefix="system-modeller-custom-gpt-") as td:
        root = Path(td) / "system-modeller-custom-gpt"
        build_tree(root, distribution_version)
        return deterministic_zip(root, out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, help="Output ZIP path")
    ap.add_argument("--directory", type=Path, help="Also materialize the generated distribution here")
    ap.add_argument("--release-version", help="Override distribution version (X.Y.Z or vX.Y.Z)")
    ns = ap.parse_args()
    info = versioning.resolve(explicit=ns.release_version)
    out = ns.output or ROOT / "distributions" / f"system-modeller-custom-gpt-v{info.release_version}.zip"
    print(build(out, ns.directory, info.distribution_version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
