# System Modeller – fas 2, GPT Byggaren 1.6.25

## Genomfört
- Fas 1 finns som ursprung; äldre 1.5-konfiguration bevarad i `gpt-project.legacy-1.5.yaml`.
- Ny kanonisk 1.6.25-konfiguration med samma ursprungliga `instructions/chat-runtime.md`.
- Domänens modell, metamodell, scheman, exempel och sju runtime-verktyg behållna.
- GPT Byggaren 1.6.25:s byggskript och byggkontrakt integrerade, inklusive fix för delat bibliotek i Plugin-paketering.
- Sex ZIP-artefakter byggda: projektet samt Chat ZIP, OpenAI Plugin, Claude Project, Claude Skills och OpenCode.
- `validate_distributions.py`: PASS för de byggda distributionerna.

## Kvarstående blockerare före release
- Fullständigt `lint_gpt_project.py` misslyckas: konfigurationen innehåller katalog-, dokument- och schemasökvägar från byggmotorns eget referensprojekt som inte levereras i den bifogade Chat-motorns källpaket. Därför är projektet **inte releaseklart**.
- Vissa 1.5-kontraktstester förutsätter den äldre `gpt-project.yaml`-strukturen och behöver uppdateras till migreringens 1.6.25-kontrakt. Vid körning med pytest passerade 6 av 7 insamlade testfunktioner före en saknad `eval-case.schema.json` i byggmotorns stödfiler.
- Runtime-miljöerna för Claude, OpenCode och ChatGPT Plugin har inte körts live. Verifiering gäller genererade paket och intern distributionstruktur.
- Ingen GitHub-push, PR eller release har genomförts.

## Nästa åtgärd
Slutför projektspecifikt kontrakt och CI mot kompletta 1.6.25-projektscheman; kör hela gamla domänregressionen och ny plattformsparitet; därefter release.
