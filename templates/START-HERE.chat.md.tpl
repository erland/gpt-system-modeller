# {{GPT_NAME}} – Chat ZIP

Den här ZIP-filen är den portabla Chat-runtime-distributionen för **{{GPT_NAME}}**.

## Användning

Bifoga ZIP-filen i en ChatGPT-konversation och ange att den ska användas som GPT-kontext i konversationen.

## Viktiga delar

- `assistant/instructions.md` – runtimeinstruktion
- `assistant/runtime-contract.json` – kompilerad snapshot av canonical capability-, artifact-, workspace/state- och tool-kontrakt
- `assistant/policies/` – runtimepolicies
- `knowledge/` – referensmaterial
- `schemas/` – runtime-scheman när de finns
- `scripts/` – endast explicit deklarerade runtimeverktyg och nödvändigt delat stöd
- `templates/` – runtime-mallar när de finns

## Version

{{VERSION}}

## Entry point

Detta dokument är den mänskliga entrypointen. Runtime-manifestet beskriver den maskinläsbara strukturen.
