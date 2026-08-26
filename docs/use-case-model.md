# Use-case-modell

Detta dokument är normativt för **Plan A steg A7**.

## Syfte

`UseCase` beskriver ett **sammanhängande beteende av värde för en aktör**. Det ska hjälpa en läsare att förstå vad en användare eller annan aktör försöker uppnå med systemet utan att behöva känna till UI, API:er eller implementation.

Bra exempel:

- Registrera order
- Avbryt order
- Visa orderstatus
- Registrera betalning

Mindre bra exempel:

- Klicka på Spara
- `POST /orders`
- Anropa `OrderService.create()`
- Visa komponenten `OrderForm`

## Avgränsning

Ett use case ska normalt:

- ha ett tydligt mål eller resultat för en aktör,
- kunna beskrivas utan implementationstermer,
- vara finare än ett `Responsibility`,
- vara grövre än en enskild UI-händelse eller teknisk operation,
- vara relevant för systemförståelse.

```text
Orderhantering                 Responsibility
  ├── Registrera order         UseCase
  ├── Ändra order              UseCase
  ├── Avbryt order             UseCase
  └── Visa orderstatus         UseCase
```

## Obligatoriska referenser

I MVP:n har varje `UseCase`:

- exakt en `primary_actor`,
- exakt ett `responsibility`,
- ett `outcome`.

Exempel:

```yaml
- id: UC-000001
  type: UseCase
  name: Registrera order
  abstraction_level: conceptual
  primary_actor: ACT-000001
  responsibility: RSP-000001
  trigger: Kunden väljer att slutföra sin beställning.
  outcome: En order har registrerats.
```

`supporting_actors`, `trigger`, `preconditions` och `postconditions` är valfria. De ska bara modelleras när de bidrar till förståelse; Plan A kräver inte fullständiga use-case-specifikationer med alla alternativa flöden.

## Relation till Actor

Den primära aktören är den aktör vars mål use caset i första hand uppfyller.

```text
Kund ──performs──> Registrera order
```

`primary_actor` är den kanoniska referensen i UseCase-objektet. `performs` är den navigerbara relation som kan materialiseras för vyer och frågor. När båda finns ska de uttrycka samma modellpåstående.

Stödjande aktörer kan anges i `supporting_actors` och kan också få `performs`-relationer när detta är användbart i en vy.

## Relation till Responsibility

`Responsibility` är grövre än `UseCase`.

```text
Orderhantering ──groups_use_case──> Registrera order
```

`responsibility` är den kanoniska referensen i UseCase-objektet. `groups_use_case` är motsvarande navigerbara relation.

## Include och extend

A7 stöder UML-liknande relationer:

- `includes`
- `extends`
- `specializes`

De är **valfria**. De ska inte användas enbart för att skapa ett mer UML-likt diagram. Om relationen inte tillför systemförståelse är det bättre att låta use casen stå självständigt.

## Information och realisering

Fälten `related_information` och `realized_by` finns redan i UseCase-formatet för att modellen ska kunna växa utan formatbyte.

- full typvalidering av `related_information` införs när `InformationObject` kommer i A8,
- full typvalidering av `realized_by` införs när `Component` och `Service` kommer i A10.

Fram till dess ska dessa fält användas sparsamt och bara med stabila ID-referenser.

## Trigger och outcome

`trigger` beskriver vad som sätter use caset i gång.

`outcome` beskriver det meningsfulla resultatet när use caset lyckas.

Exempel:

```text
Trigger: Kunden väljer att slutföra sin beställning.
Outcome: En order har registrerats och kan behandlas vidare.
```

Outcome ska inte vara ett tekniskt resultat som `HTTP 201 returneras` om use caset kan uttryckas mer begripligt.

## Pre- och postconditions

Dessa är valfria listor.

```yaml
preconditions:
  - Kunden är identifierad.
postconditions:
  - Ordern finns registrerad.
  - Ordern har ett unikt ordernummer.
```

De bör inte användas för att skriva en komplett kravspecifikation i modellen.

## Viktiga antimönster

```text
Endpoint = UseCase             ✗
Knapptryckning = UseCase       ✗
Service-metod = UseCase        ✗
Responsibility = UseCase       ✗
```

En endpoint, knapp eller metod kan vara evidens för att ett use case existerar, men är inte automatiskt use caset i sig.

## Designbeslut i A7

1. `UseCase` ligger på `conceptual` nivå.
2. Use cases optimeras för systemförståelse, inte full UML-use-case-formalism.
3. `primary_actor`, `responsibility` och `outcome` är obligatoriska i MVP:n.
4. `performs` och `groups_use_case` införs som navigerbara förstaklassrelationer.
5. `includes`, `extends` och `specializes` stöds men är valfria.
6. Information och teknisk realisering får refereras framåt, men typvalideras först i senare steg.
