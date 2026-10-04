# GPT Byggaren 1.5.0 – migreringsplan

Projekt: **System Modeller**  
Utgångsläge: utvecklingsversion **0.1.0-dev.57**, Plan C komplett, fem aktiva runtimes och unified build/release.

## Mål

Migrera projektkontrakt, runtimeparitet och build/release till GPT Byggaren 1.5.0 utan att förändra canonical systemmodelleringsbeteende eller Plan C-status.

## Preserve-first

Följande ska bevaras:

- `instructions/chat-runtime.md` som canonical runtime instruction.
- YAML som canonical source of truth.
- Stable IDs, provenance, evidence, origin och unresolved uncertainty.
- Runtimeflödet `INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`.
- Validering före och efter mutation.
- Fem aktiva runtimes: Chat, Custom GPT, Claude Project, OpenCode och OpenAI Plugin.
- Unified build via `scripts/ci_build.py`.
- Release-readiness via `scripts/release_check.py`.
- Plan C-status och tidigare produkt-/utvecklingshistorik.

## Runtime-målbild

Aktiva runtimes:

1. Chat ZIP
2. Custom GPT
3. Claude Project
4. OpenCode
5. OpenAI Plugin

OpenAI Plugin är aktiv som `equivalent_runtime_dependent`. Full canonical körning kräver projektfilåtkomst, persistent workspace/state och kompatibel Python code execution för validation before/after, mutation, deterministic derive och packaging.

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
Aktivera skills-first Plugin, paketera explicit runtime-script closure och CI-lås host-dependent parity, mutation approval och no-false-PASS.

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
- OpenAI Plugin — equivalent_runtime_dependent

CI, distributionsbuild, lokal release-readiness och GitHub Release använder samma GPT Byggaren 1.5.0-registry. Release-assets härleds exakt från `runtime-distribution-registry.yaml`, och Plugin-parity är runtime-dependent och full canonical körning får endast påstås när projektfilåtkomst, Python runtime-tool execution, persistent workspace/state, reliable validation/mutation och komplett projektpaketering faktiskt finns.

Plan C är fortsatt komplett och utvecklingsversionen är fortsatt **0.1.0-dev.57**.
