# OpenCode workspace distribution

C4 introduces a deterministic OpenCode workspace projection of the canonical System Modeller project.

The package contains:

- generated root `AGENTS.md`
- `.opencode/runtime-contract.json`
- `opencode.json`
- typed custom tool wrappers under `.opencode/tools/`
- the explicitly declared runtime scripts plus their minimal support scripts
- canonical metamodel/schema knowledge under `.opencode/knowledge/`
- `manifest.yaml`, `README.md` and `VERSION`

The target System Modeller project is separate from the runtime workspace. Every custom tool therefore accepts an explicit `projectRoot` where relevant, defaulting to the OpenCode worktree root.

OpenCode V2 permissions are generated so read-only/derived System Modeller tools are allowed, while `system_model`, generic shell execution and generic edits require approval. The wrappers invoke Python directly through `Bun.spawn`; they do not expose an unrestricted shell argument.

Builder: `scripts/package_opencode.py`

Validator: `scripts/validate_opencode.py`
