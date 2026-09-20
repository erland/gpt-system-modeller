# Plan C – Multi-runtime distributions

## Syfte

Migrera System Modeller från den nuvarande två-runtime-strukturen (Chat ZIP + Custom GPT) till ett canonical GPT-projekt som kan bygga och validera fyra jämbördiga distributioner:

- Chat ZIP
- Custom GPT
- Claude Project
- OpenCode workspace

Migrationen ska bevara System Modellers nuvarande domänbeteende, modellformat, deterministiska verktyg och Plan B-rapportering. Runtime-specifika paket ska vara genererade projektioner av samma canonical kontrakt och får inte bli separata sources of truth.

## Utgångsläge

Projektet har redan en stabil canonical domänmodell i `metamodel/` och `schemas/`, runtimeinstruktioner i `instructions/chat-runtime.md`, deterministiska scripts, Chat- och Custom GPT-builders, gemensam versionering, regressionstester samt GitHub Actions för build, validering och release.

Projektet saknar däremot den projekt- och runtime-kontraktsmodell som krävs för den nya fler-runtime-arkitekturen:

- `gpt-project.yaml`
- `project-status.yaml`
- explicit platform-neutral capability contract
- explicit artifact contract
- explicit workspace/state contract
- explicit tool contract
- generell runtime-paritetsrapport
- Claude Project-adapter
- OpenCode workspace-adapter

## Migrationsprinciper

1. Bevara domänbeteende och canonical modellsemantik.
2. Gör `instructions/chat-runtime.md` platform-neutral innan den används som canonical instruktion; Chat-specifika bootstrapdetaljer flyttas till Chat-adaptern.
3. Registrera endast scripts som runtimeverktyg när de uttryckligen behövs i assistentens kärnflöde.
4. OpenCode får genererad `AGENTS.md`, `.opencode/runtime-contract.json`, deklarerade custom tools och vid behov projektlokala skills.
5. Claude Project får genererade Project Instructions, Project Knowledge och `project/runtime-contract.json`; lokala scripts betraktas som reducerad funktion eftersom Claude Projects inte kör dem lokalt.
6. En runtime aktiveras först när compatibility är `ready` och relevanta valideringar passerar.
7. Release-taggen fortsätter vara auktoritativ versionskälla för releaseartefakter.
8. CI och release ska bygga och validera alla aktiverade runtimes från samma commit.

## Steg

### C1 – Canonical project contract och persistent status

Inför `gpt-project.yaml` och `project-status.yaml` utan att ändra System Modellers domänbeteende.

Definiera project metadata, canonical instruction source, knowledge architecture, capability contract, artifact contract, workspace/state contract, explicit tool contract, runtime registry för Chat, Custom GPT, Claude och OpenCode samt build targets och filnamn.

Klar när projektkontraktet kan lintas deterministiskt och statusen kan användas som primär källa för nästa steg.

### C2 – Canonical instruction och runtime parity baseline

Gör den gemensamma instruktionen platform-neutral och härled runtime-specifika bootstrap/adaptrar från den.

Skapa en generell paritetsrapport för behavior, capability, artifact, workspace/state och tools över alla fyra runtimes.

Klar när Chat och Custom GPT fortfarande har samma funktionella beteende som före migrationen och Claude/OpenCode har explicit compatibilitystatus.

### C3 – Claude Project distribution

Implementera Claude Project-adaptern med Project Instructions från canonical instruktion, relevant canonical knowledge, `project/runtime-contract.json`, README, VERSION och manifest.

Lokala runtime-scripts ska redovisas som reducerade eller saknade i paritetsmodellen, inte utges för att vara direkt körbara.

Klar när Claude-distributionen byggs deterministiskt och passerar strukturell samt kontraktsbaserad validering.

### C4 – OpenCode workspace distribution

Implementera OpenCode-adaptern med genererad root `AGENTS.md`, `.opencode/runtime-contract.json`, `opencode.json`, endast uttryckligen deklarerade runtime-scripts, typade custom-tool wrappers under `.opencode/tools/`, optional skills endast där de motsvarar deklarerade workflows, relevant canonical knowledge, README, VERSION och manifest.

Muterande custom tools ska kräva godkännande; read-only tools får köras direkt.

Klar när OpenCode-distributionen byggs deterministiskt och passerar adapter- och paritetsvalidering.

### C5 – Unified build och validation

Inför en gemensam buildväg som bygger aktiverade mål från projektkontraktet.

Byggresultatet ska omfatta projektpaket, Chat ZIP, Custom GPT ZIP, Claude ZIP, OpenCode ZIP, build/delivery manifest, SHA-256 checksums och runtime parity report.

Behåll befintliga projektspecifika packaging-kommandon som kompatibilitetslager där det är motiverat, men låt CI använda den gemensamma vägen.

### C6 – CI och GitHub Release

Uppdatera `.github/workflows/build-distributions.yml` så att PR, main, workflow_dispatch och release validerar den nya modellen.

PR/main ska bygga och validera alla fyra runtimeartefakter. GitHub Release ska bifoga samtliga publicerbara runtime-ZIP:ar, manifest/paritetsrapport och checksums.

Release ska stoppas om en aktiverad runtime har blockerande valideringsfel eller `do_not_publish`.

### C7 – Regression, dokumentation och hygiene

Lägg till tester för runtime adapter content, canonical-source parity, declared tool inclusion/exclusion, OpenCode permission policy, Claude tool reduction, version propagation, deterministic ZIP builds och release readiness för fyra runtimes.

Uppdatera README, runtime-dokumentation, STATUS och CHANGELOG. Kör slutlig project hygiene och release-readiness.

## Förväntade distributionsartefakter

Vid version `X.Y.Z` ska release minst kunna producera:

- `system-modeller-project-vX.Y.Z.zip`
- `system-modeller-chat-vX.Y.Z.zip`
- `system-modeller-custom-gpt-vX.Y.Z.zip`
- `system-modeller-claude-vX.Y.Z.zip`
- `system-modeller-opencode-vX.Y.Z.zip`
- build/delivery manifest
- runtime parity report
- `SHA256SUMS.txt`

## Initial kompatibilitetsbedömning

| Område | Chat | Custom GPT | Claude Project | OpenCode |
|---|---|---|---|---|
| Canonical behavior | ready | ready | ready efter adapter | ready efter adapter |
| Knowledge | ready | ready | ready efter paketering | ready efter paketering |
| Läsa/skriva workspacefiler | runtimeberoende | reducerad | reducerad | ready |
| Köra lokala scripts | runtimeberoende | reducerad | reduced/missing | ready via declared tools |
| Persistent project state | via projektfil | via projektfil/manual | via Project Files/manual | ready i workspace |
| Deterministiska tools | befintliga scripts | ej inbäddade | ej inbäddade | kan exponeras som custom tools |

Claude ska alltså inte försöka imitera OpenCodes lokala verktygsintegration. Skillnaden dokumenteras i paritetsrapporten och är inte i sig ett hinder för en användbar Claude-distribution, förutsatt att kritiska beteenden har säker manuell fallback.

## Resultat

Plan C är slutförd.

- C1 etablerade canonical project contract och persistent status.
- C2 gjorde runtimebeteendet plattformsneutralt och införde parity-baseline.
- C3 implementerade Claude Project-distributionen.
- C4 implementerade OpenCode workspace-distributionen.
- C5 införde unified build och validering.
- C6 införde full CI- och GitHub Release-publicering.
- C7 slutförde regression, dokumentation och repository hygiene.

Samtliga fyra runtimes har compatibility `ready` och byggs från samma canonical projektkontrakt.
