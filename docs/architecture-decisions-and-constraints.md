# ArchitectureDecision och Constraint – Plan A steg A20

Status: **Normativ från A20**.

## Syfte

Arkitekturbeskrivningen behöver kunna förklara både **varför arkitekturen ser ut som den gör** och vilka begränsningar den måste följa. A20 inför därför `ArchitectureDecision` och `Constraint` som förstaklassobjekt.

## ArchitectureDecision

`ArchitectureDecision` används för betydelsefulla val där det funnits eller rimligen kunnat finnas alternativa lösningar.

Obligatoriskt i MVP:

- `decision_status`
- `context`
- `decision`
- `rationale`

Valfritt:

- `alternatives`
- `consequences`
- `affected_elements`

Tillåtna statusvärden är `proposed`, `accepted`, `deprecated`, `superseded` och `rejected`.

Exempel på ett relevant beslut är att orderhändelser ska distribueras asynkront för att minska kopplingen mellan Order Management och Payment.

## Constraint

`Constraint` används för en regel eller begränsning som arkitekturen måste respektera. Den kan vara verksamhetsmässig, regulatorisk, organisatorisk, teknisk, säkerhetsmässig eller operationell.

Obligatoriskt:

- `statement`

Valfritt:

- `rationale`
- `affected_elements`
- `constraint_kind`

Exempel:

- Ingen direkt databasåtkomst mellan domäner.
- Produktionssystem ska köras på OpenShift.
- All extern kommunikation ska använda TLS.

## Skillnaden mellan beslut och constraint

Använd `ArchitectureDecision` när arkitekturen **väljer en riktning** och det är relevant att dokumentera motiv och konsekvenser.

Använd `Constraint` när arkitekturen **måste följa en begränsning** som inte bör modelleras som ett fritt lösningsval.

## Abstraktionsnivå

Båda objekten ligger på `conceptual` i MVP:n. De är tvärgående kunskap om arkitekturen och kan påverka objekt på conceptual, logical eller runtime-nivå.

Det betyder inte att ett beslut är "verksamhetsmässigt"; nivån används här för att hålla beslut och constraints separerade från den tekniska realiseringen de påverkar.

## Påverkan på modellen

A20 inför relationen:

```text
ArchitectureDecision | Constraint --affects--> model element
```

`affected_elements` får dessutom användas som en bekväm lista för rapportering. När påverkan behöver egen evidens, metadata eller querybar relation ska `affects` användas.

## Arkitekturbeskrivning

A20 gör det möjligt att generera ett avsnitt som inte bara säger **vad** som finns utan även exempelvis:

> Orderhändelser distribueras asynkront. Beslutet valdes för att minska direkt koppling mellan order- och betalningsdelarna. Konsekvensen är att flödet blir mer resilient men att eventual consistency måste hanteras.

Detta är den detaljnivå System Modeller ska eftersträva i MVP:n.
