# GPT Byggaren 1.5.0 – migreringsplan

Projekt: **System Modeller**  
Utgångsläge: utvecklingsversion **0.1.0-dev.57**, Plan C komplett, fyra aktiva runtimes och unified build/release.

## Mål

Migrera projektkontrakt, runtimeparitet och build/release till GPT Byggaren 1.5.0 utan att förändra canonical systemmodelleringsbeteende eller Plan C-status.

## Preserve-first

Följande ska bevaras:

- `instructions/chat-runtime.md` som canonical runtime instruction.
- YAML som canonical source of truth.
- Stable IDs, provenance, evidence, origin och unresolved uncertainty.
- Runtimeflödet `INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`.
- Validering före och efter mutation.
- Fyra aktiva runtimes: Chat, Custom GPT, Claude Project och OpenCode.
- Unified build via `scripts/ci_build.py`.
- Release-readiness via `scripts/release_check.py`.
- Plan C-status och tidigare produkt-/utvecklingshistorik.

## Runtime-målbild

Aktiva runtimes:

1. Chat ZIP
2. Custom GPT
3. Claude Project
4. OpenCode

OpenAI Plugin ska bedömas explicit i 1.5.0 men inte aktiveras som full peer runtime om kärnkraven för projektfilåtkomst, mutation, validering, workspace och paketering inte kan uppfyllas.

## Steg

### 1. Separat 1.5.0-migrationsstatus
Inför separat plan/status utan att röra Plan C.

### 2. Normalisera projektkontrakt
Mappa befintliga capability-, artifact-, workspace/state- och tool-kontrakt till GPT Byggaren 1.5.0 och lägg till deterministisk validering.

### 3. Normalisera runtime registry/build metadata
Gör runtime-set, artifactnamn och compatibility deklarativa för 1.5.0.

### 4. Verifiera Chat ZIP
Verifiera canonical instruction, runtime tools, workspace authority och package parity.

### 5. Verifiera Custom GPT
Verifiera compiled instruction, Knowledge, plattformsbegränsningar och no-false-PASS.

### 6. Verifiera Claude Project och OpenCode
Behåll Claude som reduced och OpenCode som equivalent med typed custom tools och mutation approval.

### 7. OpenAI Plugin compatibility assessment
Dokumentera och CI-lås not_active/reduced/advisory om full parity inte kan uppfyllas.

### 8. Generalisera CI/release
Härled build/release-assets deklarativt och kör samma 1.5-gates i CI och release.

### 9. Slutlig release-readiness
Synka README/STATUS, lägg final readiness-gate och verifiera mergebar PR.


## Slutstatus

Migreringen är genomförd **9/9**.

Slutlig runtime-status:

- Chat ZIP — equivalent_runtime_dependent
- Custom GPT — equivalent_with_platform_constraints
- Claude Project — reduced
- OpenCode — equivalent
- OpenAI Plugin — not_active / reduced / advisory_only

CI, distributionsbuild, lokal release-readiness och GitHub Release använder samma GPT Byggaren 1.5.0-registry. Release-assets härleds exakt från `runtime-distribution-registry.yaml`, och full plugin-parity får inte påstås utan verifierad projektfilåtkomst, runtime-tool execution, persistent workspace/state, reliable validation/mutation och komplett projektpaketering.

Plan C är fortsatt komplett och utvecklingsversionen är fortsatt **0.1.0-dev.57**.
