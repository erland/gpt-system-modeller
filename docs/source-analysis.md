# Enkel LLM-baserad käll- och dokumentanalys (A29)

## Syfte

A29 gör det möjligt att använda källkod och dokumentation som underlag för System Modeller utan att blanda ihop extraherade implementationstekniska detaljer med arkitekturen.

MVP-flödet är:

```text
Source material
  ↓
Deterministic inventory
  ↓
LLM analysis
  ↓
Observation
  ↓
Evidence
  ↓
Candidate model concept
  ↓
Deduplication / abstraction check
  ↓
Canonical YAML model
```

`analyze.py` är inte en LLM. Scriptet inventerar filer, klassificerar dem grovt och skapar ett reproducerbart analysunderlag. Den semantiska tolkningen görs av GPT/LLM enligt reglerna nedan.

## Underlag i MVP

Analysen ska kunna användas på bland annat:

- README och Markdown/textdokument,
- arkitektur- och systemdokumentation,
- Java, Kotlin, TypeScript, JavaScript, Python och C# på enkel semantisk nivå,
- `pom.xml`, Gradle, `package.json` och liknande buildfiler,
- OpenAPI/Swagger,
- SQL och migrationsfiler,
- Dockerfile och docker-compose,
- Kubernetes YAML,
- vanlig applikationskonfiguration.

A29 lovar inte fullständig statisk analys eller språkparser. Språkspecifika deterministiska extractors kommer i senare planer.

## Arbetsregel för LLM

1. Inventera underlaget med `scripts/analyze.py inventory` när det är praktiskt.
2. Läs relevanta filer, inte bara filnamn.
3. Registrera först **observationer** som beskriver vad källan faktiskt visar.
4. Koppla observationen till så exakta SourceReference-poster som möjligt.
5. Föreslå därefter `candidate_concepts` på conceptual/logical/runtime-nivå när abstraktionen är motiverad.
6. Jämför kandidaten med den befintliga kanoniska modellen innan nytt objekt skapas.
7. Återanvänd befintligt ID när samma koncept redan finns.
8. När en infererad kandidat förs in i modellen ska den få `origin: [inferred]` och evidens som leder tillbaka till observationens källor.
9. Tekniska fakta som förs in på implementation-nivå använder normalt `origin: [observed]`.
10. Kör `validate.py` efter modelländringar.

## Abstraktionsregler

### Kod får inte kopieras till arkitektur

Exempel:

```text
OrderResource
OrderService
OrderValidator
OrderMapper
OrderRepository
OrderEntity
```

kan tillsammans vara evidens för en logisk komponent:

```text
Order Management
```

om filstruktur, beroenden, namn och beteende stödjer den slutsatsen.

### Förbjudna automatiska likställanden

- Class ≠ Component
- Endpoint ≠ UseCase
- DatabaseTable ≠ InformationObject
- Repository ≠ System/Subsystem
- Deploybar enhet ≠ automatiskt logisk Component

### Use-case-inferens i A29

Use cases kan föreslås när flera signaler pekar mot ett sammanhängande aktörsmål, exempelvis dokumentation + UI/API + servicebeteende. Ett ensamt `POST /orders` är inte tillräckligt för att med säkerhet skapa use caset *Registrera order*.

## Observation

En Observation är inte ett kanoniskt arkitekturelement. Exempel:

```yaml
id: OBS-000001
type: Observation
observation_kind: dependency
statement: OrderService depends on OrderRepository.
source_refs: [REF-000012]
confidence: high
subject: OrderService
predicate: depends_on
object: OrderRepository
candidate_concepts:
  - type: Component
    name: Order Management
    abstraction_level: logical
    rationale: Several order-related implementation elements form one cohesive responsibility.
    confidence: medium
    source_refs: [REF-000012]
```

## Kandidater ska inte få modell-ID i förtid

`candidate_concepts` är arbetsförslag. Stabilt `CMP-*`, `UC-*` eller annat modell-ID tilldelas först när kandidaten har:

- jämförts mot befintlig modell,
- bedömts ligga på rätt abstraktionsnivå,
- fått rimligt namn och ansvar,
- fått spårbar evidens.

## Prioritering av filer

Inventeringen markerar arkitekturellt lovande filer. LLM:n bör normalt börja med:

1. README/system-/arkitekturdokument,
2. build-/dependencyfiler,
3. API-specifikationer,
4. deployment/configuration,
5. databasdefinitioner,
6. entry points, controllers/routes och servicegränser,
7. därefter kod på djupet endast där det behövs för att förstå ansvar eller flöde.

## Resultat från analys

Efter A29 ska en analys kunna ge:

- `Source` och `SourceReference`,
- `Observation`,
- `Evidence`,
- kandidatobjekt för Actor, Responsibility, UseCase, InformationObject, Component, Service, API, DataStore, Scenario, RuntimeUnit och DeploymentNode,
- öppna frågor där underlaget inte räcker.

Det är bättre att lämna en osäker kandidat eller öppen fråga än att fylla modellen med falsk precision.

## Vad A29 inte gör

- ingen full Java/TypeScript-parser,
- ingen säker call-graph-analys,
- ingen automatisk merge av alla kandidater,
- ingen avancerad architecture-drift-klassificering,
- ingen komplett reverse-engineering av varje klass/metod.

Dessa hör till senare planer.

## Nästa steg

A30 använder detta analysflöde i ett referensprojekt och ett end-to-end-test och bygger därefter den första Chat-ZIP-distributionen.
