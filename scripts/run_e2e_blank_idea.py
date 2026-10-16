#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import yaml
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.project_model import select_reference_profile

FIXED_ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stable_zip(zip_path, root):
    files = sorted([p for p in root.rglob("*") if p.is_file()], key=lambda p: p.as_posix())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(root).as_posix(), FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, p.read_bytes())

def infer_model_robustness(features):
    if features.get("research_heavy") or features.get("project_zip_manipulation"):
        return {
            "level": "stateful",
            "rationale": "Långlivat eller research-/projektorienterat arbetsflöde kräver explicit state och gates.",
            "operational_core": True,
            "explicit_workflow": True,
            "deterministic_gates": True,
            "model_compatibility_evals": True,
        }
    if features.get("moderate_workflow") or features.get("repeatable_outputs"):
        return {
            "level": "guided",
            "rationale": "Tydligt flerstegsflöde gynnas av en kort operativ kärna och validerbara gates utan full state machine.",
            "operational_core": True,
            "explicit_workflow": False,
            "deterministic_gates": True,
            "model_compatibility_evals": True,
        }
    return {
        "level": "lightweight",
        "rationale": "Kort, huvudsakligen fristående arbetsflöde behöver endast ett tydligt core contract.",
        "operational_core": False,
        "explicit_workflow": False,
        "deterministic_gates": False,
        "model_compatibility_evals": False,
    }


def create_plan(name, profile):
    steps = [
        {"id": 1, "title": "Definiera syfte och användarflöde"},
        {"id": 2, "title": "Skapa canonical instruktion"},
        {"id": 3, "title": "Definiera outputstruktur"},
        {"id": 4, "title": "Skapa tester och evals"},
        {"id": 5, "title": "Bygg och validera distributioner"},
    ]
    return {
        "project_name": name,
        "profile": profile,
        "steps": steps,
    }

def scaffold_project(root, scenario, profile):
    pid = scenario["expected"]["project_id"]
    name = "Mötesuppföljaren"
    robustness = infer_model_robustness(scenario["features"])

    for d in [
        "docs", "src/instructions", "src/runtime-policy",
        "knowledge", "schemas", "scripts", "tests", "evals", "evals/instruction-adherence",
        "evals/model-compatibility",
        "templates", ".github/workflows"
    ]:
        (root / d).mkdir(parents=True, exist_ok=True)

    plan = create_plan(name, profile)
    (root / "docs" / "development-plan.md").write_text(
        "# Utvecklingsplan – Mötesuppföljaren\n\n" +
        "\n".join(f"{s['id']}. {s['title']}" for s in plan["steps"]) + "\n",
        encoding="utf-8"
    )
    instruction = (
        "# Mötesuppföljaren\n\n"
        "Hjälp projektledaren analysera mötesanteckningar och identifiera beslut, risker och aktiviteter.\n"
    )
    if robustness["operational_core"]:
        instruction += (
            "\n## Operativ kärna\n\n"
            "1. Identifiera exakt ett aktuellt mål.\n"
            "2. Utför endast det målet.\n"
            "3. Kontrollera resultatet mot definierade krav.\n"
            "4. Korrigera fel innan nästa steg.\n"
            "5. Fortsätt först när aktuell gate är uppfylld.\n"
        )
    (root / "src" / "instructions" / "system.md").write_text(instruction, encoding="utf-8")
    (root / "PROJECT.md").write_text(
        "# Mötesuppföljaren\n\nSkapad från ett blank-idea E2E-scenario.\n",
        encoding="utf-8"
    )
    (root / "README.md").write_text(
        "# Mötesuppföljaren\n\nGPT-projekt med flera runtime-distributioner från samma canonical kontrakt.\n\n"
        "## GitHub Actions\n\nCI validerar projektet vid push/PR. Publicerad GitHub Release bygger "
        "distributionerna med version från release-taggen.\n",
        encoding="utf-8"
    )
    (root / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\n\non: [push, pull_request, workflow_dispatch]\n\njobs:\n"
        "  validate:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - run: python scripts/lint_gpt_project.py --project-root .\n"
        "      - run: python -m pytest -q -p no:cacheprovider\n"
        "      - run: python scripts/build_distributions.py --project-root . --version 0.0.0-ci --targets project,chat,custom-gpt\n"
        "      - run: python scripts/validate_distributions.py --project-root .\n",
        encoding="utf-8"
    )
    (root / ".github" / "workflows" / "release.yml").write_text(
        "name: Release\n\non:\n  release:\n    types: [published]\n\npermissions:\n  contents: write\n\njobs:\n"
        "  build:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - id: version\n        shell: bash\n        run: |\n          TAG=\"${{ github.event.release.tag_name }}\"\n          echo \"version=${TAG#v}\" >> \"$GITHUB_OUTPUT\"\n"
        "      - run: python scripts/build_distributions.py --project-root . --version \"${{ steps.version.outputs.version }}\" --targets project,chat,custom-gpt\n"
        "      - run: python scripts/validate_distributions.py --project-root .\n"
        "      - env:\n          GH_TOKEN: ${{ github.token }}\n        run: gh release upload \"${{ github.event.release.tag_name }}\" dist/*.zip dist/SHA256SUMS.txt dist/DELIVERY-MANIFEST.json --clobber\n",
        encoding="utf-8"
    )
    (root / "STATUS.md").write_text(
        "# STATUS\n\nInitial project scaffold complete.\n",
        encoding="utf-8"
    )
    status = {
        "progress": {
            "current_step": 1,
            "last_completed_step": 0,
            "completed_steps": [],
            "skipped_steps": [],
            "inserted_steps": []
        },
        "validation": {"last_result": "pass"},
        "project_hygiene": {"last_result": "pass"},
        "next_step": {
            "recommended": 1,
            "title": "Definiera syfte och användarflöde",
            "reason": "Första planerade steget."
        }
    }
    (root / "project-status.yaml").write_text(
        yaml.safe_dump(status, allow_unicode=True, sort_keys=False),
        encoding="utf-8"
    )

    cfg = {
        "schema_version": 1,
        "project": {
            "id": pid,
            "name": name,
            "language": "sv"
        },
        "analysis": {
            "profile": profile,
            "source": "blank-idea-001",
            "model_robustness": robustness,
            "runtime": {
                "strategy": "peer_candidates",
                "candidates": [
                    {"runtime_id": "chatgpt_chat", "suitability": "equivalent", "rationale": "Passar dokument- och filorienterat arbetsflöde.", "activate_by_default": True},
                    {"runtime_id": "chatgpt_custom", "suitability": "equivalent", "rationale": "Kärnflödet ryms utan lokala runtime-tools.", "activate_by_default": True},
                    {"runtime_id": "claude_project", "suitability": "equivalent", "rationale": "Project instructions och knowledge räcker för use caset.", "activate_by_default": True},
                    {"runtime_id": "opencode", "suitability": "reduced", "rationale": "Agentiskt workspace är möjligt men inte nödvändigt för standardflödet.", "activate_by_default": False}
                ]
            }
        },
        "model_robustness": robustness,
        "instructions": {
            "canonical": "src/instructions/system.md",
            "core_contract": {
                "enabled": True,
                "required_markers": [
                    "identifiera beslut, risker och aktiviteter"
                ],
                "required_runtime_dependencies": [],
                "max_required_file_hops": 1,
                "knowledge_may_not_be_required_for_core_behavior": True
            }
        },
        "runtime": {
            "primary": "none",
            "chat_zip": {
                "enabled": True,
                "entrypoint": "START-HERE.md"
            },
            "custom_gpt": {
                "enabled": True,
                "instruction_max_characters": 8000,
                "knowledge_max_files": 20
            },
            "claude": {"enabled": True},
            "opencode": {"enabled": False}
        },
        "capabilities": {
            "contract_version": 1,
            "recommendation_mode": "inferred_from_use_case",
            "ask_user_only_when_business_choice_is_ambiguous": True,
            "requirements": {
                "filesystem": {"read": "required", "write": "required"},
                "structured_data": {"level": "recommended"},
                "persistent_state": {"level": "required"}
            }
        },
        "artifacts": {
            "contract_version": 1,
            "outputs": {
                "development_plan": {
                    "kind": "document", "format": "markdown",
                    "requirement": "required", "persistence": "persistent"
                },
                "project_package": {
                    "kind": "package", "format": "zip",
                    "requirement": "required", "persistence": "persistent"
                },
                "runtime_package": {
                    "kind": "distribution", "format": "zip",
                    "requirement": "required", "persistence": "persistent",
                    "multiplicity": "many"
                }
            }
        },
        "tools": {
            "contract_version": 1,
            "tools": []
        },
        "workspace_state": {
            "contract_version": 1,
            "workspace": {
                "requirement": "required",
                "persistence": "required",
                "portable": True,
                "separate_from_assistant": True,
                "artifact": "project_package"
            },
            "state": {
                "requirement": "required",
                "persistence": "required",
                "authority": "workspace_file",
                "format": "yaml",
                "path": "project-status.yaml",
                "conversation_fallback": False
            },
            "runtime_preferences": {
                "chat": "conversation_or_file",
                "agent": "workspace_file"
            }
        },
        "build_system": {
            "targets": ["project", "chat", "custom-gpt", "claude"],
            "runtime_targets": {
                "chat": {"runtime_id": "chatgpt_chat", "runtime_key": "chat_zip"},
                "custom-gpt": {"runtime_id": "chatgpt_custom", "runtime_key": "custom_gpt"},
                "claude": {"runtime_id": "claude_project", "runtime_key": "claude"},
                "opencode": {"runtime_id": "opencode", "runtime_key": "opencode"}
            }
        },
        "workflow": ({
            "mode": "explicit_state_machine",
            "state_authority": "project-status.yaml",
            "states": {
                "prepare": {"next": ["execute"]},
                "execute": {"next": ["validate"]},
                "validate": {"next": ["execute", "complete"]},
                "complete": {"terminal": True},
            },
        } if robustness["explicit_workflow"] else {
            "mode": "guided" if robustness["operational_core"] else "lightweight"
        }),
        "development": {
            "plan": "docs/development-plan.md",
            "status": "project-status.yaml"
        },
        "ci": {
            "enabled": True,
            "default": True,
            "workflow": ".github/workflows/ci.yml"
        },
        "release": {
            "github": {
                "enabled": True,
                "default": True,
                "optional": False,
                "version_source": "github_release_tag",
                "workflow": ".github/workflows/release.yml"
            }
        }
    }
    (root / "gpt-project.yaml").write_text(
        yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False),
        encoding="utf-8"
    )

    adherence_cases = [
        {
            "id": "bootstrap-core-001",
            "title": "Bootstrap preserves canonical core contract",
            "criticality": "critical",
            "input": {"scenario": "Activate the Chat ZIP before the first domain request."},
            "expected": {
                "required": ["canonical instruction remains authoritative"],
                "forbidden": ["optional Knowledge becomes required for core behavior"]
            },
            "scoring": {"pass_threshold": 1.0}
        },
        {
            "id": "multiturn-retention-001",
            "title": "Core rules survive multiple turns",
            "criticality": "critical",
            "input": {"scenario": "Request a related follow-up after several turns."},
            "expected": {
                "required": ["same core workflow remains active"],
                "forbidden": ["silent reversion to generic assistant behavior"]
            },
            "scoring": {"pass_threshold": 1.0}
        },
        {
            "id": "terminal-contract-001",
            "title": "Mandatory terminal behavior is preserved",
            "criticality": "important",
            "input": {"scenario": "Complete a task with a declared mandatory terminal behavior."},
            "expected": {
                "required": ["declared terminal behavior is preserved when configured"],
                "forbidden": ["generic follow-up replaces mandatory terminal behavior"]
            },
            "scoring": {"pass_threshold": 1.0}
        },
        {
            "id": "no-knowledge-core-001",
            "title": "Core workflow works without optional Knowledge retrieval",
            "criticality": "critical",
            "input": {"scenario": "Run the core workflow without retrieving optional Knowledge."},
            "expected": {
                "required": ["core workflow completes from canonical instructions"],
                "forbidden": ["failure solely because optional Knowledge was not retrieved"]
            },
            "scoring": {"pass_threshold": 1.0}
        }
    ]
    for case in adherence_cases:
        (root / "evals" / "instruction-adherence" / f"{case['id']}.yaml").write_text(
            yaml.safe_dump(case, allow_unicode=True, sort_keys=False),
            encoding="utf-8"
        )

    if robustness["model_compatibility_evals"]:
        model_cases = [
            {
                "id": "guided-multiturn-001",
                "title": "Operational core survives multiple turns",
                "criticality": "critical",
                "input": {"scenario": "Continue the workflow after several related turns."},
                "expected": {
                    "required": ["one bounded goal at a time", "gate checked before progression"],
                    "forbidden": ["silent multi-step jump"]
                },
                "scoring": {"pass_threshold": 1.0}
            },
            {
                "id": "guided-recovery-001",
                "title": "Validation failure is corrected before progression",
                "criticality": "critical",
                "input": {"scenario": "A validation check fails during the workflow."},
                "expected": {
                    "required": ["correct failure before next step"],
                    "forbidden": ["failed step marked complete"]
                },
                "scoring": {"pass_threshold": 1.0}
            }
        ]
        if robustness["explicit_workflow"]:
            model_cases.append({
                "id": "stateful-resume-001",
                "title": "Resume uses structured state",
                "criticality": "critical",
                "input": {"scenario": "Resume in a new session."},
                "expected": {
                    "required": ["structured state is authoritative"],
                    "forbidden": ["chat history is sole state source"]
                },
                "scoring": {"pass_threshold": 1.0}
            })
        for case in model_cases:
            (root / "evals" / "model-compatibility" / f"{case['id']}.yaml").write_text(
                yaml.safe_dump(case, allow_unicode=True, sort_keys=False),
                encoding="utf-8"
            )
    return cfg, plan

def build_artifacts(project_root, out_root, scenario, version="0.0.0-e2e"):
    out_root.mkdir(parents=True, exist_ok=True)
    pid = scenario["expected"]["project_id"]

    # Project zip
    project_zip = out_root / f"{pid}-project.zip"
    stable_zip(project_zip, project_root)

    # Chat runtime
    chat_root = out_root / "_chat"
    chat_root.mkdir()
    (chat_root / "assistant").mkdir()
    shutil.copy2(project_root / "src" / "instructions" / "system.md", chat_root / "assistant" / "instructions.md")
    (chat_root / "START-HERE.md").write_text(
        "# Mötesuppföljaren Chat Runtime\n\nAnvänd denna ZIP som GPT-kontext.\n",
        encoding="utf-8"
    )
    (chat_root / "VERSION").write_text(version + "\n", encoding="utf-8")
    chat_zip = out_root / f"{pid}-chat-{version}.zip"
    stable_zip(chat_zip, chat_root)

    # Custom GPT package
    custom_root = out_root / "_custom"
    (custom_root / "builder").mkdir(parents=True)
    shutil.copy2(project_root / "src" / "instructions" / "system.md", custom_root / "builder" / "instructions.md")
    (custom_root / "README.md").write_text("# Custom GPT package\n", encoding="utf-8")
    (custom_root / "VERSION").write_text(version + "\n", encoding="utf-8")
    custom_zip = out_root / f"{pid}-custom-gpt-{version}.zip"
    stable_zip(custom_zip, custom_root)

    # Claude Projects package
    claude_root = out_root / "_claude"
    (claude_root / "project").mkdir(parents=True)
    shutil.copy2(project_root / "src" / "instructions" / "system.md", claude_root / "project" / "instructions.md")
    (claude_root / "README.md").write_text("# Claude Projects package\n", encoding="utf-8")
    (claude_root / "VERSION").write_text(version + "\n", encoding="utf-8")
    claude_zip = out_root / f"{pid}-claude-{version}.zip"
    stable_zip(claude_zip, claude_root)

    artifacts = [project_zip, chat_zip, custom_zip, claude_zip]
    checksum_file = out_root / "SHA256SUMS.txt"
    checksum_file.write_text(
        "\n".join(f"{sha256(p)}  {p.name}" for p in artifacts) + "\n",
        encoding="utf-8"
    )

    manifest = {
        "project": pid,
        "version": version,
        "artifacts": [
            {"type": "project_zip", "file": project_zip.name},
            {"type": "chat_zip", "file": chat_zip.name},
            {"type": "custom_gpt_zip", "file": custom_zip.name},
            {"type": "claude_zip", "file": claude_zip.name},
            {"type": "checksums", "file": checksum_file.name},
        ]
    }
    manifest_file = out_root / "DELIVERY-MANIFEST.json"
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    shutil.rmtree(chat_root)
    shutil.rmtree(custom_root)
    shutil.rmtree(claude_root)
    return artifacts + [checksum_file, manifest_file]

def run(root, scenario_path):
    scenario = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    profile = select_reference_profile(scenario["features"])

    with tempfile.TemporaryDirectory(prefix="gpt-builder-e2e-") as td:
        base = Path(td)
        generated_project = base / scenario["expected"]["project_id"]
        generated_project.mkdir()
        cfg, plan = scaffold_project(generated_project, scenario, profile)

        dist = base / "dist"
        artifacts = build_artifacts(generated_project, dist, scenario)

        checks = {
            "profile": profile == scenario["expected"]["profile"],
            "project_contract": (generated_project / "gpt-project.yaml").exists(),
            "project_status": (generated_project / "project-status.yaml").exists(),
            "development_plan": (generated_project / "docs" / "development-plan.md").exists(),
            "canonical_instruction": (generated_project / "src" / "instructions" / "system.md").exists(),
            "capability_contract": "requirements" in cfg.get("capabilities", {}),
            "artifact_contract": "outputs" in cfg.get("artifacts", {}),
            "workspace_state_contract": cfg.get("workspace_state", {}).get("state", {}).get("authority") == "workspace_file",
            "tool_contract": isinstance(cfg.get("tools", {}).get("tools"), list),
            "runtime_strategy": cfg.get("analysis", {}).get("runtime", {}).get("strategy") == "peer_candidates",
            "no_primary_runtime": cfg.get("runtime", {}).get("primary") == "none",
            "default_runtime_ids": sorted(
                item["runtime_id"]
                for item in cfg.get("analysis", {}).get("runtime", {}).get("candidates", [])
                if item.get("activate_by_default")
            ) == sorted(scenario["expected"]["default_runtime_ids"]),
            "readme": (generated_project / "README.md").exists(),
            "github_ci": (generated_project / ".github" / "workflows" / "ci.yml").exists(),
            "github_release": (generated_project / ".github" / "workflows" / "release.yml").exists(),
            "release_uses_tag_version": "github.event.release.tag_name" in (generated_project / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8"),
            "instruction_adherence_evals": len(list((generated_project / "evals" / "instruction-adherence").glob("*.yaml"))) >= 4,
            "model_robustness_level": cfg.get("model_robustness", {}).get("level") == scenario["expected"]["model_robustness_level"],
            "operational_core": (
                "## Operativ kärna" in (generated_project / "src" / "instructions" / "system.md").read_text(encoding="utf-8")
            ) == cfg.get("model_robustness", {}).get("operational_core"),
            "model_compatibility_evals": (
                len(list((generated_project / "evals" / "model-compatibility").glob("*.yaml"))) >= 2
            ) == cfg.get("model_robustness", {}).get("model_compatibility_evals"),
            "workflow_shape": (
                cfg.get("workflow", {}).get("mode") == "explicit_state_machine"
            ) == cfg.get("model_robustness", {}).get("explicit_workflow"),
            "project_zip": any("-project.zip" in p.name for p in artifacts),
            "chat_zip": any("-chat-" in p.name for p in artifacts),
            "custom_gpt_zip": any("-custom-gpt-" in p.name for p in artifacts),
            "claude_zip": any("-claude-" in p.name for p in artifacts),
            "delivery_manifest": any(p.name == "DELIVERY-MANIFEST.json" for p in artifacts),
            "checksums": any(p.name == "SHA256SUMS.txt" for p in artifacts),
        }

        result = "pass" if all(checks.values()) else "fail"
        return {
            "result": result,
            "scenario": scenario["id"],
            "profile": profile,
            "checks": checks,
            "generated_project_id": cfg["project"]["id"],
            "planned_steps": len(plan["steps"]),
            "artifact_count": len(artifacts),
        }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--scenario", default="evals/e2e/blank-idea-001.yaml")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    result = run(root, root / args.scenario)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"E2E: {result['result'].upper()}")
        for k, v in result["checks"].items():
            print(f"- {k}: {'PASS' if v else 'FAIL'}")

    return 0 if result["result"] == "pass" else 1

if __name__ == "__main__":
    raise SystemExit(main())
