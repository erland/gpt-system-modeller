# Runtime instruction – source analysis

When asked to analyze source code or documentation for a System Modeller project:

1. Preserve the canonical model as the truth source; source files are evidence.
2. Prefer system understanding over implementation inventory.
3. First identify concrete observations and their source references.
4. Separate observed facts from inferred architecture concepts.
5. Never infer Class=Component, Endpoint=UseCase, Table=InformationObject or Repository=Subsystem solely from structural similarity.
6. Group implementation elements only when responsibility, dependencies, naming and/or documentation support the grouping.
7. Before adding a candidate concept, search the existing model for the same concept and reuse its stable ID when appropriate.
8. Inferred architecture elements/relations use `origin: [inferred]` and evidence. Direct implementation facts use `origin: [observed]` when represented.
9. Prefer conceptual/logical candidates: Actor, Responsibility, UseCase, InformationObject, Component, Service, API, DataStore, Scenario, RuntimeUnit and DeploymentNode.
10. Record unresolved ambiguity instead of inventing precision.
11. Validate the project after updates.
12. Keep observations under `sources/observations.yaml`; do not include Observation records in architecture views/reports.

Use `scripts/analyze.py inventory <path>` for a deterministic source inventory when useful. It prepares input; semantic conclusions must come from actual file content and LLM reasoning.
