# Systemprojektets format (A23)

## Syfte

Ett **systemprojekt** är den portabla och versionshanteringsbara representationen av modellen för ett konkret system. Det är uttryckligen separat från själva **System Modeller-GPT-paketet**.

```text
System Modeller GPT                Systemprojekt
------------------                -------------
instruktioner                     project.yaml
metamodell        arbetar med →   model/
schemas                           interactions/
scripts                           sources/
tester                            views/
                                  reports/
                                  issues/
                                  exports/
```

Systemprojektet ska kunna packas som ZIP, bifogas i en ny konversation, ändras och returneras utan att modellens identiteter eller semantik går förlorade.

## ZIP-rot

En distributions-ZIP ska ha en enda rotkatalog:

```text
system-project/
```

Projektets namn behöver alltså inte vara mappnamnet; den stabila identiteten finns i `project.yaml`.

## Obligatoriskt

Minimikravet är:

```text
system-project/
├── project.yaml
└── model/
```

`project.yaml` är alltid obligatorisk. `model/` är den kanoniska modellens hemvist. Ett helt nytt projekt får ha tomma modellshards.

## Rekommenderad MVP-struktur

```text
system-project/
├── project.yaml
├── model/
│   ├── context.yaml
│   ├── functions.yaml
│   ├── use-cases.yaml
│   ├── information.yaml
│   ├── structure.yaml
│   ├── integrations.yaml
│   ├── data-stores.yaml
│   ├── deployment.yaml
│   ├── decisions.yaml
│   └── relationships.yaml
├── interactions/
├── implementation/
├── sources/
├── views/
├── reports/
├── issues/
└── exports/
```

### `model/`

Innehåller den **kanoniska arkitekturmodellen**. Filuppdelningen är organisatorisk; identiteter och referenser gäller över hela projektet.

| Fil | Primärt innehåll |
|---|---|
| `context.yaml` | System, ExternalSystem, Actor |
| `functions.yaml` | Responsibility |
| `use-cases.yaml` | UseCase |
| `information.yaml` | InformationObject |
| `structure.yaml` | Subsystem, Component, Service |
| `integrations.yaml` | Interface, API, Message, Event |
| `data-stores.yaml` | DataStore |
| `deployment.yaml` | RuntimeUnit, Environment, DeploymentNode |
| `decisions.yaml` | ArchitectureDecision, Constraint |
| `relationships.yaml` | relationer som inte naturligt ägs av en annan shard |

En framtida validator får slå samman shards till en logisk helhetsmodell före referens- och semantikvalidering.

### `interactions/`

Dynamiska scenarier och interaktioner. Ett större projekt kan exempelvis ha en fil per viktigt scenario utan att skapa en fil per enskilt modellobjekt.

### `implementation/`

Kod- och implementationselement som främst används som evidens eller för teknisk fördjupning. Innehållet får inte automatiskt upphöjas till logisk arkitektur.

### `sources/`

Provenance: Source, SourceReference och Evidence. Senare steg kan även lagra observationsresultat här.

### `views/`

Återanvändbara vydefinitioner. Vyer är projektioner av modellen och aldrig sanningskälla för modellinnehållet.

### `reports/`

Rapportdefinitioner och rapportkällor. Genererad arkitekturbeskrivning får bygga på dessa men modellen ligger fortfarande i `model/`.

### `issues/`

Kända oklarheter, konflikter och öppna frågor.

### `exports/`

Endast genererade artefakter, till exempel diagram och exporterad Markdown. **Innehållet i `exports/` får aldrig användas som kanonisk modellkälla.**

## `project.yaml`

Exempel:

```yaml
format: system-modeller-project
project:
  id: order-system
  name: Order System
  description: Referensprojekt för System Modeller.
  schema_version: 0.1.0
  model_version: 0.1.0
  language: sv
  default_view_profile: system_overview
```

### `schema_version`

Version av projektformat/metamodellschema som projektet förväntar sig.

### `model_version`

Projektets egen modellversion. Den ska kunna ändras oberoende av System Modeller-GPT:ns versionsnummer.

### `language`

Standardspråk för mänskligt läsbara namn och beskrivningar. En enkel BCP47-liknande kod används, exempelvis `sv` eller `en-GB`.

### `default_view_profile`

Frivillig referens till den vyprofil som senare ska användas som standard.

## Shards och global identitet

Projektet använder **shards**, inte en fil per objekt och inte heller en enda gigantisk YAML-fil.

Regler:

1. stabila ID:n är globala inom hela projektet,
2. ett ID får inte förekomma som två olika objekt i olika shards,
3. referenser får gå mellan filer,
4. filplacering ändrar inte modellsemantik,
5. namnbyte eller flytt mellan shards får inte byta stabilt ID,
6. en modell ska kunna läsas som en sammanfogad logisk helhet.

## Obligatoriskt kontra valfritt

För MVP:n är endast `project.yaml` och `model/` principiellt obligatoriska. De rekommenderade modellfilerna skapas av projektmallen för att ge förutsägbar struktur, men tomma eller irrelevanta shards får utelämnas i importerade projekt.

Övriga kataloger är valfria på formatnivå men skapas i standardmallen eftersom de behövs i det fulla Plan A-flödet.

## Portabilitet och ZIP-säkerhet

ZIP:en får inte innehålla:

- absoluta sökvägar,
- `..`-traversering,
- editor-temporärfiler,
- `.DS_Store`,
- `__pycache__`,
- genererade cachekataloger.

Ett systemprojekt ska kunna packas upp på en ny maskin utan beroende till ursprungliga absoluta sökvägar.

## Separation från GPT-paketet

Följande ska **inte** läggas i systemprojektet:

- System Modellers egna instruktioner,
- GPT:ns metamodelldefinitioner,
- schemas som tillhör GPT-versionen,
- GPT:ns regressionstester,
- release/build-scripts för GPT-paketet.

Det gör att samma systemprojekt kan öppnas av en senare kompatibel version av System Modeller utan att verktyget dupliceras i varje modellprojekt.
