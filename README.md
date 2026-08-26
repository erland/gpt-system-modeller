# System Modeller

**System Modeller** är ett planerat LLM-baserat verktygs- och GPT-paket för att bygga, förvalta, analysera och presentera en spårbar modell av hur ett system fungerar och är uppbyggt.

Målet är **systemförståelse före maximal implementationsdetalj**. Systemmodellen ska lagras i YAML och fungera som gemensam sanningskälla för arkitekturvyer, analyser och arkitekturbeskrivningar.

## Plan A – MVP

Detta repository befinner sig i **steg A23 av 30** i MVP-planen.

A1–A4 etablerade grund, scope, abstraktionsregler och gemensam modellbas. A5–A13 införde systemkontext, funktion, information, logisk struktur, integration och datalager. A14–A16 introducerar scenarier och deras dynamiska realisering genom Interaction, Participant och InteractionMessage. A17 inför RuntimeUnit som brygga från logisk arkitektur till deployment. A18 kompletterar runtime-lagret med Environment och DeploymentNode för att beskriva miljö och övergripande körplats.

## Grundprinciper

- **YAML är canonical source of truth** för systemmodellen.
- **Modell och vy separeras**; diagram ska kunna återskapas från modellen.
- **GPT-paket och systemprojekt separeras**; System Modeller är verktyget, systemprojektet innehåller modellen av ett konkret system.
- **Stabila ID:n** ska bevara modellobjektens identitet över tid.
- **Evidens och osäkerhet** ska vara explicita och spårbara.
- **Systemförståelse prioriteras framför maximal detalj**; implementation är underlag/evidens och blir inte automatiskt arkitektur.
- **Abstraktionsnivåer hålls isär** så att konceptuell, logisk, runtime- och implementationsnivå kan samexistera.
- **Fakta och inferens hålls isär**; observerat, dokumenterat och härlett ska kunna särskiljas.

Se [`docs/design-principles.md`](docs/design-principles.md) för grundprinciperna, [`docs/mvp-scope.md`](docs/mvp-scope.md) för MVP-målbilden och [`docs/modeling-principles.md`](docs/modeling-principles.md) för normativa abstraktions- och modelleringsregler.

## Repositorystruktur

```text
system-modeller/
├── README.md
├── VERSION
├── CHANGELOG.md
├── STATUS.md
├── instructions/     # GPT-instruktioner och runtime-regler
├── metamodel/        # Metamodell och semantiska regler
├── schemas/          # Maskinvaliderbara formatkontrakt
├── scripts/          # Deterministiska verktyg
├── templates/        # Projekt-, vy- och rapportmallar
├── examples/         # Referens- och användningsexempel
├── tests/            # Automatiska tester
├── docs/             # Design- och användardokumentation
└── distributions/    # Byggda distributionspaket (genererade)
```

## Utvecklingsflöde

Varje steg i Plan A ska:

1. utgå från senaste kompletta ZIP,
2. göra en avgränsad förändring,
3. uppdatera dokumentation och tester,
4. validera tidigare funktion,
5. skapa en ny komplett ZIP för nästa steg.

## Paketering

Kör från repositoryroten:

```bash
python3 scripts/check_structure.py
python3 scripts/package.py
```

`package.py` skapar en utvecklings-ZIP under `distributions/` och exkluderar genererade/temporära filer.

## Version

Aktuell utvecklingsversion finns i [`VERSION`](VERSION).

## Gemensam modellbas (A4)

Plan A steg A4 etablerar den första formella modellbasen:

- [`docs/model-format.md`](docs/model-format.md) – normativt gemensamt YAML-format, ID- och relationsregler.
- [`metamodel/common.yaml`](metamodel/common.yaml) – gemensamma fält och konventioner.
- [`metamodel/id-prefixes.yaml`](metamodel/id-prefixes.yaml) – provisoriskt prefixregister för stabila ID:n.
- [`schemas/common.schema.json`](schemas/common.schema.json) – återanvändbart JSON Schema för YAML-data.

Domänspecifika elementtyper introduceras från A5 och ska bygga ovanpå denna bas.


## Kontextmodell (A5)

Plan A steg A5 definierar [`System`, `ExternalSystem` och `Actor`](docs/context-model.md) samt deras första kontextrelationer. Den formella modellen finns i [`metamodel/context.yaml`](metamodel/context.yaml) och [`schemas/context.schema.json`](schemas/context.schema.json).


## Funktionell ansvarsnivå (A6)

Plan A steg A6 definierar [`Responsibility / SystemFunction`](docs/functional-model.md) som konceptuell gruppering av vad systemet ansvarar för. Den formella modellen finns i [`metamodel/functions.yaml`](metamodel/functions.yaml) och [`schemas/functions.schema.json`](schemas/functions.schema.json).

## Current model scope

Through A23 the MVP supports system context, actors, responsibilities, use cases, conceptual information, logical architecture, interfaces/APIs, messages/events, data stores, scenarios, dynamic interactions, runtime/deployment and architecture decisions/constraints.

## Informationsanvändning (A9)

Se [`docs/information-usage.md`](docs/information-usage.md), [`metamodel/information-usage.yaml`](metamodel/information-usage.yaml) och [`schemas/information-usage.schema.json`](schemas/information-usage.schema.json).


## Logisk arkitektur (A10)

Se [`docs/logical-architecture.md`](docs/logical-architecture.md), [`metamodel/logical-structure.yaml`](metamodel/logical-structure.yaml) och [`schemas/logical-structure.schema.json`](schemas/logical-structure.schema.json).

## Dynamiska interaktioner (A15)

Se [`docs/interactions.md`](docs/interactions.md), [`metamodel/interactions.yaml`](metamodel/interactions.yaml) och [`schemas/interactions.schema.json`](schemas/interactions.schema.json).


## Deploymenttopologi och kommunikation (A19)

Se [`docs/deployment-relations.md`](docs/deployment-relations.md) och den normativa modellen i [`metamodel/deployment.yaml`](metamodel/deployment.yaml). A19 inför `deployed_on`, `belongs_to` och `connects_to` som grund för MVP:ns övergripande deployment-vy.

## Current development status

Plan A steg A1–A30 är implementerade. MVP:n är redo för praktiskt Chat-ZIP-test mot verkliga system.


## Arkitekturbeslut och constraints (A20)

Se [`docs/architecture-decisions-and-constraints.md`](docs/architecture-decisions-and-constraints.md), [`metamodel/decisions.yaml`](metamodel/decisions.yaml) och [`schemas/decisions.schema.json`](schemas/decisions.schema.json).

## Provenance i MVP

Från A21 kan modellobjekt och relationer spåras via `Evidence` → `SourceReference` → `Source`, utan att källmaterial blandas ihop med arkitekturelement.

## Declared, observed och inferred (A22)

Från A22 är `origin` en validerad dimension på modellobjekt och relationer. Se [`docs/origin-declared-observed-inferred.md`](docs/origin-declared-observed-inferred.md) och [`metamodel/origin.yaml`](metamodel/origin.yaml). Origin hålls separat från A21:s Evidence-status så att exempelvis en infererad logisk komponent kan vara starkt källunderbyggd.


## Systemprojektformat (A23)

Från A23 finns ett normativt, portabelt systemprojektformat med obligatorisk `project.yaml`, kanoniska modellshards under `model/` och separata kataloger för interaktioner, implementation/evidens, källor, vyer, rapporter, issues och exporter. Se [`docs/system-project-format.md`](docs/system-project-format.md), [`schemas/project.schema.json`](schemas/project.schema.json) och [`templates/system-project/`](templates/system-project/).

## Projektvalidering

Från A25 kan systemprojekt valideras med `python3 scripts/validate.py /path/to/project`.


## Vyer (A26)

Från A26 finns ett generellt vyformat och sex kärnvyer: System Context, Functional Overview, Use Case Overview, Information Overview, Functional–Information View och Logical Component View. Vyer materialiseras från den kanoniska modellen med `python3 scripts/view.py /path/to/project --type system_context` eller från en YAML-definition under projektets `views/`. Se [`docs/views.md`](docs/views.md), [`metamodel/views.yaml`](metamodel/views.yaml) och [`schemas/views.schema.json`](schemas/views.schema.json).

## A27 – tvärgående och dynamiska vyer

MVP-vymotorn stödjer nu tio arkitekturvyer, inklusive Use Case Realization, Integration, Sequence och Deployment, samt Mermaid/PlantUML-rendering.

## Arkitekturbeskrivning (A28)

`python3 scripts/report.py <system-project>` genererar MVP:ns samlade arkitekturbeskrivning i Markdown med härledda arkitekturvyer.


## A29 – käll- och dokumentanalys

MVP:n innehåller nu ett spårbart analysflöde för dokumentation och källkod. `scripts/analyze.py` skapar en deterministisk inventering och `instructions/source-analysis.md` beskriver hur LLM:n ska skapa Observation → Evidence → kandidat → kanonisk modell utan att likställa kodstruktur med arkitektur. Se `docs/source-analysis.md`.


## A30 – Plan A MVP komplett

Plan A är slutförd. `examples/reference-order-system/` innehåller ett end-to-end-referenssystem med golden model, tio arkitekturvyer och arkitekturbeskrivning.

Bygg första Chat-distributionen med:

```bash
python3 scripts/package_chat.py
```

Bygg ett portabelt systemprojekt med:

```bash
python3 scripts/package_project.py /path/to/system-project --output project.zip
```

Se [`docs/mvp-reference-test.md`](docs/mvp-reference-test.md) och [`SYSTEM-MODELLER-CHAT.md`](SYSTEM-MODELLER-CHAT.md).


## A31 – Custom GPT-distribution

Custom GPT är definierad som en **genererad projektion av samma kanoniska System Modeller-källor**, inte som en separat handunderhållen produktdefinition. Se [`docs/custom-gpt-distribution.md`](docs/custom-gpt-distribution.md) och den maskinläsbara källmappningen [`templates/custom-gpt-distribution.yaml`](templates/custom-gpt-distribution.yaml).

A32 implementerar buildern som genererar `instructions.md`, sex optimerade Knowledge-filer och `manifest.yaml`.

## Custom GPT build

A32 can generate the first Custom GPT distribution from the same canonical sources as the Chat distribution:

```bash
python3 scripts/package_custom_gpt.py
```

See `docs/custom-gpt-builder.md`.



## GitHub Actions

Från A34 finns `.github/workflows/build-distributions.yml`, som kör regressionstester och bygger både Chat- och Custom GPT-distributionen med gemensam versionskälla och paritetsvalidering. Se `docs/github-actions.md`.
