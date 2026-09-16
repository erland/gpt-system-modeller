# Deterministisk arbetskontext (B2)

## Syfte

`scripts/context.py` skapar en kompakt, deterministisk arbetsbild av ett System Modeller-systemprojekt. Den är avsedd som första läsbar kontext för Chat-runtime, särskilt för mindre modeller som annars behöver hålla för mycket projektstruktur och valideringslogik i arbetsminnet.

Arbetskontexten är **inte** en ny sanningskälla. Kanonisk källa är fortsatt `project.yaml` och projektets YAML-shards.

## Körning

```bash
python3 scripts/context.py /path/to/system-project
python3 scripts/context.py /path/to/system-project --format json
python3 scripts/context.py /path/to/system-project --focus Order --focus API
```

`--focus` är repeterbar och begränsar den explicita matchningslistan till element vars ID, typ, namn eller beskrivning innehåller samtliga angivna söktermer. Den förändrar inte projektet.

`--limit` begränsar antalet detaljerade findings och osäkerhetsposter. Summeringar och typantal är alltid kompletta.

## Innehåll

Arbetskontexten innehåller:

- projektmetadata,
- antal element och relationer per typ,
- valideringsstatus och kompakta findings,
- inventering av kanoniska shards,
- osäkerhetssignaler (`inferred`, `unresolved`, saknad evidens),
- enkla kandidatgrupper för dubbletter med samma normaliserade namn och typ,
- valfria fokusmatchningar med filplacering,
- det normativa runtimeflödet `INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`.

## Exit codes

- `0`: projektet är valideringsmässigt giltigt,
- `1`: arbetskontext skapades men projektet har valideringsfel,
- `2`: argument- eller internt körfel.

Det gör att scriptet både kan användas av en LLM-runtime och i shell/CI utan att valideringsfel döljs.

## Designprincip

B2 flyttar deterministisk projektinventering, valideringssammanfattning och enkel relevansfiltrering från LLM-resonemang till kod. Modellen ska fortfarande göra semantiska arkitekturbedömningar, men ska inte behöva rekonstruera grundläggande projektfakta själv.
