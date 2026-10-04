# OpenAI Plugin compatibility assessment – GPT Byggaren 1.5.0

## Beslut

OpenAI Plugin är en **aktiv peer runtime** för System Modeller.

Compatibility är `equivalent_runtime_dependent`.

Det betyder att canonical System Modeller-beteende kan bevaras när hosten tillhandahåller de capabilities som krävs för ett verkligt projektflöde. Pluginpaketet provisionerar inte själv workspace eller Python-runtime.

## Kärnkrav

Fullt System Modeller-flöde kräver:

1. faktisk projektfilåtkomst och filesystem read/write,
2. persistent workspace/state utanför chattminnet,
3. Python code execution,
4. PyYAML och jsonschema,
5. validation before/after canonical mutation,
6. kontrollerad canonical mutation med approval,
7. runtime-tool execution för deterministic derive/report/package,
8. komplett projektpaketering,
9. preservation av stable IDs, provenance, evidence, origin och unresolved uncertainty,
10. no-false-PASS.

Canonical YAML är alltid source of truth. Conversation history är aldrig auktoritativ projektstate.

## Paketerade runtimeverktyg

Pluginen innehåller de sju canonical runtimeverktygen:

- context.py
- validate.py
- model.py
- view.py
- report.py
- package_project.py
- analyze.py

Den innehåller också deras explicita support-closure:

- ids.py
- report_profile.py
- sequence_diagrams.py
- view_split.py
- diagram_complexity.py

samt runtime-relevant `schemas/` och `metamodel/`.

Scripts är resurser och behöver inte MCP-wrapper enbart för att köras. Hostens kompatibla Python code execution kan användas direkt.

## Mutation och approval

`model.py` muterar canonical YAML och kräver approval. Pluginen ska bevara ordningen:

`INSPECT → VALIDATE → PLAN → CHANGE → VALIDATE → DERIVE → PACKAGE`

Mutation får inte genomföras om pre-validation inte kan köras tillförlitligt. Post-validation måste köras efter förändring.

## Runtime-dependent parity

`equivalent_runtime_dependent` är korrekt eftersom parity beror på hosten. Om required filesystem, persistent workspace/state eller Python execution saknas får Pluginen fortfarande ge rådgivande hjälp, men den får inte hävda att canonical System Modeller-flödet genomförts.

Unrun verification får aldrig redovisas som PASS. Ett scriptresultat får aldrig simuleras.

## Release

Plugin-distributionen byggs och valideras som:

`system-modeller-plugin-v<version>.zip`

Den ingår i registry-driven unified build, parity, checksums, manifest och exact release asset set.
