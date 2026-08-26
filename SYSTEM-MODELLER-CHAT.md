# System Modeller – Chat distribution v0.1.0 MVP

Detta paket är avsett att bifogas i en vanlig ChatGPT-konversation och användas som runtime-kontext för **System Modeller**.

## Startinstruktion för LLM

1. Läs först `instructions/chat-runtime.md`.
2. Behandla `metamodel/`, `schemas/` och `docs/` som normativa för modellformatet.
3. Använd scripts för deterministiska operationer när det är möjligt.
4. Ett konkret systems projekt-ZIP är separat från detta GPT-paket.
5. Bevara stabila ID:n, evidens och origin vid alla uppdateringar.
6. Modellera för systemförståelse; abstrahera bort koddetaljer om de inte behövs som evidens.

Typisk användning:

> Använd denna ZIP som System Modeller i den här konversationen. Inventera därefter det bifogade systemprojektet/källkodspaketet och fortsätt enligt runtime-instruktionerna.
