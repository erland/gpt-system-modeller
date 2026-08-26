# Origin: declared, observed och inferred

## Syfte

A22 gör `origin` till en normativ och maskinvaliderad dimension på modellobjekt och relationer. Den beskriver **hur ett arkitekturpåstående har uppkommit**. Den ska hållas separat från `Evidence.status`, som beskriver hur påståendet stöds.

## Värden

### `declared`

Använd när påståendet uttryckligen beskriver avsedd eller dokumenterad arkitektur, exempelvis i systemdokumentation, ett ADR, en specifikation eller en av användaren angiven målbild.

### `observed`

Använd när påståendet direkt kan observeras i faktisk implementation eller tekniskt underlag, exempelvis källkod, konfiguration, databasdefinition eller API-specifikation.

### `inferred`

Använd när System Modeller har abstraherat eller härlett ett arkitekturpåstående som inte förekommer direkt i underlaget. Exempel: flera klasser och repositories grupperas till den logiska komponenten `Order Management`. Inferensen ska kunna motiveras genom evidensens `reason`.

### `user_confirmed`

Använd när användaren explicit har bekräftat att modellpåståendet är korrekt. Värdet kan kombineras med exempelvis `declared` eller `inferred`.

### `unresolved`

Använd när ursprunget eller statusen ännu inte kan avgöras tillräckligt säkert. Det bör normalt inte kombineras med andra origin-värden.

## Flera origin-värden

Samma kanoniska modellpåstående kan ha flera ursprung. Det viktigaste fallet är:

```yaml
origin:
  - declared
  - observed
```

Det betyder att samma arkitekturella påstående både finns dokumenterat och kan observeras i implementationen. Det är ett starkt underlag för senare architecture-drift-analys, men A22 inför ännu ingen separat driftklassificering.

## Origin är inte Evidence.status

Exempel:

```yaml
id: CMP-000001
type: Component
name: Order Management
abstraction_level: logical
origin:
  - inferred
evidence:
  - EVD-000003
```

```yaml
id: EVD-000003
status: source_confirmed
confidence: high
source_refs:
  - REF-000014
reason: >-
  Flera sammanhängande orderklasser, REST-resurser och repositories
  bildar ett tydligt gemensamt logiskt ansvar.
```

Här är komponenten **inferred** eftersom själva komponentabstraktionen har härletts, samtidigt som evidensen är **source_confirmed** eftersom slutsatsen bygger på direkt källkod.

## Declared och observed

A22 möjliggör senare jämförelser mellan avsedd och faktisk arkitektur. Exempel:

- `declared` men inte `observed`: dokumenterad lösning som inte har verifierats i implementationen.
- `observed` men inte `declared`: implementation som saknar motsvarande dokumenterat arkitekturpåstående.
- `declared + observed`: dokumentation och implementation stödjer samma modellpåstående.

Dessa är ännu **tolkningsmöjligheter**, inte automatiska driftresultat. Mer avancerad reconciliation och architecture-drift-analys ligger efter MVP:n.

## Regler

1. `origin` används på både modellobjekt och relationer.
2. Ett eller flera origin-värden får anges.
3. `inferred` ska ha spårbar motivering via Evidence när slutsatsen är viktig.
4. `unresolved` bör normalt stå ensamt.
5. Att ett element saknar `origin` är tillåtet under successiv modellering, men viktiga modellpåståenden bör få origin när underlag finns.
6. Origin ska beskriva **det kanoniska modellpåståendet**, inte bara källfilens typ.
