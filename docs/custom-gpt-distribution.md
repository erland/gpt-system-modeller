# Custom GPT-distribution – normativ specifikation (A31)

## 1. Syfte

System Modeller ska kunna distribueras både som Chat-ZIP och som Custom GPT utan att två semantiskt separata produktdefinitioner behöver underhållas.

Custom GPT-distributionen är därför en **genererad projektion av samma kanoniska repositoryinnehåll** som Chat-distributionen använder.

## 2. Source-of-truth-princip

Följande gäller normativt:

1. `VERSION` är enda källa för produktversion.
2. Metamodell och relationer under `metamodel/` är enda normativa källa för modellsemantik.
3. JSON Schemas under `schemas/` är enda normativa källa för maskinvaliderbara formatregler.
4. `docs/` innehåller den normativa mänskligt läsbara modellerings- och användarguiden.
5. `instructions/chat-runtime.md` och `instructions/source-analysis.md` innehåller delad runtime-semantik som även Custom GPT ska härleda sitt beteende från.
6. `templates/custom-gpt-distribution.yaml` är den deklarativa kartan från kanoniska källor till Custom GPT-artefakter.
7. Filer i ett byggt `system-modeller-custom-gpt-*.zip` är **genererade artefakter** och får aldrig redigeras som source of truth.
8. En ändring som påverkar både Chat och Custom GPT ska göras i den gemensamma kanoniska källan och därefter byggas om till båda distributionerna.

## 3. Avsedd output

A32 ska generera ungefär följande paket:

```text
system-modeller-custom-gpt-v0.1.0.zip
└── system-modeller-custom-gpt/
    ├── manifest.yaml
    ├── instructions.md
    └── knowledge/
        ├── 01-modeling-core.md
        ├── 02-metamodel-reference.md
        ├── 03-project-format-and-validation.md
        ├── 04-views-and-architecture-description.md
        ├── 05-source-analysis-and-evidence.md
        └── 06-reference-example.md
```

Exakta filnamn styrs av `templates/custom-gpt-distribution.yaml`.

## 4. Custom GPT-instruktionen

`instructions.md` ska vara en **kompakt genererad runtime-instruktion**, inte en kopia av hela Knowledge-basen.

Den ska innehålla det som måste ligga nära modellens beteende:

- rollen System Modeller,
- huvudmålet systemförståelse,
- YAML-modellen som sanningskälla,
- separation mellan GPT-paket och systemprojekt,
- arbetsordning för befintligt systemprojekt,
- arbetsordning för källkod/dokumentation,
- abstraktionsreglerna Class ≠ Component, Endpoint ≠ UseCase, Table ≠ InformationObject,
- evidens/origin och hantering av osäkerhet,
- krav att validera före/efter modelländring,
- att vyer och rapporter genereras från modellen,
- vilka MVP-vyer som stöds.

Detaljerade tabeller, full metamodell och långa exempel hör hemma i Knowledge-filerna.

## 5. Knowledge-bundle

### 01-modeling-core.md

Kanoniska källor:

- `docs/design-principles.md`
- `docs/modeling-principles.md`
- `docs/mvp-scope.md`

Syfte: målbild, abstraktionsnivåer, terminologi och centrala anti-patterns.

### 02-metamodel-reference.md

Kanoniska källor:

- `metamodel/*.yaml`
- relevanta beskrivningar i `docs/`

Syfte: kompakt men komplett referens över element, relationer, ID-prefix och viktig semantik.

### 03-project-format-and-validation.md

Kanoniska källor:

- `docs/system-project-format.md`
- `docs/model-format.md`
- `docs/model-operations.md`
- `docs/validation.md`
- `schemas/project.schema.json`

Syfte: hur systemprojektet är uppbyggt, ändras och valideras.

### 04-views-and-architecture-description.md

Kanoniska källor:

- `docs/views.md`
- `docs/architecture-description.md`

Syfte: tio MVP-vyer, detaljnivåer, diagramprincip och rapportstruktur.

### 05-source-analysis-and-evidence.md

Kanoniska källor:

- `instructions/source-analysis.md`
- `docs/source-analysis.md`
- `docs/provenance-and-evidence.md`
- `docs/origin-declared-observed-inferred.md`

Syfte: reverse engineering-flödet, observationer, evidens, origin och inference-regler.

### 06-reference-example.md

Kanoniska källor:

- `docs/mvp-reference-test.md`
- valda, genererade utdrag från `examples/reference-order-system/`

Syfte: konkret referens för hur en sammanhängande modell och arkitekturbeskrivning ser ut.

## 6. Vad som inte ska följa med Custom GPT-paketet

Normalt ska följande inte läggas i Knowledge eller instruktionen:

- hela `tests/`-trädet,
- Python-scripts som rena kodkopior,
- historiska utvecklingsartefakter,
- `distributions/`,
- temporära filer/cache,
- duplicerade versioner av samma normtext,
- hela golden-outputen när ett kort referensutdrag räcker.

Detta material får användas av bygg/validering men ska inte belasta Custom GPT:s Knowledge i onödan.

## 7. Paritet mellan Chat och Custom GPT

Funktionell paritet betyder för v0.1.0 att båda distributionerna ska förstå samma:

- elementtyper,
- relationer,
- abstraktionsnivåer,
- evidens- och originregler,
- systemprojektformat,
- tio MVP-vyer,
- arkitekturbeskrivningsstruktur,
- source-analysis-principer.

Paritet betyder **inte** att ZIP-paketen behöver innehålla samma filer. Chat-ZIP kan bära runtime-scripts, schemas, mallar och referensmaterial; Custom GPT ska bära en optimerad instruktion och Knowledge-projektion. Utvecklingsmaterial som tester och releaseverktyg behöver inte följa med i Chat-runtime:n.

## 8. Versionering

- Repositoryversion läses från `VERSION`.
- Under utveckling kan den vara exempelvis `0.1.0-dev.31`.
- Releaseartefaktens publika version normaliseras enligt release/build-reglerna i kommande A32–A35.
- Chat och Custom GPT från samma build/release måste rapportera samma produktversion i sina manifests.

Ingen versionssträng får handunderhållas separat i genererade Custom GPT-filer.

## 9. Genereringskrav för A32

A32-buildern ska:

1. läsa `templates/custom-gpt-distribution.yaml`,
2. läsa version från `VERSION`,
3. kontrollera att alla deklarerade source-filer finns,
4. generera `instructions.md`,
5. generera Knowledge-filerna i deklarerad ordning,
6. generera `manifest.yaml` med source mapping och checksummor,
7. bygga ZIP deterministiskt,
8. aldrig skriva tillbaka till kanoniska source-filer.

## 10. Valideringskrav för A33

A33 ska bland annat kontrollera:

- att instruktionen inte saknar kritiska runtime-regler,
- att alla Knowledge-sektioner kan härledas till deklarerade källor,
- att versionen är synkad,
- att inga förbjudna utvecklingsfiler följer med,
- att centrala modellkoncept finns i både Chat- och Custom GPT-projektionen,
- att byggt paket är reproducerbart.

## 11. Designbeslut

### A31-01 – En kanonisk produktdefinition

**Beslut:** Chat och Custom GPT ska genereras från samma repositorykällor.

**Motiv:** minskar drift, dubbelunderhåll och risken att de två distributionsformerna beter sig olika.

### A31-02 – Custom GPT är en optimerad projektion

**Beslut:** Custom GPT-paketet ska inte vara Chat-ZIP med nytt filnamn.

**Motiv:** Custom GPT har ett annat runtime- och Knowledge-format och bör optimeras för instruktionens och Knowledge-filernas funktion.

### A31-03 – Declarative distribution map

**Beslut:** `templates/custom-gpt-distribution.yaml` är den enda mappningen mellan kanoniska källor och Custom GPT-output.

**Motiv:** builder och parity-test kan då använda samma maskinläsbara kontrakt.
