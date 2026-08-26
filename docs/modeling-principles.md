# Modelleringsprinciper – System Modeller Plan A

Detta dokument är normativt för **System Modeller MVP** från och med steg A3. Syftet är att säkerställa att modeller som skapas manuellt, från dokumentation eller från källkod håller en konsekvent abstraktionsnivå och främst stödjer **systemförståelse**.

## 1. Grundregel: modellera det som behöver förstås

System Modeller ska inte försöka avbilda varje teknisk detalj. Ett modellobjekt ska finnas därför att det hjälper en läsare att förstå systemets syfte, beteende, information, struktur, samverkan eller övergripande körmiljö.

Följande prioriteringsordning gäller:

1. begriplighet,
2. korrekt semantik,
3. spårbarhet till evidens,
4. tillräcklig detalj för aktuell fråga,
5. teknisk fullständighet.

Detalj som inte förändrar förståelsen ska normalt stanna i implementations-/evidenslagret.

## 2. Fyra abstraktionsnivåer

Varje förstaklassobjekt ska kunna placeras på en huvudsaklig abstraktionsnivå.

### 2.1 Conceptual

Beskriver systemet på en verksamhets- och förståelsenära nivå.

Typiska koncept:

- System
- ExternalSystem
- Actor
- Responsibility / SystemFunction
- UseCase
- InformationObject
- Scenario

Frågor nivån ska besvara:

- Varför finns systemet?
- Vem använder eller samverkar med det?
- Vad gör systemet?
- Vilken information är central?
- Vilka viktiga scenarier finns?

Conceptual ska normalt vara den första nivån i en arkitekturbeskrivning.

### 2.2 Logical

Beskriver hur systemets ansvar delas upp i stabila lösningsdelar utan att låsa modellen till varje implementationsteknisk detalj.

Typiska koncept:

- Subsystem
- Component
- Service
- Interface / API
- Message / Event
- DataStore

Frågor nivån ska besvara:

- Vilka större delar består systemet av?
- Vilket ansvar har delarna?
- Hur beror delarna på varandra?
- Hur kommunicerar de?
- Var ägs eller lagras information?

### 2.3 Runtime

Beskriver vad som faktiskt körs och var det körs på en övergripande nivå.

Typiska koncept:

- RuntimeUnit
- DeploymentNode
- Environment
- runtime connections

Frågor nivån ska besvara:

- Vilka körande enheter finns?
- Var deployas de?
- Vilka huvudkommunikationsvägar finns?
- Hur skiljer sig exempelvis production från andra miljöer när detta är arkitekturellt relevant?

MVP:n ska inte kräva modellering av varje pod, process, nätverksregel eller instans.

### 2.4 Implementation

Beskriver konkreta tekniska artefakter som huvudsakligen används som evidens och fördjupning.

Typiska koncept:

- Repository
- Module
- Package / Namespace
- Class
- Interface
- Endpoint
- DatabaseTable
- SourceFile

Frågor nivån kan besvara:

- Var i koden implementeras ett logiskt ansvar?
- Vilka filer eller symboler ger evidens för en komponent eller integration?
- Vilka tekniska artefakter ligger bakom en runtime-enhet?

Implementation ska inte automatiskt exponeras i översiktsvyer.

## 3. Regler mellan abstraktionsnivåer

### 3.1 Lägre nivå får ge evidens för högre nivå

Exempel:

```text
OrderResource
OrderService
OrderRepository
       ↓ evidence / implements
Order Management Component
       ↓ realizes
Order Management Responsibility
       ↓ supports
Create Order Use Case
```

### 3.2 Lägre nivå är inte automatiskt samma sak som högre nivå

En Java-klass blir inte automatiskt en Component.

Ett Maven-module blir inte automatiskt ett Subsystem.

En databas-tabell blir inte automatiskt ett InformationObject.

En REST-endpoint blir inte automatiskt ett UseCase.

### 3.3 Abstraktion ska kunna motiveras

När LLM:n grupperar eller abstraherar implementation ska slutsatsen kunna förklaras och senare bära evidens/confidence.

### 3.4 En vy ska normalt hålla en huvudsaklig nivå

Blandade nivåer får användas när relationen mellan nivåer är själva syftet, exempelvis Use Case Realization eller Deployment.

## 4. System

Ett **System** är den huvudsakliga lösning som systemprojektet beskriver, eller en tydligt avgränsad självständig lösning inom scope.

Modellera som System när objektet:

- har ett eget tydligt syfte,
- kan förstås som en helhet av sina användare eller ägare,
- har en meningsfull systemgräns.

Skapa inte ett nytt System bara för att implementationen finns i ett separat repository eller deployas separat.

## 5. ExternalSystem

Ett **ExternalSystem** ligger utanför den modellerade systemgränsen men samverkar med systemet.

Exempel:

- betalningsleverantör,
- folkbokningssystem,
- identitetsleverantör,
- externt SaaS-system.

Ett tekniskt bibliotek eller ramverk är inte ett ExternalSystem.

Om scope ändras så att ett tidigare externt system börjar modelleras internt kan det senare omklassificeras utan att dess identitet behöver tappas.

## 6. Subsystem

Ett **Subsystem** är en större logisk indelning inom ett System.

Använd Subsystem när flera komponenter tillsammans:

- har ett sammanhållet ansvar,
- utgör en tydlig domän eller lösningsdel,
- är meningsfulla att diskutera som grupp.

Undvik Subsystem om det bara speglar:

- en katalog,
- ett repository,
- en namespace-struktur,
- en organisatorisk teamgräns utan arkitekturell betydelse.

## 7. Component

En **Component** är en logisk lösningsdel med ett tydligt sammanhållet ansvar.

En bra Component ska kunna beskrivas med en kort mening av typen:

> Komponenten ansvarar för ...

En Component ska normalt vara stabilare än enskilda klasser och implementationsdetaljer.

Typiska signaler för en Component:

- flera implementationselement arbetar mot samma ansvar,
- en tydlig API- eller servicegräns finns,
- dataägarskap eller ansvar är tydligt avgränsat,
- delen kan förändras relativt självständigt.

Undvik att skapa en Component per controller, repository eller klass om dessa tillsammans realiserar ett gemensamt ansvar.

## 8. Service

En **Service** beskriver en funktion/tjänst som en Component eller ett System erbjuder.

Skillnaden mellan Component och Service är:

- Component = **vilken logisk del som har ansvaret**,
- Service = **vad delen erbjuder andra**.

Exempel:

```text
Component: Order Management
Service: Order Registration Service
API: Order API
```

En deploybar mikrotjänst kan i vissa lösningar motsvara både en logisk Component och en RuntimeUnit, men dessa ska ändå hållas semantiskt separata så att modellen kan hantera andra implementationsformer.

## 9. Module

En **Module** hör i MVP:n främst hemma på implementation-nivån.

Exempel:

- Maven module,
- npm workspace/package,
- .NET project,
- Python package på bygg-/distributionsnivå.

En Module kan implementera en Component, men ska inte automatiskt modelleras som Component.

## 10. Responsibility / SystemFunction

En **Responsibility** beskriver ett större funktionellt ansvar för systemet, utan att säga hur det implementeras.

Exempel:

- Order Management
- Customer Management
- Payment Handling
- Reporting

Responsibility ligger normalt mellan System och UseCase och används för att skapa en stabil funktionell översikt.

Bra responsibilities:

- uttrycks med verksamhetsnära språk,
- grupperar flera relaterade use cases,
- överlever tekniska implementationbyten.

Undvik responsibilities som heter efter ett ramverk, repository eller en teknisk klass.

## 11. UseCase

Ett **UseCase** beskriver ett mål eller resultat av värde som en Actor uppnår genom samverkan med systemet.

### 11.1 Bra avgränsning

Ett use case bör normalt:

- ha en tydlig primär aktör,
- uttrycka ett användar-/aktörsmål,
- ge ett observerbart resultat,
- vara större än ett enskilt UI-klick eller API-anrop,
- vara mindre än ett helt funktionellt område.

Bra exempel:

- Registrera order
- Avbryt order
- Se orderstatus
- Godkänn deklaration

För tekniska exempel kan en extern systemaktör initiera use caset om interaktionen verkligen representerar ett systemmål.

### 11.2 Undvik tekniska use cases

Följande är normalt inte use cases i conceptual-vyn:

- `POST /orders`
- `saveOrder()`
- Validiera JWT-token
- Läs tabell ORDER_T

Dessa kan vara implementation/evidens för ett use case.

### 11.3 Detaljerade flöden är valfria

MVP:n kräver inte fullständig UML-use-case-specifikation. Trigger och outcome är viktigare än att modellera varje alternativflöde.

## 12. Actor

En **Actor** är en extern part som har en roll i relation till systemet.

Typiska aktörer:

- användarroll,
- extern organisation,
- externt system i en roll som deltagare i ett use case.

Skapa normalt inte en Actor för en intern komponent.

En fysisk person kan ha flera Actor-roller; modellen ska beskriva rollen, inte individen.

## 13. InformationObject

Ett **InformationObject** beskriver verksamhetsmässigt eller systemmässigt betydelsefull information som behöver förstås över implementationen.

Bra exempel:

- Order
- Customer
- Declaration
- Payment
- Shipment

### 13.1 InformationObject är inte tabell eller klass

Följande kan ge evidens för InformationObject men är inte automatiskt samma koncept:

```text
OrderEntity.java
ORDER_HEADER
OrderDto
OrderCreatedEventPayload
```

De kan alla representera olika tekniska uttryck för informationsobjektet **Order**.

### 13.2 När ett InformationObject ska skapas

Skapa ett InformationObject när informationen:

- är central för ett eller flera use cases,
- överförs mellan betydande systemdelar,
- har tydligt ägarskap/livscykel,
- behöver förstås i arkitekturbeskrivningen.

Undvik att modellera varje DTO, tabellkolumn eller lokalt variabelobjekt.

## 14. Interface och API

Ett **Interface** är ett logiskt kontrakt eller åtkomstsätt som en del erbjuder.

Ett **API** är en tekniskt mer specifik form av Interface.

Modellera ett API när det är arkitekturellt relevant att förstå:

- vem som tillhandahåller det,
- vem som konsumerar det,
- vilken typ av information som utbyts,
- övergripande protokoll/stil.

Individuella Endpoint-objekt hör i första hand till implementation/evidensnivån om inte en viss endpoint är viktig för en fördjupad vy.

## 15. DataStore

Ett **DataStore** är en logiskt eller fysiskt relevant lagringsresurs.

Exempel:

- Order Database
- Customer Search Index
- Document Storage

Modellera inte varje schema eller tabell som ett separat DataStore om de tillhör samma arkitekturellt sammanhållna lagring.

## 16. Scenario och Interaction

Ett **Scenario** representerar ett viktigt end-to-end-förlopp som hjälper läsaren förstå hur systemet fungerar.

Ett Scenario ska normalt väljas därför att det:

- realiserar ett centralt use case,
- korsar viktiga komponent-/systemgränser,
- visar ett kritiskt integrationsflöde,
- förklarar arkitektur som annars är svår att förstå statiskt.

En **Interaction** beskriver deltagare och ordnade meddelanden för scenariot.

Modellera inte alla möjliga exekveringsvägar i MVP:n; välj representativa huvudflöden.

## 17. RuntimeUnit

En **RuntimeUnit** är en exekverande enhet som är relevant i deploymentbilden.

Exempel:

- Web Frontend
- Order API
- Payment Worker
- Message Broker

RuntimeUnit är inte samma sak som Component:

```text
Component: Order Management
        ↓ realized_as
RuntimeUnit: Order API
```

Flera Components kan realiseras av samma RuntimeUnit och en Component kan i vissa fall realiseras av flera RuntimeUnits.

## 18. DeploymentNode

En **DeploymentNode** beskriver var en RuntimeUnit körs på en nivå som är användbar för arkitekturbeskrivningen.

Exempel:

- User Browser
- OpenShift Production
- Integration VM
- Managed PostgreSQL Service

I MVP:n ska vi undvika att automatiskt skapa noder för varje pod, host eller instans om dessa inte behövs för förståelsen.

## 19. Environment

Ett **Environment** representerar en relevant miljö, exempelvis:

- development
- test
- staging
- production

Modellera miljöskillnader när de påverkar arkitekturen eller behövs för deploymentförståelsen. Duplicera inte hela modellen bara för att samma topologi finns i flera miljöer.

## 20. Hur källkod ska abstraheras

Kodanalys ska följa fyra steg:

```text
Implementation facts
      ↓
Observed clusters
      ↓
Responsibility inference
      ↓
Logical / conceptual model candidates
```

### 20.1 Exempel

Observerat:

```text
OrderResource
OrderService
OrderValidator
OrderMapper
OrderRepository
OrderEntity
```

Möjlig inferens:

```text
Component: Order Management
Responsibility: Order Management
InformationObject: Order
```

Det ska finnas spårbarhet tillbaka till implementationselementen.

### 20.2 Signaler som stödjer gruppering

LLM:n får bland annat använda:

- package/module-sammanhang,
- namn och domänbegrepp,
- dependency structure,
- API-gränser,
- dataägarskap,
- återkommande use-case-beteenden,
- dokumentation,
- deploymentgränser.

Ingen enskild signal ska automatiskt bestämma arkitekturen.

## 21. När två objekt ska slås ihop

Föredra ett gemensamt modellobjekt när två kandidater:

- representerar samma ansvar eller information,
- bara har olika tekniska representationer,
- har olika namn men tydligt samma identitet.

Bevara alias och evidens i stället för att skapa dubbletter.

Skapa separata objekt när de har:

- olika ansvar,
- olika livscykel/ägarskap,
- meningsfull separat systemidentitet,
- olika arkitekturell betydelse.

## 22. När modellen ska vara osäker

LLM:n ska inte tvinga fram en abstraktion när evidensen är svag.

Om det inte går att avgöra om exempelvis två moduler är en eller två Components ska modellen eller arbetsflödet senare kunna markera slutsatsen som `inferred` med lägre confidence eller `unresolved`.

Att synliggöra osäkerhet är bättre än att skapa falsk precision.

## 23. Namngivningsprinciper

### Conceptual

Använd verksamhets-/domänspråk:

```text
Registrera order
Order
Order Management
```

### Logical

Använd ansvarsfokuserade namn:

```text
Order Management
Payment Integration
Customer Search
```

### Runtime

Använd kör-/deploymentnära men begripliga namn:

```text
Order API
Payment Worker
Web Frontend
```

### Implementation

Behåll faktiska tekniska namn:

```text
OrderResource
order-service
se.example.order
```

## 24. Minsta modell för systemförståelse

En modell behöver inte innehålla alla koncept för att vara användbar. För en grundläggande systemöversikt bör GPT:n prioritera att identifiera:

1. System,
2. Actor/ExternalSystem,
3. Responsibility,
4. UseCase,
5. InformationObject,
6. Component,
7. centrala integrationer,
8. minst de viktigaste runtime/deployment-elementen när underlag finns.

## 25. Kontrollfrågor före modellering

För varje föreslaget objekt ska GPT:n kunna resonera utifrån följande frågor:

1. Hjälper objektet en läsare att förstå systemet?
2. Vilken abstraktionsnivå tillhör det?
3. Finns samma koncept redan under annat namn?
4. Är detta arkitektur eller endast implementation/evidens?
5. Vilket ansvar eller vilken information representerar objektet?
6. Vilken evidens stödjer slutsatsen?
7. Kan detaljen lämnas utanför översiktsmodellen utan informationsförlust?

## 26. Regler för arkitekturvyer

### System Context

Primärt conceptual. Visa systemgräns, aktörer, externa system och huvudsakliga utbyten.

### Use Case / Functional

Conceptual. Visa ansvar, aktörer och use cases utan implementationsdetaljer.

### Information

Conceptual/logical. Visa centrala informationsobjekt och relevanta relationer, inte tabellnivå.

### Logical Component

Logical. Visa Subsystem/Component/Service och viktiga beroenden.

### Use Case Realization

Medvetet tvärgående: Actor/UseCase → Responsibility → Component/Service → InformationObject.

### Integration

Logical, med relevanta externa System, Interface/API, Message/Event och InformationObject.

### Sequence

Scenarioorienterad. Använd den högsta deltagarnivå som fortfarande förklarar förloppet; klasser ska endast användas i en uttryckligen implementationsteknisk sekvensvy.

### Deployment

Runtime + relevanta logical-referenser. Visa RuntimeUnit, DeploymentNode, Environment och huvudkommunikation.

## 27. Antimönster

System Modeller ska aktivt undvika:

### 27.1 Klassdiagram som systemarkitektur

Hundratals klasser ger normalt sämre systemförståelse än ett fåtal välmotiverade Components.

### 27.2 Repository = Component

Repositorygränser kan vara evidens men får inte antas vara arkitekturgränser.

### 27.3 Endpoint = UseCase

Flera endpoints kan realisera ett use case; en endpoint kan också bara vara teknisk stödoperation.

### 27.4 Table = InformationObject

Databasdesign och verksamhetsinformation är olika nivåer.

### 27.5 Deploymentdetaljer utan arkitekturvärde

MVP-vyn ska inte fyllas med pods, replicas och intern plattformsdetalj om dessa inte förändrar systemförståelsen.

### 27.6 Inferens presenterad som fakta

LLM-baserade slutsatser ska senare kunna bära origin/evidence/confidence och får inte beskrivas som observerade om de inte är det.

## 28. Beslutsregel vid tvekan

När två modellnivåer är möjliga ska GPT:n välja **den högre abstraktionsnivån som fortfarande bevarar den information som behövs för att förstå systemet**.

Detaljerna ska hellre bevaras som evidens eller implementationsobjekt än visas som huvudarkitektur.

## 29. Konsekvens för kommande metamodell

A3 låser semantiken ovan men inte den fullständiga YAML-strukturen. Från A4 och framåt ska schemas och objektdefinitioner implementera dessa regler.

Särskilt viktigt är att kommande modellformat kan uttrycka relationer mellan nivåer, exempelvis:

```text
UseCase → supported_by / realized_by → Responsibility / Component
Component → realized_as → RuntimeUnit
RuntimeUnit → deployed_on → DeploymentNode
InformationObject → represented_by → Class/Table/API schema
Implementation element → evidence_for → logical/conceptual element
```

Exakta relationstyper fastställs i de steg där respektive koncept införs.
