# Diagramkomplexitet

Plan B steg B6 inför deterministisk mätning av materialiserade arkitekturvyer innan rendering.

## Syfte

Mätningen gör rapportgeneratorn oberoende av modellens spontana bedömning av om ett diagram är för stort. Samma materialiserade vy och samma rapportprofil ska alltid ge samma klassificering.

Standardprofilens budgetar finns i `metamodel/report-profiles/standard.yaml`:

- preferred: högst 12 element och 18 relationer,
- hard: högst 20 element och 30 relationer.

## Klassificering

`scripts/diagram_complexity.py` klassificerar varje vy som:

- `within_preferred` – både element och relationer ligger inom preferred-budget,
- `above_preferred` – minst en preferred-budget överskrids men ingen hard-budget,
- `above_hard` – minst en hard-budget överskrids.

När standardprofilens `split_large_views` är aktiverad sätts `split_recommended: true` för både `above_preferred` och `above_hard`. Själva uppdelningen implementeras i B7; B6 ändrar inte rendering eller rapportinnehåll.

## Sekvensdiagram

Sekvensvyer mäts även med:

- antal Interaction,
- antal unika deltagare,
- antal meddelanden.

Dessa mått registreras i B6 för att ge deterministiskt underlag till B8. Standardprofilen använder ännu inte separata participant/message-budgetar.

## Användning

Mät alla vyer som standardprofilen använder:

```bash
python3 scripts/diagram_complexity.py path/to/system-project
```

Mät en eller flera specifika vytyper:

```bash
python3 scripts/diagram_complexity.py path/to/system-project \
  --type logical_component \
  --type integration
```

JSON-output stöds med `--format json`. Resultatet kan även skrivas till fil med `--output`.

## Sanningskälla

Komplexitetsresultatet är en härledd analys av en materialiserad vy. Kanonisk YAML förblir sanningskälla, och rapportprofilen är sanningskälla för diagram-budgetarna.
