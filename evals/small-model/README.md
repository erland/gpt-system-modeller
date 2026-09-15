# Small-model robustness evals

Dessa evals hör till Plan B B1–B4 och mäter runtime-robusthet för modeller med begränsad planerings-, kontext- eller instruktionsförmåga.

De är avsiktligt modellneutrala. De kan användas mot exempelvis mindre lokala modeller, Qwen-varianter eller andra enklare chattmodeller utan att testdefinitionen behöver ändras.

## Fyra kvalitetsdimensioner

`suite.yaml` delar regressionen i:

- `instruction_adherence` – arbetsordning, valideringsgrindar och relevant kontext,
- `model_quality` – semantisk återanvändning, stabila ID:n och dubblettkontroll,
- `provenance_uncertainty` – origin, evidence, inferred och unresolved,
- `deterministic_tools` – korrekt användning av deterministiska scripts och kanonisk YAML som sanningskälla.

## Modellklasser

Resultat märks med en jämförelseklass, inte med leverantörsspecifik logik:

- `small_local`,
- `general_chat`,
- `strong_reasoning`.

Samma evaldefinitioner används för alla klasser. Modellnamn/version anges separat i resultatfilen.

## Reproducerbar regressionsprocess

1. Kör varje scenario i `suite.yaml` mot den modell/runtime som ska utvärderas.
2. Bedöm varje `required`-punkt som `true` endast om beteendet uppfylldes.
3. Bedöm varje `forbidden`-punkt som `true` endast om det förbjudna beteendet faktiskt observerades.
4. Spara bedömningen i formatet `system-modeller-small-model-result-v1`.
5. Kör den deterministiska poängsättaren:

```bash
python3 scripts/evaluate_small_model.py --results result.yaml
```

Maskinläsbar sammanfattning:

```bash
python3 scripts/evaluate_small_model.py --results result.yaml --format yaml
```

Validera endast suite-definitionen:

```bash
python3 scripts/evaluate_small_model.py
```

Poängsättaren gör inte en ny LLM-bedömning av fri text. Den validerar den registrerade rubrikbedömningen och räknar deterministiskt case-, dimensions- och totalresultat. En framtida extern testharness får automatisera själva rubric-judgment-steget utan att ändra suite-kontraktet.

## Säkerhetsgrind

Critical cases måste passera helt. Om ett critical case faller blir `canonical_mutation_allowed: false` även om andra dimensioner passerar. Det gör att regressionsresultatet uttryckligen skiljer mellan en modell som kan användas för läsning/analys och en modell som är säker nog för ändringar av kanonisk modell.

## Referensfixtures

- `tests/fixtures/small-model-pass.yaml` visar en fullständigt godkänd körning.
- `tests/fixtures/small-model-critical-fail.yaml` visar att ett kritiskt runtimefel blockerar kanonisk mutation utan att dölja resultaten för övriga dimensioner.

## Avgränsning

Regressionen avgör inte om en modell är generellt "smart" eller om dess arkitekturförslag är optimala. Fokus är om den följer System Modellers runtime-kontrakt tillräckligt säkert och reproducerbart. Semantisk arkitekturkvalitet mäts i B4 endast genom de uttryckliga B1-rubrikerna, inte genom subjektiv helhetsbedömning.
