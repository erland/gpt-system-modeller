# Source, SourceReference och Evidence

Status: **normativ för Plan A från steg A21**.

## Syfte

System Modeller ska kunna förklara **varför** ett modellpåstående finns. Därför hålls provenance i ett separat lager i stället för att källkod och dokumentation görs till arkitekturelement.

Spårbarhetskedjan är:

```text
Model element / Relationship
          │ evidence: EVD-*
          v
       Evidence
          │ source_refs: REF-*
          v
   SourceReference
          │ source: SRC-*
          v
        Source
```

## Source

`Source` representerar ett identifierbart underlag. Tillåtna MVP-typer är:

- `source_code`
- `documentation`
- `user_statement`
- `api_specification`
- `database_schema`
- `configuration`
- `other`

En Source kan ange `location` och `revision`. För ett Git-repository bör revision i första hand vara commit-ID eller annan reproducerbar revision.

## SourceReference

`SourceReference` pekar in i en Source och ska vara så exakt som möjligt.

För kod används i första hand:

- `file`
- `symbol`
- `start_line` / `end_line`

För dokument används i första hand:

- `file`
- `page`
- `section`
- vid behov `paragraph` eller fri `locator`

## Evidence

`Evidence` beskriver stödet bakom ett modellpåstående.

Statusvärden:

- `source_confirmed` – uttryckligt stöd i en källa
- `user_confirmed` – uttryckligen bekräftat av användaren
- `inferred` – härlett från ett eller flera underlag
- `assumed` – antagande med otillräckligt underlag
- `unresolved` – oklart eller motstridigt underlag

Confidence:

- `high`
- `medium`
- `low`
- `unknown`

`inferred` och `assumed` ska ha `reason`.

## Koppling till modellen

Alla arkitekturelement och relationer kan använda det gemensamma fältet:

```yaml
evidence:
  - EVD-000001
```

Evidensposten lagras separat, exempelvis:

```yaml
evidence:
  - id: EVD-000001
    status: source_confirmed
    confidence: high
    source_refs:
      - REF-000001
```

Detta gör att samma evidens kan återanvändas av flera modellpåståenden utan att källdata dupliceras.

## Kodexempel

```yaml
sources:
  - id: SRC-000001
    source_kind: source_code
    name: Order backend
    location: backend/
    revision: 1a2b3c4d

source_references:
  - id: REF-000001
    source: SRC-000001
    file: src/main/java/example/OrderService.java
    symbol: OrderService.createOrder
    start_line: 42
    end_line: 71
```

## Dokumentexempel

```yaml
sources:
  - id: SRC-000002
    source_kind: documentation
    name: Systembeskrivning
    location: docs/systembeskrivning.pdf

source_references:
  - id: REF-000002
    source: SRC-000002
    page: 12
    section: Orderhantering
```

## Viktig gräns mot A22

`Evidence.status` beskriver **hur väl ett påstående stöds**. Det beskriver inte om arkitekturen är avsedd/dokumenterad eller faktiskt observerad. `declared`, `observed` och `inferred` som arkitekturursprung hanteras separat i A22.
