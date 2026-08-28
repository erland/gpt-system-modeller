# System Modeller – Chat distribution v0.1.0 MVP

Detta paket är avsett att bifogas i en vanlig ChatGPT-konversation och användas som runtime-kontext för **System Modeller**.

## Startinstruktion för LLM

Använd följande precedence:

1. `instructions/chat-runtime.md` är det obligatoriska beteendekontraktet och ska läsas först.
2. `instructions/source-analysis.md` är obligatorisk när källkod eller dokumentation analyseras.
3. `metamodel/` och `schemas/` är normativa för modellens struktur och semantik.
4. Runtime-relevanta filer i `docs/` används som fördjupning när uppgiften kräver dem.
5. `examples/` visar modell- och outputexempel; de är inte beteendeinstruktioner och inte faktakällor för det aktuella systemet.
6. Använd runtime-scripts för deterministiska operationer när det är möjligt.

Kärnflödet ska fungera från runtime-instruktionerna utan att modellen först behöver läsa alla docs, schemas eller examples.

Ett konkret systems projekt-ZIP är separat från detta GPT-paket. Bevara stabila ID:n, evidens och origin vid alla uppdateringar. Modellera för systemförståelse och abstrahera bort koddetaljer om de inte behövs som evidens.

Typisk användning:

> Använd denna ZIP som System Modeller i den här konversationen. Inventera därefter det bifogade systemprojektet/källkodspaketet och fortsätt enligt runtime-instruktionerna.
