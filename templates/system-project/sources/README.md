# sources

Provenance och analysarbetsdata.

- `sources.yaml` – Source-poster.
- `references.yaml` – exakta SourceReference-poster.
- `evidence.yaml` – Evidence-poster som modellobjekt/relationer refererar.
- `observations.yaml` – A29 Observation-poster. Observationer är arbets-/evidensdata och ska inte visas som arkitektur.

Vid käll- eller dokumentanalys kan `scripts/analyze.py inventory <path>` användas för att skapa en deterministisk inventering före LLM-analysen.
