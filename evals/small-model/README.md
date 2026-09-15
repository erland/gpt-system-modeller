# Small-model robustness evals

Dessa evals hör till Plan B steg B1 och mäter runtime-robusthet för modeller med begränsad planerings-, kontext- eller instruktionsförmåga.

De är avsiktligt modellneutrala. De ska kunna användas mot exempelvis mindre lokala modeller, Qwen-varianter eller andra enklare chattmodeller utan att testdefinitionen behöver ändras.

## Vad som mäts

- ordningsdisciplin i runtime-flödet,
- validering före mutation,
- återanvändning av stabila ID:n och undvikande av dubbletter,
- korrekt hantering av origin/evidence/osäkerhet,
- begränsning till relevant arbetskontext,
- användning av deterministiska verktyg när sådana finns.

## Vad som inte mäts i B1

B1 försöker inte avgöra om en modell är generellt "smart" eller om dess arkitekturförslag är optimala. Fokus är om den följer System Modellers runtime-kontrakt tillräckligt för att kunna arbeta säkert och reproducerbart.

## Tolkning

Varje YAML-fil beskriver ett scenario med `required` och `forbidden` beteenden. Kritiska evals bör passera helt innan en modellprofil betraktas som lämplig för ändringar av kanonisk modell.
