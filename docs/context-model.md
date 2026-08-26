# Kontextmodell – System, ExternalSystem och Actor

Detta dokument är normativt för Plan A steg A5.

## 1. Syfte

Kontextmodellen beskriver systemets gräns och de viktigaste aktörerna och externa systemen runt den. Den ska ge underlag för en framtida **System Context View** utan att blanda in intern komponent- eller kodstruktur.

## 2. System

`System` är det system som systemprojektet beskriver. I MVP:n ska ett systemprojekt ha exakt ett primärt `System`-element.

Använd `System` för helheten som en läsare ska kunna förstå som en sammanhållen produkt eller lösning. Interna delar modelleras senare som `Subsystem`, `Component` och `Service`.

Typiska fält utöver A4-basen är:

- `purpose` – varför systemet finns,
- `scope` – vad som ingår i systemgränsen,
- `ownership` – valfri organisatorisk ägare.

`System` ligger på abstraktionsnivån `conceptual` och använder prefixet `SYS`.

## 3. ExternalSystem

`ExternalSystem` representerar ett system eller en extern teknisk tjänst **utanför systemgränsen** som det modellerade systemet samverkar med.

Exempel:

- betalningsplattform,
- identitetsleverantör,
- extern myndighetstjänst,
- separat affärssystem.

Ett system ska inte modelleras som `ExternalSystem` enbart därför att det ligger i ett annat repository eller körs i en annan runtime. Systemgränsen avgör.

`ExternalSystem` ligger på `conceptual` nivå och använder prefixet `EXT`.

## 4. Actor

`Actor` representerar en människa, roll, organisation eller i undantagsfall en extern teknisk aktör som har en meningsfull interaktion med systemet.

Tillåtna `actor_kind` i MVP:n:

- `person`,
- `role`,
- `organization`,
- `external_technical_actor`.

Föredra `role` framför en namngiven individ när arkitekturen beskriver en användarroll, exempelvis `Handläggare` eller `Kund`.

Interna komponenter, klasser, batchjobb och API-klienter ska inte modelleras som Actor.

En extern teknisk lösning som har egen systemidentitet bör normalt modelleras som `ExternalSystem`, inte dubbleras som `Actor`. `external_technical_actor` används när aktörsbegreppet tillför ett meningsfullt användnings-/use-case-perspektiv som inte bör blandas ihop med ett fullständigt externt system.

`Actor` ligger på `conceptual` nivå och använder prefixet `ACT`.

## 5. Relationer i A5

### `uses`

Tillåten riktning:

```text
Actor → System
```

Används när en aktör använder systemet.

### `interacts_with`

Tillåtna riktningar:

```text
Actor → System
System → ExternalSystem
ExternalSystem → System
```

Används när mer specifik semantik ännu inte finns eller inte behövs.

### `exchanges_information_with`

Tillåtna riktningar:

```text
System → ExternalSystem
ExternalSystem → System
```

Används när den viktiga arkitekturella betydelsen är att information utbyts över systemgränsen. Vilken information som utbyts modelleras mer precist i senare steg.

## 6. Systemgränsen styr klassificeringen

Före klassificering ska GPT:n fråga sig:

1. Är detta själva systemet som projektet beskriver? → `System`.
2. Är det utanför systemgränsen och interagerar med systemet? → normalt `ExternalSystem`.
3. Är det en människa, roll eller organisation som använder eller interagerar med systemet? → `Actor`.
4. Är det intern struktur? → vänta på lämplig intern typ i senare steg.

## 7. Undvik dubbletter

Samma externa betalningsplattform ska exempelvis inte bli både:

```text
Actor: Payment Provider
ExternalSystem: Payment Provider
```

utan särskilt skäl. Modellen ska beskriva arkitekturell innebörd, inte skapa ett UML-liknande actorobjekt för varje teknisk integration.

## 8. MVP-begränsningar

A5 beskriver endast kontexten. Detaljer om:

- use cases,
- informationsobjekt,
- API:er,
- interna komponenter,
- runtime och deployment

introduceras i senare Plan A-steg.
