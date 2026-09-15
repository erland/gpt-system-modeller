# Status

- Current plan: Plan B – Runtime robustness and architecture reporting
- Plan A completion marker: A1–A30 / A30
- Completed: A1–A39 / A30 + A31 + A32 + A33 + A34 + A35 + A36 + A37 + A38 + A39
- Plan B progress: B3 / B12
- Current version: 0.1.0-dev.41
- Milestone: **Chat runtime simplified into explicit deterministic operations**
- Next: B4 – add small-model regression coverage for the simplified runtime and context-driven workflow.

## Plan B

Plan B focuses first on Chat-runtime robustness for simpler models and then on deterministic, readable architecture reporting and diagram composition. The normative development plan is in `docs/PLAN-B-runtime-robustness-and-reporting.md`.

### B1 result

A model-neutral small-model eval suite now defines baseline expectations for:

- explicit runtime operation order,
- validation before canonical mutation,
- reuse of stable IDs and avoidance of semantic duplicates,
- preservation of origin, evidence and unresolved uncertainty,
- minimal relevant working context,
- preference for deterministic project tools over free-form reconstruction.

The evals live under `evals/small-model/` and are intended to be reusable across model families.

### B2 result

`scripts/context.py` now produces a deterministic compact working context containing project metadata, model and relationship counts, validation state, canonical shard inventory, uncertainty signals, duplicate-name candidates and optional focused matches. It delegates validation to the existing deterministic validator and is included in the portable Chat runtime together with `docs/context-summary.md`.

The output explicitly carries the Plan B runtime sequence `INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE` but does not replace canonical YAML as source of truth.

### B3 result

`instructions/chat-runtime.md` is now structured directly around the seven runtime operations `INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`.

The contract now makes `scripts/context.py` the preferred entry point for `INSPECT`, requires validation before canonical mutation, maps each operation to deterministic runtime tools, defines stop conditions after validation failures, and keeps stable IDs, provenance and unresolved uncertainty explicit. `SYSTEM-MODELLER-CHAT.md` mirrors the same core flow so bootstrap and runtime instructions no longer depend on an implicit interpretation of the older numbered checklist.

## A36 result

GitHub tag `vX.Y.Z` is authoritative for release distributions. The same resolved version is injected into Chat and Custom GPT package metadata and filenames. `VERSION` remains the development fallback.

## Source of truth

Canonical model/runtime sources remain unchanged. Release version authority is contextual: GitHub tag for tagged releases, `VERSION` otherwise.

## Repository cleanup after A36
A conservative cleanup removed superseded duplicate/generated artifacts while preserving active regression fixtures. The A23 duplicate example project and stored golden reference ZIP are no longer required; tests now validate the maintained reference project and deterministic packaging directly.

## A37 result

Pull requests run the full regression suite, pushes to `main` and manual runs additionally build/validate both distributions, and `release.published` builds and attaches Chat, Custom GPT and the build manifest to the GitHub Release. Only the release job receives `contents: write`.

## A38 result

Development distribution versions (`X.Y.Z-dev.N`) are now valid inputs to ZIP parity validation, while release/tag parsing remains strict (`vX.Y.Z` or `X.Y.Z`). This fixes the A36 hosted main-build failure without weakening release validation.

## A39 – Test environment isolation

Release/tag environment variables are now isolated from ordinary regression tests. Explicit version-context tests inject their own environment, so the same suite behaves identically on PR, main, workflow_dispatch and release.published jobs.
