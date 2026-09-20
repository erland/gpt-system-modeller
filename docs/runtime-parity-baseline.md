# Runtime parity baseline

Plan C använder en explicit parity-baseline för att skilja gemensamt beteende från runtime-specifika möjligheter.

Den canonical instruktionen finns fortsatt i `instructions/chat-runtime.md` för bakåtkompatibilitet med befintliga Chat- och Custom GPT-builders, men innehållet är från C2 plattformsneutralt. Chat-specifik bootstrap ligger i `SYSTEM-MODELLER-CHAT.md`.

Paritet mäts i fem dimensioner:

- **behavior** – om runtimen kan följa samma normativa arbetsflöde,
- **capabilities** – om System Modellers deklarerade förmågor är direkt tillgängliga eller kräver fallback,
- **artifacts** – om runtime-distributionen och dess artefaktkontrakt är implementerat,
- **workspace_state** – hur väl runtimen kan läsa, bevara och uppdatera projektets tillstånd,
- **tools** – om deklarerade deterministiska verktyg kan köras direkt.

`gpt-project.yaml` är sanningskälla för baseline-status. `scripts/runtime_parity.py` validerar och renderar samma information deterministiskt.

C2 aktiverar inte Claude eller OpenCode. Deras parity-status beskriver migrationsläget före adaptrarna i C3 respektive C4.

Särskilt viktigt är att tool parity inte fabriceras. Custom GPT och Claude Project saknar lokal script-exekvering och ska därför använda dokumenterad fallback eller stoppa före osäker kanonisk mutation. OpenCode planeras däremot få deklarerade custom tools runt utvalda scripts.
