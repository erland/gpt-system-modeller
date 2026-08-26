# Logisk systemstruktur – A10

Detta dokument är normativt för `Subsystem`, `Component` och `Service` i System Modeller MVP.

## Syfte

Den logiska modellen ska göra det möjligt att förstå **hur systemets ansvar är organiserade i större arkitekturdelar**, utan att blanda ihop dem med källkod eller fysisk deployment.

## Subsystem

`Subsystem` är en större logisk gruppering inom det modellerade systemet. Ett subsystem används när flera komponenter tillsammans bildar ett stabilt och begripligt område. Det är inte synonymt med repository, namespace, process eller deploymentmiljö.

## Component

`Component` är den viktigaste logiska byggstenen. Den ska ha ett sammanhållet ansvar som är meningsfullt i en arkitekturbeskrivning. En klass, package, repository eller deploybar enhet är **inte automatiskt** en Component.

Exempel på rimliga komponenter är `Order Management`, `Customer Management` och `Payment Integration`.

## Service

`Service` beskriver ett logiskt erbjudande från en komponent. Det kan exempelvis vara `Order Query Service` eller `Payment Service`. En Service är inte automatiskt samma sak som en mikrotjänst, process eller `RuntimeUnit`; runtime införs separat i A17.

## Strukturrelationer

- `contains`: överordnat element → underordnat element.
- `part_of`: underordnat element → överordnat element.
- `depends_on`: source behöver target för sitt logiska ansvar.
- `uses`: source använder target eller dess erbjudande.
- `provides`: `Component → Service`.
- `realized_by`: `Responsibility → Component`.
- `realizes`: alternativ läsriktning `Component → Responsibility`.

`contains`/`part_of` respektive `realized_by`/`realizes` ska normalt inte lagras dubbelt för samma faktum.

## Koppling mellan konceptuell och logisk nivå

Den viktigaste bryggan är:

```text
Responsibility (conceptual)
        │ realized_by
        ▼
Component (logical)
        │ provides
        ▼
Service (logical)
```

Det gör att systemets funktionella ansvar kan beskrivas oberoende av den logiska lösningen, men fortfarande spåras till hur de realiseras.

## Informationsanvändning

Från A10 får `Component` och `Service` vara source i de informationsrelationer som infördes i A9, exempelvis `reads_information`, `updates_information` och `creates_information`.

Det gör att en senare vy kan visa både funktionellt ansvar och vilken information den logiska arkitekturen hanterar.

## Abstraktionsregel

Välj den minsta mängd Subsystem, Component och Service som behövs för att förstå systemet. Reverse engineering får gärna observera hundratals implementationselement, men A10-modellen ska sammanfatta dem till ett mindre antal arkitekturmässigt meningsfulla delar.

## Antimönster

Undvik särskilt:

- `Class = Component`
- `Package = Subsystem`
- `Repository = Component`
- `Microservice process = Service` utan semantisk analys
- att modellera både `contains` och `part_of` för samma par
- att modellera både `realized_by` och `realizes` för samma faktum
