# Funktionell ansvarsnivå – Responsibility / SystemFunction

Detta dokument är normativt för **Plan A steg A6**.

## Syfte

`Responsibility` beskriver ett **stabilt funktionellt ansvarsområde** hos systemet. Det är den grova nivå som ska hjälpa en läsare att förstå *vad systemet ansvarar för* innan modellen går ned till enskilda use cases eller logiska komponenter.

`SystemFunction` används som ett begripligt synonymbegrepp i text, men den kanoniska modelltypen i YAML är `Responsibility`.

Exempel:

- Kundhantering
- Orderhantering
- Betalning
- Rapportering

## Responsibility är inte implementation

En Responsibility ska inte skapas bara för att koden innehåller en modul, klass eller tjänst med samma namn. Den ska representera ett begripligt ansvar på konceptuell nivå.

```text
OrderController + OrderService + OrderRepository
                    ↓ evidens
              Orderhantering
              Responsibility
```

Det betyder också att följande likställanden är fel som standard:

```text
Responsibility = Component   ✗
Responsibility = Service     ✗
Responsibility = Module      ✗
Responsibility = Package     ✗
```

En senare logisk komponent kan **realisera** ett Responsibility, men objekten är fortfarande separata.

## Relation till System

I A6 införs relationen:

```text
System ──has_responsibility──> Responsibility
```

Exempel:

```text
Ordersystem
  ├── Kundhantering
  ├── Orderhantering
  ├── Betalning
  └── Rapportering
```

I MVP:n hör ett Responsibility till det primära modellerade systemet. Om ett ansvar egentligen ligger hos ett system utanför systemgränsen ska det normalt inte modelleras som ett internt Responsibility.

## Relation till UseCase

UseCase introduceras i A7. Den avsedda relationen är:

```text
Responsibility ──groups_use_case──> UseCase
```

Responsibility är därmed grövre än ett use case.

Exempel:

```text
Orderhantering
  ├── Registrera order
  ├── Ändra order
  ├── Avbryt order
  └── Visa orderstatus
```

Ett Responsibility bör inte skapas för varje liten användarhandling. Om ett tänkt ansvar bara innehåller ett mycket smalt enstaka use case bör man först överväga om ansvaret ligger på för låg abstraktionsnivå.

## Relation till Component

Component introduceras i A10. Den avsedda kopplingen är:

```text
Responsibility ──realized_by──> Component
```

Det gör att modellen senare kan visa:

```text
Vad systemet ansvarar för
        ↓
  Responsibility
        ↓ realized_by
     Component
        ↓
Hur ansvaret realiseras
```

A6 låser bara semantiken för denna framtida koppling. Själva Component-typen och den maskinvaliderbara relationen införs först i A10.

## Namngivning

Namn ska vara begripliga för någon som inte känner implementationen.

Bra exempel:

- Kundhantering
- Orderhantering
- Betalning
- Dokumenthantering
- Rapportering

Mindre bra exempel:

- `OrderService`
- `com.example.order`
- `Module3`
- `POST /orders`

Tekniska namn kan finnas som aliases eller evidens, men de ska inte styra den konceptuella nivån.

## Avgränsning och granularitet

Välj den högsta abstraktionsnivå som fortfarande gör systemets ansvar begripligt.

Ett bra Responsibility:

- är stabilt över mindre implementationstekniska förändringar,
- kan normalt omfatta flera use cases,
- går att beskriva utan att nämna en specifik klass eller produkt,
- är relevant för systemförståelse,
- har en tydlig relation till systemets syfte.

Undvik att skapa ett enda mycket brett ansvar som bara heter exempelvis `Systemfunktioner`. Ansvarsområdena ska samtidigt vara tillräckligt distinkta för att ge struktur åt use-case-vyn.

## YAML-exempel

```yaml
elements:
  - id: SYS-000001
    type: System
    name: Ordersystem
    abstraction_level: conceptual

  - id: RSP-000001
    type: Responsibility
    name: Orderhantering
    description: Hanterar orderns livscykel från registrering till avslut.
    abstraction_level: conceptual

relationships:
  - id: REL-000001
    type: has_responsibility
    source: SYS-000001
    target: RSP-000001
```

## Designbeslut i A6

1. Den kanoniska typen heter `Responsibility`; `SystemFunction` är synonym för människor och dokumentation.
2. Responsibility ligger på `conceptual` nivå.
3. `has_responsibility` är den enda nya maskinvaliderade relationsformen i A6.
4. Relationer till UseCase och Component dokumenteras nu men aktiveras först när dessa typer införs.
5. Responsibility ska beskriva **vad**, inte **hur**.
