# Status

- Current plan: Plan B – Runtime robustness and architecture reporting
- Plan A completion marker: A1–A30 / A30 — Plan A complete
- Completed: A1–A39 / A30 + A31 + A32 + A33 + A34 + A35 + A36 + A37 + A38 + A39
- Plan B progress: B11 / B12
- Current version: 0.1.0-dev.49
- Milestone: **Report-profile registry supports future variants while standard remains the only implemented profile**
- Next: B12 – finalize Chat/Custom GPT distribution packaging, regression and release readiness for Plan B.

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

### B4 result

`evals/small-model/suite.yaml` now groups the B1 evals into four explicit dimensions: instruction adherence, model quality, provenance/uncertainty and deterministic tool use. The same suite applies to `small_local`, `general_chat` and `strong_reasoning` comparison classes.

`scripts/evaluate_small_model.py` validates the suite and deterministically scores recorded rubric judgments. Critical case failures explicitly set `canonical_mutation_allowed: false`, allowing the regression result to distinguish safe read/analysis use from safe canonical mutation. Passing and deliberate critical-failure fixtures plus `tests/test_b4.py` lock the scoring and safety-gate behavior.

### B5 result

`metamodel/report-profiles/standard.yaml` is now the canonical internal profile for the standard architecture description. It declares the stable twelve-section structure, section-to-view mapping, concise narrative policy and the diagram budgets that B6–B8 will enforce.

`scripts/report_profile.py` validates the profile deterministically, including exact section order, internal-only status and preferred/hard diagram budgets. `tests/test_b5.py` verifies that the current generated architecture description still matches the profile section structure, so B5 establishes a declarative contract without changing the existing A28 report output.

The profile intentionally remains `user_selectable: false`; support for alternative report structures/detail levels is deferred until B11 after the standard report path is stable.

### B6 result

`scripts/diagram_complexity.py` now measures every materialized profile view deterministically before rendering. It records element and relationship counts and classifies each diagram as `within_preferred`, `above_preferred` or `above_hard` using the B5 standard-profile budgets.

When `split_large_views` is enabled, diagrams above preferred are marked `split_recommended`. Sequence views additionally report Interaction count, unique participant count and message count as groundwork for B8. B6 does not yet alter rendering; deterministic splitting is reserved for B7.

`docs/diagram-complexity.md` documents the contract and `tests/test_b6.py` verifies thresholds, sequence metrics, profile view ordering and reference-project measurement. The complexity tool and documentation are included in the portable Chat runtime.

### B7 result

`scripts/view_split.py` now splits oversized `logical_component`, `integration`, `deployment` and `functional_information` views before rendering. It prefers semantic anchors from the model—Subsystem, Responsibility, Environment/DeploymentNode and integration provider/producer nodes—and otherwise falls back to stable-ID partitioning.

Each split produces overview part(s) first and then deterministic detail parts. Detail parts cover all original elements and are chunked against the preferred element and relationship budgets. `scripts/report.py` now renders those parts as separate Mermaid diagrams while keeping small views byte-compatible with the earlier report path.

`docs/diagram-splitting.md` documents the strategy, `tests/test_b7.py` locks semantic splitting, fallback behavior, coverage and determinism, and the split runtime follows the portable Chat ZIP.

### B8 result

`scripts/sequence_diagrams.py` now materializes sequence views with exactly one canonical `Interaction` per diagram when the standard profile declares `one_interaction_per_diagram: true`. Interactions are ordered deterministically by Scenario name/ID and then Interaction name/ID.

`scripts/report.py` renders each relevant Interaction as its own Mermaid block under a stable `Scenario – Interaction` heading. Participants and messages are therefore isolated to the current interaction and unrelated scenarios are never merged into one sequence diagram.

`docs/scenario-sequence-diagrams.md` documents the contract, `tests/test_b8.py` verifies ordering, isolation and one-Interaction-per-diagram behavior, and the helper plus documentation are included in the portable Chat ZIP.

### B9 result

The standard report profile now contains a canonical `presentation.pdf` contract covering A4 page geometry, margins, heading hierarchy, major-section page breaks, diagram width/height and captions, table wrapping/header behavior, body/table typography, code wrapping and widow/orphan/page-number rules.

`scripts/report_profile.py` validates the PDF contract and `scripts/pdf_contract.py` exposes it deterministically as `system-modeller-pdf-presentation-v1` together with section order and the B6–B8 diagram policy. This keeps PDF layout derived from the same report profile as Markdown instead of creating a second presentation source of truth.

`docs/pdf-presentation-contract.md` documents the contract and `tests/test_b9.py` locks the key values plus invalid-profile rejection. The PDF contract helper and documentation are included in the portable Chat ZIP. B9 defines presentation requirements; B10 adds end-to-end report regression over representative system sizes.

### B10 result

`evals/report-regression/cases.yaml` now defines deterministic `small`, `medium` and `dense` architecture-report regression levels. `scripts/evaluate_report_regression.py` generates temporary system projects from those declarations and runs the complete standard report composition path.

The regression verifies stable twelve-section report structure, B7 split behavior, preferred diagram budgets, semantic coverage of split detail views, and B8 one-Interaction-per-diagram isolation. Repeated runs must produce identical machine-readable summaries. The medium case exercises multiple split paths and the dense case exercises all four B7-supported view types.

`docs/report-regression.md` documents the contract and `tests/test_b10.py` locks determinism, representative density growth and the expected sequence-diagram counts. B10 deliberately tests report composition rather than adding report variants; profile variation remains B11 work.

### B11 result

`metamodel/report-profiles/catalog.yaml` now defines the stable profile identities `overview`, `standard` and `detailed`. `standard` is the only implemented and stable profile, remains the default, and all three identities remain `user_selectable: false`.

`scripts/report_profile.py` now resolves profiles through the catalog while preserving `report_profile.load()` as the standard default. Explicit `profile="standard"` resolves identically; `overview` and `detailed` fail deterministically as planned-but-not-implemented rather than silently aliasing the standard report. Unknown profiles also fail explicitly.

`docs/report-profile-groundwork.md` documents the lifecycle boundary and `tests/test_b11.py` locks the registry, default resolution and non-selectability contract. The catalog is included through the metamodel and the documentation follows the portable Chat ZIP. B11 does not create alternate report output or expose a user-facing profile switch.

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
