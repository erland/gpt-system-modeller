# Migrering till GPT Byggaren 1.6.25 – fas 1

## Utgångsläge
Källprojekt: gpt-system-modeller, VERSION 0.1.0-dev.57. Migreringen har genomförts på en separat kopia; ursprungligt ZIP-innehåll har inte ändrats.

## Utfört
- Evidensbaserad inventering med GPT Byggaren 1.6.25:s `migrate_legacy_copy.py`.
- Normaliserat grundkontrakt för capabilities och härlett preliminärt workspace/state-kontrakt i `gpt-project.yaml`.
- Sparat maskinläsbart revisionsunderlag i `MIGRATION-REPORT.json`.
- Kontrollerat befintligt projektkontrakt och runtime-registry med lyckat resultat.
- Kört de existerande C1–C4-skripttesterna med lyckat resultat.

## Kritiska kompatibilitetsfrågor inför fas 2
1. Projektet har kanonisk instruktion på `instructions/chat-runtime.md`, men nya motorn förväntar modern `src/instructions`-struktur. Flytta inte innehåll utan att behålla kanoniskt beteende och samtliga hänvisningar.
2. De sju runtimeverktygen är redan explicit deklarerade i projektets `contracts.tools`: context, validate, model, view, report, package_project och analyze. Granska verkliga beroenden, exekveringskrav och behörigheter innan de projiceras till nya motorns `tools`-format. Resterande Pythonfiler är inte automatiskt runtimeverktyg.
3. Nuvarande `runtimes`/`build.active_targets` är GPT Byggaren 1.5-format. Nytt format kräver `runtime` och `build_system.runtime_targets` med fem mål: chat, plugin, claude_project, claude_skills och opencode. Custom GPT är historiskt och ska pensioneras först efter funktionell jämförelse.
4. Verifiera Plugin-körning av Python, skrivbart filsystem och persistent workspace. Paketfiler räcker inte för att intyga körbarhet i host-miljö.
5. Projektets egna builders, CI och releaseartefaktnamn måste avstämmas mot nya byggmotorn utan att ersätta domänens egna Pythonverktyg.
6. Uppdatera README, PROJECT.md, STATUS.md, docs/development-plan.md och CI/release först när den nya motorn kan producera och validera distributionerna.

## Verifiering
PASS: scripts/validate_project_contract.py
PASS: scripts/validate_runtime_distribution_registry.py
PASS: tests/test_c1.py, test_c2.py, test_c3.py, test_c4.py (direkt exekverade som skript)
EJ GENOMFÖRT: installation av den nya kanoniska byggmotorn, fem nya runtimebyggen, host-paritet och release-readiness. Migrationsverktyget markerar `ready_with_manual_review`, inte release-ready.

## Rekommenderat nästa steg
Granska och komplettera det nya plattformsneutrala canonical capability/artifact/workspace/tool-kontraktet, inklusive projektspecifika script och beroenden. Anpassa sedan källstruktur och `build_system.runtime_targets`, installera GPT Byggaren 1.6.25-motorn, bygg och validera fem distributioner.
