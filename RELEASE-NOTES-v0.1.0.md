# System Modeller v0.1.0 – release notes

System Modeller v0.1.0 is the first MVP release candidate for building a traceable YAML-based architecture model focused on system understanding.

## Highlights

- Conceptual, logical, runtime and implementation abstraction levels.
- Actors, responsibilities, use cases and information objects.
- Subsystems, components, services, interfaces/APIs, messages/events and data stores.
- Scenarios, interactions and sequence flows.
- Runtime units, environments, deployment nodes and communication relations.
- Architecture decisions and constraints.
- Provenance/evidence plus declared, observed and inferred origin semantics.
- Portable system-project ZIP format with stable IDs and validation.
- Ten MVP architecture views, including use-case realization, integration, sequence and deployment.
- Markdown architecture-description generation.
- LLM-oriented source-analysis workflow with observations and candidate concepts.
- Deterministic Chat and Custom GPT distributions with parity validation.
- GitHub Actions workflow that tests, builds and uploads both distributions.

## Distribution artifacts

- `system-modeller-chat-v0.1.0.zip`
- `system-modeller-custom-gpt-v0.1.0.zip`
- `build-manifest.yaml`

## Release verification

Run `python scripts/release_check.py --output-dir release-dist` and require `status: READY`. A real GitHub Actions run should then be executed once to verify hosted-runner behavior and artifact upload before publishing/tagging v0.1.0.
