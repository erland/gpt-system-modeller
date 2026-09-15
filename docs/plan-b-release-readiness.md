# Plan B – distribution och release readiness

B12 avslutar Plan B genom att verifiera att de funktioner som byggts i B1–B11 faktiskt följer med de två distributionsmålen och kan byggas reproducerbart.

## Distributionsmål

System Modeller har två likvärdiga distributionsmål med olika tekniska begränsningar:

- **Chat-ZIP** innehåller den portabla runtime-miljön med deterministiska scripts, metamodell, schemas, mallar, exempel och relevant dokumentation.
- **Custom GPT** är en genererad projektion med kompakt instruktion och sex Knowledge-filer. Den får inte vara en separat source of truth.

Båda byggs från samma repositoryversion och samma kanoniska modell-/rapportkällor.

## Plan B-innehåll i Chat-ZIP

Chat-ZIP ska minst innehålla runtime för:

- kompakt context summary,
- rapportprofil och profilkatalog,
- diagramkomplexitet,
- deterministisk diagramuppdelning,
- scenario-specifika sekvensdiagram,
- PDF-presentation contract,
- standardrapportens dokumentation och profilgrund.

`metamodel/report-profiles/catalog.yaml` och `standard.yaml` följer med genom hela `metamodel/`-trädet.

## Plan B-innehåll i Custom GPT

Knowledge-filen `04-views-and-architecture-description.md` genereras från samma kanoniska dokumentation som beskriver:

- vyer och arkitekturbeskrivning,
- standardprofilen,
- diagram-budget och split,
- scenario-specifika sekvensdiagram,
- PDF-presentation,
- profilkatalogens framtida `overview`/`standard`/`detailed`-struktur.

Antalet Knowledge-filer förblir sex. B12 utökar alltså innehållet utan att skapa fler Knowledge-slotar.

## Paritet

`templates/custom-gpt-distribution.yaml` deklarerar Plan B-förmågorna i `parity_contract.shared_capabilities`. Custom GPT-manifestet hashar dessutom hela `metamodel/` och `schemas/`, vilket inkluderar rapportprofilkatalogen och standardprofilen.

Paritet betyder funktionell gemensam grund, inte identiska ZIP-filer. Chat kan köra scripts direkt medan Custom GPT använder kompakt instruktion och Knowledge.

## CI-gate

Pull requests kör nu två gates:

1. full repository- och regressionssvit,
2. faktisk build och validering av Chat- och Custom GPT-distributionerna.

Build-gaten kör `scripts/ci_build.py`, validerar ZIP-filerna igen och laddar upp Chat-ZIP, Custom GPT-ZIP och `build-manifest.yaml` som Actions-artifacts. Samma buildväg används på `main`; release-flödet bygger från den publicerade taggen och bifogar artefakterna till GitHub Release.

## Lokal release-readiness

`scripts/release_check.py` gör en deterministisk dubbelbuild och kontrollerar:

- identiska buildresultat,
- Chat/Custom GPT-paritet,
- ZIP-hygien,
- manifest/checksums.

B12-regressionen kör samma kontroll mot utvecklingsversionen och inspekterar även att Plan B:s runtime- och Knowledge-källor finns i de genererade ZIP-filerna.

## Definition of done för Plan B

Plan B är distributionsklar när:

- B1–B12-regressionerna passerar,
- instruction-adherence passerar,
- Chat och Custom GPT byggs på hosted GitHub Actions för PR-head,
- ZIP-validering/paritet passerar,
- inga kända release-/repository-hygiene blockers återstår,
- `STATUS.md`, `VERSION` och `CHANGELOG.md` beskriver den avslutade etappen.

En faktisk release skapas fortfarande separat genom repositoryts normala tag/release-flöde; B12 mergear eller publicerar ingen release automatiskt.
