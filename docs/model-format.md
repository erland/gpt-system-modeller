# Gemensamt modellformat – Plan A steg A4

Status: **Normativ för A4 och senare Plan A-steg**.

## 1. Syfte

Detta dokument definierar den gemensamma baskonstruktionen för alla modellobjekt och relationer i System Modeller. Domänobjekt som `System`, `Actor`, `UseCase` och `Component` definieras i senare steg ovanpå denna bas.

A4 låser fyra saker:

1. gemensamma fält för modellobjekt,
2. stabila typade ID:n,
3. relationer som förstaklassobjekt,
4. ett formellt basschema som framtida schemas ska återanvända.

A4 låser **inte** den slutliga listan över elementtyper, relationsnamn eller full semantik för `origin` och `evidence`.

## 2. Kanoniskt YAML-mönster

Ett modellobjekt följer i grunden detta mönster:

```yaml
id: CMP-000017
type: Component
name: Order Management
abstraction_level: logical
description: Hanterar orderlivscykeln.
status: active
aliases:
  - Order Service
tags:
  - order
origin:
  - declared
evidence:
  - EVD-000041
metadata:
  owner_team: order-team
```

Endast `id`, `type`, `name` och `abstraction_level` är obligatoriska i den generella basen. En konkret elementtyp kan i senare schema kräva fler fält.

## 3. Gemensamma fält

### `id`

Stabil teknisk identitet. ID:t används i alla korsreferenser och ska bevaras vid namnbyte.

### `type`

Metamodelltypen, exempelvis `Component`. Typnamn skrivs i PascalCase. A4 tillåter ännu framtida typer; respektive senare steg begränsar vilka typer som är giltiga i sitt sammanhang.

### `name`

Människoläsbart namn. Namnet är inte identiteten och behöver inte vara globalt unikt.

### `description`

Kort semantisk beskrivning av vad objektet representerar. Beskrivningen ska uttrycka betydelse/ansvar, inte bara upprepa namnet.

### `abstraction_level`

Ett av:

- `conceptual`
- `logical`
- `runtime`
- `implementation`

Betydelsen definieras i `docs/modeling-principles.md`.

### `status`

Valfri livscykel/statusmarkör. A4 begränsar ännu inte värdemängden.

### `aliases`

Tidigare eller alternativa namn. Alias ska inte användas som primära korsreferenser.

### `tags`

Fria, korta klassificeringsetiketter. Taggar får inte användas som ersättning för modellerad semantik.

### `origin`

Plats reserverad för hur modellpåståendet har uppkommit. Full semantik för declared/observed/inferred införs i A22. Fältet är en lista för att samma objekt senare ska kunna styrkas från flera ursprung.

### `evidence`

Lista med stabila ID-referenser till evidensposter. Själva evidensmodellen definieras i A21.

### `metadata`

Kontrollerad extensionspunkt för icke-kärnsemantisk metadata. Domänbetydelse som behövs för queries, validering eller vyer ska få ett uttryckligt schemafält i stället för att gömmas här.

## 4. Stabil ID-strategi

Format:

```text
PREFIX-000001
```

Regler:

- versalt prefix,
- bindestreck,
- sexsiffrig sekvens,
- ledande nollor,
- ID är immutable efter tilldelning,
- namnbyte ändrar aldrig ID,
- dubbletter får inte återanvända ett befintligt ID,
- referenser ska använda ID, inte namn.

Exempel:

```text
SYS-000001
ACT-000003
UC-000017
INFO-000023
CMP-000044
RUN-000011
REL-000102
```

`metamodel/id-prefixes.yaml` innehåller ett provisoriskt prefixregister för de typer som Plan A förväntas introducera. Ett senare steg får utöka registret men ska undvika att byta prefix på redan skapade objekt.

## 5. Relationer är förstaklassobjekt

En relation lagras explicit och får ett eget stabilt ID:

```yaml
id: REL-000102
type: realizes
source: CMP-000044
target: RSP-000004
abstraction_level: logical
description: Order Management realiserar det funktionella ansvaret.
evidence:
  - EVD-000041
```

Detta gör att en relation själv kan:

- beskrivas,
- spåras till evidens,
- markeras med ursprung/status,
- hittas i queries,
- jämföras och ändras utan att bäddas in i ett annat objekt.

### `source` och `target`

Ska alltid vara stabila ID-referenser. Vilka kombinationer av käll- och måltyper som är tillåtna definieras stegvis när respektive domänrelation införs.

### `type`

Relationsnamn skrivs i `snake_case`, exempelvis:

```text
uses
realizes
contains
reads
exchanges_information_with
```

A4 håller mängden öppen. Senare metamodellsteg definierar tillåtna relationstyper och typkompatibilitet.

## 6. Abstraktionsnivå på relationer

`abstraction_level` är valfritt på en relation. Om det anges ska det beskriva nivån på själva arkitekturpåståendet, inte mekaniskt kopieras från käll- eller målobjektet.

Exempel: en relation mellan en konceptuell `UseCase` och en logisk `Component` kan sakna nivå eller senare klassificeras enligt den relationssemantik som introduceras för use-case-realisering.

## 7. Referensintegritet

Följande principer gäller från A4:

- alla korsreferenser använder ID,
- refererade ID:n ska kunna lösas inom projektets kanoniska modell eller dess definierade referenslager,
- borttagning av objekt får inte lämna brutna relationer,
- namn får ändras utan att relationer påverkas.

Teknisk kontroll av referensintegritet implementeras fullt i A25.

## 8. JSON Schema

`schemas/common.schema.json` är det formella basschemat.

Det innehåller återanvändbara definitioner för:

- `stableId`
- `abstractionLevel`
- `modelElement`
- `relationship`

Framtida schemas ska använda `$ref`/komposition mot dessa definitioner i stället för att duplicera baskonstruktionen.

## 9. Extensionsprincip

När ett senare steg behöver ny semantik ska den i första hand läggas till som ett explicit schemafält eller en konkret elementtyp. `metadata` är avsett för kompletterande metadata och implementation-/verktygsspecifika tillägg som inte ska styra modellens kärnsemantik.

## 10. Kompatibilitetsregel för senare steg

Senare Plan A-steg får:

- lägga till typer,
- lägga till obligatoriska fält för en specifik typ,
- begränsa relationsnamn,
- definiera typkompatibilitet,
- precisera status/origin/evidence.

De bör inte utan migration:

- ändra betydelsen av ett redan tilldelat ID,
- göra namn till identitet,
- bädda in relationer så att deras egna ID/evidens försvinner,
- flytta kärnsemantik till ostrukturerad `metadata`.
