#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import versioning

SPEC = ROOT / "templates" / "opencode-distribution.yaml"
FIXED_DATE = (2020, 1, 1, 0, 0, 0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_spec() -> dict:
    data = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("OpenCode distribution spec must be a mapping")
    return data


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def wrapper_common() -> str:
    return """import { tool } from "@opencode-ai/plugin"
import path from "path"

async function runScript(scriptName: string, argv: string[], context: any) {
  const script = path.join(context.worktree, ".opencode/runtime/scripts", scriptName)
  const proc = Bun.spawn(["python3", script, ...argv], {
    cwd: context.worktree,
    stdout: "pipe",
    stderr: "pipe",
  })
  const stdout = await new Response(proc.stdout).text()
  const stderr = await new Response(proc.stderr).text()
  const code = await proc.exited
  if (code !== 0) throw new Error(stderr.trim() || "System Modeller tool failed with exit " + code)
  return stdout.trim()
}

"""


def tool_wrapper(tool_id: str) -> str:
    common = wrapper_common()
    bodies = {
        "system_context": """export default tool({
  description: "Inspect a System Modeller project and return compact canonical context.",
  args: {
    projectRoot: tool.schema.string().default(".").describe("Project root relative to the OpenCode worktree"),
    focus: tool.schema.string().optional().describe("Optional focus text"),
  },
  async execute(args, context) {
    const argv = [args.projectRoot, "--format", "yaml"]
    if (args.focus) argv.push("--focus", args.focus)
    return runScript("context.py", argv, context)
  },
})
""",
        "system_validate": """export default tool({
  description: "Validate a System Modeller project's canonical YAML.",
  args: {
    projectRoot: tool.schema.string().default(".").describe("Project root relative to the OpenCode worktree"),
  },
  async execute(args, context) {
    return runScript("validate.py", [args.projectRoot], context)
  },
})
""",
        "system_model": """export default tool({
  description: "Query or mutate canonical System Modeller YAML. Mutating calls require approval.",
  args: {
    projectRoot: tool.schema.string().default("."),
    command: tool.schema.enum(["find", "list", "add", "update", "delete", "add-relation", "delete-relation"]),
    id: tool.schema.string().optional(),
    type: tool.schema.string().optional(),
    json: tool.schema.string().optional().describe("JSON payload for add, update or add-relation"),
    force: tool.schema.boolean().optional(),
  },
  async execute(args, context) {
    const argv = [args.projectRoot, args.command]
    if (["find", "update", "delete", "delete-relation"].includes(args.command)) {
      if (!args.id) throw new Error("id is required for this command")
      argv.push(args.id)
    }
    if (args.command === "list" && args.type) argv.push("--type", args.type)
    if (["add", "update", "add-relation"].includes(args.command)) {
      if (!args.json) throw new Error("json is required for this command")
      argv.push("--json", args.json)
    }
    if (args.command === "delete" && args.force) argv.push("--force")
    return runScript("model.py", argv, context)
  },
})
""",
        "system_view": """export default tool({
  description: "Derive a System Modeller view from canonical YAML.",
  args: {
    projectRoot: tool.schema.string().default("."),
    type: tool.schema.enum(["system_context", "functional_overview", "use_case_overview", "information_overview", "functional_information", "logical_component", "use_case_realization", "integration", "sequence", "deployment"]),
    format: tool.schema.enum(["yaml", "json", "mermaid", "plantuml"]).default("yaml"),
  },
  async execute(args, context) {
    return runScript("view.py", [args.projectRoot, "--type", args.type, "--format", args.format], context)
  },
})
""",
        "system_report": """export default tool({
  description: "Generate the standard architecture description from canonical YAML.",
  args: {
    projectRoot: tool.schema.string().default("."),
    noDiagrams: tool.schema.boolean().optional(),
  },
  async execute(args, context) {
    const argv = [args.projectRoot]
    if (args.noDiagrams) argv.push("--no-diagrams")
    return runScript("report.py", argv, context)
  },
})
""",
        "system_package": """export default tool({
  description: "Package a complete System Modeller project ZIP.",
  args: {
    projectRoot: tool.schema.string().default("."),
    output: tool.schema.string().describe("Output ZIP path relative to the OpenCode worktree"),
  },
  async execute(args, context) {
    return runScript("package_project.py", [args.projectRoot, "--output", args.output], context)
  },
})
""",
        "system_analyze": """export default tool({
  description: "Inventory source material for System Modeller source analysis.",
  args: {
    sourcePath: tool.schema.string().describe("Source path relative to the OpenCode worktree"),
  },
  async execute(args, context) {
    return runScript("analyze.py", ["inventory", args.sourcePath], context)
  },
})
""",
    }
    if tool_id not in bodies:
        raise ValueError(f"Unknown tool id: {tool_id}")
    return common + bodies[tool_id]


def build_tree(target: Path, distribution_version: str | None = None) -> dict:
    spec = load_spec()
    version = distribution_version or (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    target.mkdir(parents=True, exist_ok=True)

    canonical = (ROOT / spec["canonical_instruction"]).read_text(encoding="utf-8").strip()
    agents = (
        "# System Modeller - OpenCode workspace\n\n"
        f"Version: **{version}**\n\n"
        "This file is generated from the canonical System Modeller runtime contract. "
        "The canonical model in the target system project remains the source of truth.\n\n"
        "Use the project-local system_* custom tools when available. Pass projectRoot explicitly "
        "when the target System Modeller project is not the OpenCode worktree root. "
        "Mutating model operations require approval through opencode.json.\n\n"
        + canonical
        + "\n"
    )
    (target / spec["output"]["instructions"]).write_text(agents, encoding="utf-8")

    runtime_scripts = target / spec["output"]["runtime_scripts_dir"]
    script_names = spec["runtime_scripts"]["declared_tools"] + spec["runtime_scripts"]["support"]
    for name in script_names:
        copy_file(ROOT / "scripts" / name, runtime_scripts / name)

    tools_dir = target / spec["output"]["tools_dir"]
    tools_dir.mkdir(parents=True, exist_ok=True)
    for item in spec["tools"]:
        (tools_dir / f"{item['id']}.ts").write_text(tool_wrapper(item["id"]), encoding="utf-8")

    knowledge = target / spec["output"]["knowledge_dir"]
    for root_name in spec["knowledge_roots"]:
        source_root = ROOT / root_name
        for src in sorted(source_root.rglob("*")):
            if src.is_file() and "__pycache__" not in src.parts:
                copy_file(src, knowledge / root_name / src.relative_to(source_root))
    for rel in spec["knowledge_files"]:
        copy_file(ROOT / rel, knowledge / rel)

    contract = {
        "schema_version": "1.0",
        "runtime": "opencode",
        "version": version,
        "canonical_instruction": "AGENTS.md",
        "workspace_state": "ready",
        "target_project": {"project_root_argument": "projectRoot", "default": "."},
        "tools": [
            {
                "id": item["id"],
                "script": item["script"],
                "mutates_workspace": bool(item["mutates_workspace"]),
                "permission": "ask" if item["mutates_workspace"] else "allow",
            }
            for item in spec["tools"]
        ],
        "runtime_sequence": ["INSPECT", "VALIDATE", "PLAN", "CHANGE", "VALIDATE", "DERIVE", "PACKAGE"],
    }
    contract_path = target / spec["output"]["runtime_contract"]
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    permissions = [
        {"action": "shell", "resource": "*", "effect": "ask"},
        {"action": "edit", "resource": "*", "effect": "ask"},
    ]
    for item in spec["tools"]:
        permissions.append({
            "action": item["id"],
            "resource": "*",
            "effect": "ask" if item["mutates_workspace"] else "allow",
        })
    config = {"$schema": "https://opencode.ai/config.json", "permissions": permissions}
    (target / spec["output"]["config"]).write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    (target / "README.md").write_text(
        "# System Modeller - OpenCode\n\n"
        "Open this directory as an OpenCode workspace. The target System Modeller project may be "
        "the workspace root or a subdirectory supplied through projectRoot.\n",
        encoding="utf-8",
    )
    (target / "VERSION").write_text(version + "\n", encoding="utf-8")

    source_hashes = {spec["canonical_instruction"]: digest(ROOT / spec["canonical_instruction"])}
    for rel in spec["knowledge_files"]:
        source_hashes[rel] = digest(ROOT / rel)
    for root_name in spec["knowledge_roots"]:
        for src in sorted((ROOT / root_name).rglob("*")):
            if src.is_file():
                source_hashes[src.relative_to(ROOT).as_posix()] = digest(src)
    for name in script_names:
        source_hashes[f"scripts/{name}"] = digest(ROOT / "scripts" / name)

    generated = {}
    for path in sorted(target.rglob("*")):
        if path.is_file():
            rel = path.relative_to(target).as_posix()
            generated[rel] = {"sha256": digest(path), "bytes": path.stat().st_size}

    manifest = {
        "schema_version": 1,
        "id": spec["id"],
        "distribution_type": "opencode_workspace",
        "version": version,
        "generator": "scripts/package_opencode.py",
        "source_hashes": dict(sorted(source_hashes.items())),
        "generated": generated,
    }
    (target / spec["output"]["manifest"]).write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    return manifest


def deterministic_zip(source: Path, out: Path) -> Path:
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(source).as_posix()
            info = ZipInfo(f"system-modeller-opencode/{rel}", FIXED_DATE)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    return out


def build(out: Path, directory: Path | None = None, distribution_version: str | None = None) -> Path:
    if directory is not None:
        if directory.exists():
            for path in sorted(directory.rglob("*"), reverse=True):
                if path.is_file() or path.is_symlink():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
        directory.mkdir(parents=True, exist_ok=True)
        build_tree(directory, distribution_version)
        return deterministic_zip(directory, out)

    with tempfile.TemporaryDirectory(prefix="system-modeller-opencode-") as td:
        root = Path(td) / "system-modeller-opencode"
        build_tree(root, distribution_version)
        return deterministic_zip(root, out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--directory", type=Path)
    ap.add_argument("--release-version")
    ns = ap.parse_args()
    info = versioning.resolve(explicit=ns.release_version)
    out = ns.output or ROOT / "distributions" / f"system-modeller-opencode-v{info.release_version}.zip"
    print(build(out, ns.directory, info.distribution_version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
