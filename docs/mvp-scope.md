# MVP-målbild och scope – System Modeller Plan A

## 1. Syfte

System Modeller är ett LLM-baserat verktygs- och GPT-paket för att bygga, förvalta, analysera och presentera en spårbar modell av hur ett system fungerar och är uppbyggt.

Plan A ska leverera en första verkligt testbar MVP. Den ska vara tillräckligt komplett för att kunna användas på ett mindre eller medelstort verkligt system och svara på den centrala frågan:

> Kan System Modeller skapa en modell på tillräckligt bra abstraktionsnivå för att en person som inte känner systemet ska förstå vad systemet gör, vilken information det hanterar, hur det är uppbyggt, hur delarna samverkar och hur det övergripande deployas?

MVP:n ska prioritera begriplighet och spårbarhet framför fullständig UML-täckning och maximal implementationsdetalj.

## 2. Primära målgrupper

MVP:n ska i första hand stödja:

- lösnings- och systemarkitekter,
- enterprise architects som behöver förstå ett system på lösningsnivå,
- utvecklare och tekniska leads som behöver skapa eller verifiera en arkitekturbeskrivning,
- förvaltning och systemansvariga som behöver en sammanhållen systembild,
- nya teammedlemmar som behöver onboarding och systemförståelse,
- granskare som behöver kunna följa arkitekturpåståenden tillbaka till dokumentation eller implementation.

Olika målgrupper ska kunna använda samma kanoniska modell men få olika vyer och detaljnivåer. Den fullständiga mekanismen för vyprofiler byggs senare i Plan A.

## 3. Primära användningsfall

### 3.1 Skapa en modell via dialog

Användaren ska kunna beskriva systemets funktion, information och struktur i naturligt språk och få detta infört i en YAML-baserad systemmodell.

Exempel:

- Lägg till use caset Registrera order.
- Order Management ansvarar för Order.
- Payment Service anropas via ett REST-API.
- Backend körs på OpenShift i produktionsmiljön.

### 3.2 Fortsätta arbeta på en befintlig modell

Ett systemprojekt ska kunna bifogas som ZIP, läsas, ändras, valideras och returneras som en ny komplett ZIP.

### 3.3 Skapa modellunderlag från dokumentation

LLM:n ska i MVP:n kunna analysera dokumentation semantiskt och föreslå exempelvis:

- systemets syfte,
- aktörer,
- ansvar,
- use cases,
- informationsobjekt,
- komponenter,
- integrationer,
- runtime/deployment,
- arkitekturbeslut och constraints.

### 3.4 Skapa modellunderlag från källkod och tekniska artefakter

MVP:n ska kunna använda LLM-baserad analys av källkod och konfiguration som underlag. Fokus är inte fullständig statisk kodanalys, utan att identifiera tillräckligt med evidens för en begriplig systemmodell.

Exempel på underlag:

- Java och TypeScript/JavaScript,
- README och projektstruktur,
- OpenAPI,
- SQL,
- Docker/docker-compose,
- enklare Kubernetes- och konfigurationsfiler.

Språkspecifika deterministiska extractors hör huvudsakligen till senare planer.

### 3.5 Fråga och analysera modellen

MVP:n ska kunna besvara centrala systemförståelsefrågor, exempelvis:

- Vad gör systemet?
- Vilka aktörer och use cases finns?
- Vilken information hanteras?
- Vilka komponenter realiserar ett use case?
- Vilka externa system integrerar systemet med?
- Hur kommunicerar huvuddelarna?
- Vilka runtime-enheter finns och var deployas de?
- Vilka delar av modellen är observerade, dokumenterade eller infererade?

### 3.6 Generera arkitekturvyer

Plan A ska som mål kunna generera minst:

1. System Context View
2. Functional Overview
3. Use Case Overview
4. Information Overview
5. Functional–Information View
6. Logical Component View
7. Use Case Realization View
8. Integration View
9. Sequence View
10. Deployment View

### 3.7 Generera en samlad arkitekturbeskrivning

MVP:n ska kunna generera en första sammanhållen arkitekturbeskrivning i Markdown baserat på modellen och dess vyer.

## 4. Informationsbehov som MVP:n ska kunna besvara

Modellen ska i slutet av Plan A ge tillräckligt underlag för följande perspektiv.

### 4.1 Varför och i vilket sammanhang?

- systemets syfte och omfattning,
- vilka aktörer som använder systemet,
- vilka externa system som omger det,
- centrala arkitekturbeslut och constraints.

### 4.2 Vad gör systemet?

- funktionella ansvarsområden,
- use cases,
- koppling mellan aktörer och use cases.

### 4.3 Vilken information hanteras?

- centrala informationsobjekt,
- informationsrelationer,
- vem som skapar, läser, uppdaterar, äger eller lagrar information.

### 4.4 Hur är systemet logiskt uppbyggt?

- subsystem,
- komponenter,
- tjänster,
- interfaces/API:er,
- data stores,
- huvudberoenden.

### 4.5 Hur samverkar delarna?

- integrationer,
- API-anrop,
- meddelanden/events,
- centrala scenarier och sekvenser.

### 4.6 Hur körs och deployas systemet övergripande?

- runtime-enheter,
- deployment nodes,
- environments,
- centrala kommunikationsvägar.

MVP:n ska visa en arkitekturellt användbar översikt, inte nödvändigtvis varje pod, process, server eller nätverksregel.

## 5. In-scope för Plan A

### 5.1 Kärnkoncept

Plan A ska successivt etablera stöd för:

- System
- ExternalSystem
- Actor
- Responsibility / SystemFunction
- UseCase
- InformationObject
- Subsystem
- Component
- Service
- Interface / API
- Message / Event
- DataStore
- Scenario
- Interaction
- InteractionMessage
- RuntimeUnit
- DeploymentNode
- Environment
- ArchitectureDecision
- Constraint
- Source
- SourceReference
- Evidence
- Relationship

### 5.2 Grundläggande implementations- och evidenslager

För att kunna analysera källkod ska MVP:n åtminstone kunna representera underlag som:

- Repository
- Module
- Package / Namespace
- Class
- Interface
- Endpoint
- DatabaseTable
- SourceFile
- Observation

Detta lager ska främst fungera som evidens och spårbarhet. Det ska inte automatiskt styra den logiska arkitekturens detaljnivå.

### 5.3 Ursprung och säkerhet i slutsatser

Modellen ska kunna skilja mellan åtminstone:

- declared – dokumenterad eller avsedd arkitektur,
- observed – observerad i implementation eller tekniskt underlag,
- inferred – semantiskt härledd slutsats,
- user_confirmed – uttryckligen bekräftad av användaren,
- unresolved – ännu inte tillräckligt fastställd.

Confidence och källreferenser ska kunna associeras med viktiga modellpåståenden.

### 5.4 Projektformat

Plan A ska leverera ett ZIP-baserat systemprojekt med YAML-filer som kan:

- skapas,
- läsas,
- ändras,
- valideras,
- paketeras och returneras.

### 5.5 Diagram och notation

MVP:n ska använda UML-kompatibla eller UML-liknande vyer där det förbättrar förståelsen. Mermaid och PlantUML är prioriterade första renderingsformat.

## 6. Out-of-scope för Plan A

Följande är uttryckligen inte krav för MVP:n:

- fullständig UML 2.x-metamodell eller round-trip engineering,
- stöd för alla UML-diagramtyper,
- fullständig BPMN-modellering,
- avancerade språkspecifika statiska kodextractors,
- komplett dependency graph från varje kodsymbol,
- avancerad merge/reconciliation mellan stora modeller,
- fullständig diff- och migrationsmotor,
- avancerad architecture drift-motor,
- fullständig säkerhets- eller hotmodell,
- fullständig NFR-/quality-modell och quality scenarios,
- avancerad change impact analysis,
- komplett policy/rule engine,
- live GitHub-integrering,
- runtime telemetry eller distribuerade traces,
- SBOM/SCA,
- fullständig draw.io-roundtrip,
- Custom GPT-distribution,
- PDF/DOCX/Confluence-export som kärnkrav.

Dessa får införas i senare planer utan att MVP:n ska behöva designas om fundamentalt.

## 7. Förhållande till UML

System Modeller ska **inte** försöka implementera hela UML-standarden som sin interna metamodel i MVP:n.

I stället gäller:

> Den kanoniska modellen beskriver systemet med semantiskt tydliga systemarkitekturkoncept. UML används där dess notation ger en välkänd och begriplig vy av dessa koncept.

Prioriterade UML-liknande uttryck i Plan A är:

- Use Case Diagram
- Component Diagram
- Sequence Diagram
- Deployment Diagram
- förenklat information/class-like diagram

Package Diagram kan användas senare eller vid behov för implementationsfördjupning.

## 8. Förhållande till C4

C4 är en viktig inspirationskälla för abstraktion och begriplighet, framför allt för:

- System Context,
- system-/containerliknande översikter,
- komponentnivå,
- tydlig målgruppsanpassad detaljnivå.

System Modeller ska däremot inte begränsas till C4. Modellen måste även kunna beskriva use cases, information, integrationer, scenarier, arkitekturbeslut och evidens.

En möjlig framtida C4-export eller C4-profil ska kunna härledas från samma modell.

## 9. Förhållande till klassiska arkitekturvyer

Plan A ska ge underlag för en pragmatisk kombination av klassiska lösningsarkitekturperspektiv och 4+1-liknande scenariotänkande.

### Funktionell/use-case-vy

- Actor
- Responsibility
- UseCase

### Logisk vy

- Subsystem
- Component
- Service
- Interface

### Informationsvy

- InformationObject
- informationsanvändning och relationer

### Integrationsvy

- API
- Message/Event
- ExternalSystem
- informationsutbyten

### Process/runtime-vy

- Scenario
- Interaction
- InteractionMessage

### Deployment-vy

- RuntimeUnit
- DeploymentNode
- Environment
- kommunikationsrelationer

### Scenario som sammanhållande perspektiv

Viktiga scenarier ska kunna knyta samman use case, information, logiska komponenter, integration och runtime utan att duplicera modellen.

## 10. Abstraktionspolicy för MVP:n

Plan A ska använda fyra huvudnivåer:

```text
conceptual
logical
runtime
implementation
```

### Conceptual

Fokuserar på systemförståelse:

- Actor
- UseCase
- Responsibility
- InformationObject
- System/ExternalSystem

### Logical

Fokuserar på lösningens ansvarsfördelning:

- Subsystem
- Component
- Service
- Interface/API
- DataStore

### Runtime

Fokuserar på exekverande arkitektur:

- RuntimeUnit
- DeploymentNode
- Environment
- kommunikationsvägar

### Implementation

Fokuserar på evidens:

- Repository
- Module
- Package
- Class
- Endpoint
- SourceFile
- DatabaseTable

Arkitekturbeskrivningen ska normalt prioritera conceptual, logical och runtime. Implementation visas när den tillför förståelse eller spårbarhet.

## 11. Förväntad arkitekturbeskrivning efter Plan A

En första standardrapport ska kunna innehålla:

1. Syfte och omfattning
2. Systemets sammanhang
3. Funktionell översikt
4. Aktörer och use cases
5. Informationsarkitektur
6. Logisk arkitektur
7. Integrationsarkitektur
8. Viktiga scenarier
9. Runtime och deployment
10. Arkitekturbeslut och constraints
11. Kända osäkerheter
12. Källor och evidens

MVP:n behöver inte generera en fullständig formell arkitekturdokumentation enligt en viss standard. Målet är en sammanhängande, begriplig och spårbar beskrivning.

## 12. Definition of Done för Plan A

Plan A är funktionellt lyckad när ett praktiskt end-to-end-test kan genomföras där:

1. System Modeller Chat-ZIP bifogas i en ny konversation.
2. Ett systemprojekt, dokumentationspaket eller källkodspaket bifogas.
3. GPT:n kan inventera underlaget och skapa eller komplettera en YAML-modell.
4. Modellpåståenden kan bära evidens och tydligt ursprung.
5. Användaren kan korrigera eller komplettera modellen i dialog.
6. Modellen kan valideras.
7. De centrala arkitekturvyerna kan genereras från modellen.
8. En sammanhängande arkitekturbeskrivning kan genereras.
9. Ett komplett uppdaterat systemprojekt kan returneras som ZIP.
10. Resultatet ger en rimlig systemförståelse utan att överväldiga läsaren med implementationsdetaljer.

## 13. Designbeslut låsta av A2

Följande räknas efter A2 som etablerade MVP-beslut, om de inte senare ändras explicit genom ett dokumenterat designbeslut:

1. Systemförståelse är huvudmålet.
2. YAML är kanoniskt modellformat.
3. UML används som vy/notation, inte som intern fullständig metamodel.
4. C4 används som inspirationskälla för abstraktion och kontext, inte som ensam modellstandard.
5. Use cases och informationsobjekt är förstaklasskoncept.
6. Logisk arkitektur ska hållas åtskild från implementation.
7. En övergripande deploymentmodell ingår i MVP:n.
8. Evidens och ursprung ska kunna spåras.
9. Declared, observed och inferred ska kunna särskiljas.
10. En samlad arkitekturbeskrivning är en huvudleverans från modellen.
11. Chat-ZIP och Custom GPT är båda distributionsmål; Chat-ZIP är den portabla runtime som först användes i MVP-testningen.
