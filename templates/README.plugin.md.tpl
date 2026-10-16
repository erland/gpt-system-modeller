# {{GPT_NAME}} — OpenAI Plugin

Version: {{VERSION}}

Detta är en genererad skills-first plugin-distribution från GPT Byggaren.

## Innehåll

Pluginpaketet innehåller:

- `plugin.json`
- en eller flera skills under `skills/`
- relevanta `references/`
- relevanta `assets/`
- runtime-relevanta `scripts/`
- `runtime-contract.json`
- `MANIFEST.json`
- `VERSION`

## Skills

{{SKILLS}}

## Installation och användning

Installera pluginpaketet enligt den aktuella ChatGPT/plugin-miljön där det ska användas.

Runtimepaketet är genererat från projektets canonical kontrakt. Runtime-specifika filer i paketet ska därför betraktas som genererade artefakter, inte som nya sanningskällor.

## Begränsningar i Plugin v1

Denna version är skills-first och genererar inte:

- MCP-servrar
- UI-komponenter
- lifecycle hooks
- marketplace-metadata

Sådana funktioner ska endast införas när projektets use case faktiskt kräver dem.

## Script-resurser och MCP

Scripts under en skill är runtime-resurser. När host-runtimen erbjuder kompatibel code execution kan skillen använda dem direkt; de behöver inte automatiskt kapslas som MCP-tools.

MCP är en separat integrationsform och behövs när projektet kräver ett explicit, garanterat tool-gränssnitt eller serverbaserad exekvering. Full funktionalitet för ett script beror fortfarande på att hosten erbjuder de dependencies, filesystem-rättigheter och workspace-funktioner som scriptet behöver.

## Portabilitet

Skilldefinitioner, referenser, assets och scripts är härledda från samma canonical projektdata som övriga peer runtimes.
