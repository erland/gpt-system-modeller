# Plan B – Runtime robustness and architecture reporting

## Syfte

Plan B vidareutvecklar System Modeller efter MVP med två primära mål:

1. göra Chat-ZIP/runtime mer robust på enklare och mindre modeller,
2. göra arkitekturbeskrivningar och diagram mer enhetliga, reproducerbara och läsbara, särskilt i PDF.

Ett tredje mål är att förbereda stöd för valbar rapportstruktur och detaljnivå utan att exponera detta som användarfunktion innan standardrapporten är stabil.

## Principer

- Deterministiskt först, LLM sist.
- Kanonisk YAML-modell förblir sanningskälla.
- Enklare modeller ska inte behöva återskapa projektstruktur, valideringsstatus eller rapportregler genom implicit resonemang.
- Rapportlayout och diagramkomplexitet ska styras av explicita kontrakt, inte av modellens spontana val.
- Stora vyer ska delas upp i begripliga delvyer i stället för att krympas till oläsliga helhetsbilder.
- Förändringar ska kunna regressionsprovas både mot starkare och enklare modeller.

## Arbetsflöde för Chat-runtime

Målbilden är ett explicit arbetsflöde:

`INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`

Varje steg ska ha ett avgränsat ansvar och, där det är möjligt, stödjas av deterministiska scripts.

## Steg

### B1 – Small-model baseline och evals

Definiera modellneutrala evals som mäter om runtime-kontraktet följs när modellen har begränsad planerings- och kontextförmåga.

Fokus:

- följa arbetsordningen,
- undvika modelländring före validering,
- återanvända stabila ID:n,
- undvika dubbletter,
- skilja observerat/infererat/unresolved,
- arbeta med minsta nödvändiga fil-/modellkontext,
- inte ersätta deterministiska verktyg med fritt resonemang.

Klart när:

- baseline-evals finns i repositoryt,
- varje eval har tydliga required/forbidden-kriterier,
- evalerna är tillräckligt generella för att kunna köras mot flera modellfamiljer.

### B2 – Deterministiskt project/context summary

Inför ett verktyg, preliminärt `scripts/context.py`, som sammanfattar ett systemprojekt till ett kompakt arbetsunderlag.

Minimiinnehåll:

- projektmetadata,
- modelltyper och antal,
- valideringsstatus,
- relevanta shards,
- unresolved/inferred utan verifierad evidens,
- kandidatfiler för aktuell operation.

Målet är att minska behovet av att en LLM själv inventerar hela projektet.

### B3 – Förenklad Chat-runtime

Omstrukturera runtime-instruktionen kring den explicita sekvensen:

`INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`.

Regler ska vara korta, imperativa och lokala. Exempel:

- Ändra aldrig kanonisk modell före validering.
- Skapa inte nytt element om befintligt element har samma innebörd.
- Ändra endast de shards som behövs för aktuell operation.
- Generera vyer och rapporter först efter godkänd validering.

### B4 – Small-model regression suite

Knyt B1-evalerna till en reproducerbar manuell eller automatiserad regressionsprocess för flera modellklasser.

Resultatet ska skilja mellan:

- instruction adherence,
- modellkvalitet,
- provenance/osäkerhet,
- korrekt användning av deterministiska verktyg.

### B5 – Canonical architecture report profile

Flytta presentationsregler för arkitekturbeskrivningen till en deklarativ standardprofil.

Profilen ska initialt vara intern och entydig, exempelvis:

```yaml
architecture_report:
  profile: standard
  sections:
    - purpose
    - system_context
    - functional
    - use_cases
    - information
    - logical
    - integration
    - scenarios
    - deployment
    - decisions
    - uncertainties
    - evidence
  diagrams:
    split_large_views: true
    preferred_max_elements: 12
    hard_max_elements: 20
    preferred_max_relationships: 18
    hard_max_relationships: 30
  narrative:
    style: concise
```

### B6 – Diagram complexity metrics

Inför mätning av diagramkomplexitet innan rendering.

Minst:

- antal element,
- antal relationer,
- antal deltagare och meddelanden för sekvensdiagram.

Rapportgeneratorn ska kunna avgöra när en vy överskrider preferred/hard budget.

### B7 – Automatisk diagramuppdelning

Dela stora vyer i huvudvy + delvyer.

Prioriterade vyer:

- Logical Component,
- Integration,
- Deployment,
- Functional–Information när den blir tät.

Uppdelning ska baseras på modellerade grupperingar/ägarskap/relationer där sådana finns och annars använda deterministiska fallback-regler.

### B8 – Scenario-specifika sekvensdiagram

Generera ett separat sekvensdiagram per relevant Scenario/Interaction i arkitekturbeskrivningen.

Undvik att slå samman orelaterade scenarier till ett enda diagram.

### B9 – PDF presentation contract

Definiera en stabil presentation för PDF-export:

- rubriknivåer,
- sidbrytningar,
- diagramstorlek,
- maximal diagramyta,
- tabellbeteende,
- radbrytning,
- caption/diagramrubriker,
- hantering av delvyer.

PDF-kontraktet ska vara härlett från samma rapportprofil som Markdown-rapporten.

### B10 – End-to-end report regression

Skapa tre referensnivåer:

- litet system,
- medelstort system,
- stort/tätt system.

Verifiera att:

- rapportstrukturen är stabil,
- diagram håller budget,
- stora vyer delas upp,
- sekvensdiagram är scenario-specifika,
- inga kanoniska fakta försvinner genom presentationen.

### B11 – Report profile groundwork

Förbered stöd för framtida variationer som:

- `overview`,
- `standard`,
- `detailed`,
- senare eventuellt målgruppsprofiler.

Detta steg ska inte exponera nya användarval om standardprofilen ännu inte är stabil.

### B12 – Distribution och regression

Uppdatera Chat- och Custom GPT-distributioner, dokumentation, tester och releasekontroller så att Plan B-funktionerna paketeras reproducerbart.

## Avgränsning

Plan B ändrar inte den grundläggande metamodellen om det inte krävs för deterministisk vyuppdelning eller rapportprofilering. Första prioritet är runtime-robusthet och presentation, inte nya arkitekturbegrepp.

## Rekommenderad ordning

B1–B4 genomförs först. Därefter B5–B10. B11 genomförs först när standardrapporten fungerar konsekvent. B12 avslutar etappen.
