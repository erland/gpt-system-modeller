# Arkitekturbeskrivning i MVP (A28)

A28 inför den första sammanhängande arkitekturbeskrivningen i System Modeller. Rapporten genereras deterministiskt från projektets kanoniska YAML-modell och de vyregler som infördes i A26–A27.

## Standardstruktur

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

Strukturen är medvetet stabil i MVP:n. Den är en rapportpresentation och förändrar inte metamodellen.

## Generering

```bash
python3 scripts/report.py path/to/system-project \
  --output path/to/system-project/exports/architecture-description.md
```

`--no-diagrams` genererar samma text och tabeller utan Mermaid-block.

## Diagram

Rapporten återanvänder A26/A27-vymotorn. Diagram genereras som Mermaid från den kanoniska modellen. De är härledda presentationer och är aldrig en separat sanningskälla.

Följande vyer kan ingå när det finns relevanta modelelement:

- System Context
- Functional Overview
- Use Case Overview
- Information Overview
- Functional–Information View
- Logical Component View
- Integration View
- Sequence View
- Deployment View

## Narrativ nivå i A28

A28 prioriterar reproducerbarhet. Förklarande text består därför av modellens egna beskrivningar och korta deterministiska sammanfattningar. A29:s LLM-baserade analys får senare använda samma modell och rapportstruktur för rikare semantisk text utan att göra rapporten till sanningskälla.

## Osäkerhet

Kapitlet *Kända osäkerheter* listar bland annat element och relationer som är `inferred`, `unresolved` eller saknar evidensreferens. Detta är en granskningslista, inte ett påstående om att objekten är felaktiga.

## Evidens

Rapporten sammanfattar `Source`, `SourceReference` och `Evidence`. Full provenance ligger fortsatt i YAML-modellen.

## Kvalitetsprincip

Arkitekturbeskrivningen ska hjälpa en ny läsare förstå:

- vad systemet gör,
- vilka som använder det,
- vilken information det hanterar,
- hur det är logiskt uppbyggt,
- hur det integrerar,
- hur viktiga scenarier fungerar,
- var huvuddelarna körs,
- vilka beslut och osäkerheter som är viktiga.

A29 kompletterar detta med enkel LLM-baserad analys av dokumentation och källkod.
