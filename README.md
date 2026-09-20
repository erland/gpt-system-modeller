# System Modeller

**System Modeller** är ett LLM-baserat stöd för att bygga, förvalta, analysera och presentera en spårbar modell av hur ett system fungerar och är uppbyggt.

Målet är **systemförståelse före maximal implementationsdetalj**. Den kanoniska systemmodellen lagras i YAML och är sanningskälla för arkitekturvyer, analyser, rapporter och exporter.

## Status

Plan A (MVP), Plan B (runtime-robusthet och rapportering) och Plan C (multi-runtime distributions) är implementerade.

System Modeller byggs från samma canonical projektkontrakt till fyra runtime-distributioner:

- Chat ZIP
- Custom GPT
- Claude Project
- OpenCode workspace

Aktuell utvecklingsversion finns i [`VERSION`](VERSION). Maskinläsbar projektstatus finns i [`project-status.yaml`](project-status.yaml) och runtime-/capability-kontraktet i [`gpt-project.yaml`](gpt-project.yaml).

## Grundprinciper

- **YAML är canonical source of truth** för systemmodellen.
- **Modell och vy separeras**; diagram och rapporter härleds från modellen.
- **Runtime-distribution och systemprojekt separeras**; System Modeller är verktyget, systemprojektet innehåller modellen av ett konkret system.
- **Stabila ID:n** bevarar modellobjektens identitet över tid.
- **Evidens, origin och osäkerhet** ska vara explicita och spårbara.
- **Systemförståelse prioriteras framför maximal detalj**; implementation är evidens och blir inte automatiskt arkitektur.
- **Fakta och inferens hålls isär**; deklarerat, observerat och infererat innehåll ska kunna särskiljas.
- **Validering före och efter mutation** är en del av det canonical runtimeflödet.

Fördjupning: [`docs/modeling-principles.md`](docs/modeling-principles.md) beskriver de normativa modellerings- och abstraktionsreglerna.

Det gemensamma runtimeflödet är:

`INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`

## Repositorystruktur

```text
system-modeller/
├── README.md
├── VERSION
├── CHANGELOG.md
├── STATUS.md
├── gpt-project.yaml
├── project-status.yaml
├── instructions/     # canonical runtime- och source-analysis-instruktioner
├── metamodel/        # metamodell och rapportprofiler
├── schemas/          # maskinvaliderbara formatkontrakt
├── scripts/          # deterministiska verktyg, builders och validators
├── templates/        # systemprojekt- och distributionsspecifikationer
├── examples/         # referenssystem och testunderlag
├── evals/            # instruction/small-model/report-evals
├── tests/            # regressionstester
└── docs/             # design-, runtime- och användardokumentation
```

## Runtime-distributioner

### Chat

Bygg:

```bash
python3 scripts/package_chat.py
```

Chat-paketet innehåller runtime-relevant canonical material och deterministiska scripts.

### Custom GPT

Bygg:

```bash
python3 scripts/package_custom_gpt.py
```

Custom GPT är en kompakt genererad projektion av samma canonical källor. Instruktionen hålls inom Custom GPT:s distributionsbudget och kompletteras med genererade Knowledge-filer.

### Claude Project

Bygg:

```bash
python3 scripts/package_claude.py
```

Claude Project innehåller Project Instructions, Knowledge, runtime contract och manifest. Lokal Python-scriptkörning betraktas som otillgänglig; canonical mutation ska stoppas om tillförlitlig validering inte kan utföras.

### OpenCode

Bygg:

```bash
python3 scripts/package_opencode.py
```

OpenCode-workspacet innehåller `AGENTS.md`, `.opencode/runtime-contract.json`, `opencode.json` och typade project-local custom tools. Muterande modelloperationer kräver approval.

## Unified build

Den rekommenderade buildvägen för projektet och samtliga runtimes är:

```bash
python3 scripts/ci_build.py --output-dir dist
```

Den producerar:

- `system-modeller-project-vX.Y.Z.zip`
- `system-modeller-chat-vX.Y.Z.zip`
- `system-modeller-custom-gpt-vX.Y.Z.zip`
- `system-modeller-claude-vX.Y.Z.zip`
- `system-modeller-opencode-vX.Y.Z.zip`
- `runtime-parity.yaml`
- `SHA256SUMS.txt`
- `build-manifest.yaml`

Full lokal release-readiness:

```bash
python3 scripts/release_check.py --output-dir release-dist
```

## Systemprojekt

Ett konkret System Modeller-projekt använder obligatorisk `project.yaml`, canonical YAML-shards och separata kataloger för bland annat interactions, sources, views, reports och exports.

Validera ett systemprojekt:

```bash
python3 scripts/validate.py /path/to/system-project
```

Skapa kompakt arbetskontext:

```bash
python3 scripts/context.py /path/to/system-project --format yaml
```

Generera arkitekturbeskrivning:

```bash
python3 scripts/report.py /path/to/system-project
```

Paketera ett portabelt systemprojekt:

```bash
python3 scripts/package_project.py /path/to/system-project --output project.zip
```

## GitHub Actions och release

`.github/workflows/build-distributions.yml` verifierar repositoryt och bygger den unified leveransen på pull requests, `main` och manuella körningar.

En publicerad GitHub Release använder release-taggen som auktoritativ versionskälla och bifogar projektpaketet, alla fyra runtime-ZIP:ar, parity report, checksummor och build manifest. Endast release-jobbet har write-behörighet.

Se [`docs/github-actions.md`](docs/github-actions.md), [`docs/unified-build.md`](docs/unified-build.md), [`docs/runtime-parity-baseline.md`](docs/runtime-parity-baseline.md), [`docs/claude-project-distribution.md`](docs/claude-project-distribution.md) och [`docs/opencode-distribution.md`](docs/opencode-distribution.md).

## Utveckling

Kör hela regressionen:

```bash
bash scripts/test.sh
```

Projektets utvecklingsplaner och historik finns i `docs/PLAN-*.md`, `STATUS.md` och `CHANGELOG.md`.
