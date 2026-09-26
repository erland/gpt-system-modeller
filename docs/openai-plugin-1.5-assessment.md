# OpenAI Plugin compatibility assessment – GPT Byggaren 1.5.0

## Beslut

OpenAI Plugin är **inte en aktiv runtime-distribution** för System Modeller i GPT Byggaren 1.5.0.

Compatibility-målet är **reduced / advisory only**.

Pluginen får användas för rådgivande modellstöd när användaren tillhandahåller tillräckligt underlag, men får inte presenteras som full peer runtime för System Modellers kompletta projektflöde.

## Kärnkrav för full parity

Full System Modeller-runtime kräver i praktiken:

- åtkomst till konkreta projektfiler,
- tillförlitlig validering före och efter mutation,
- persistent workspace/state utanför chattminnet,
- kontrollerad mutation av canonical YAML,
- faktisk exekvering av runtimeverktyg,
- paketering av komplett systemprojekt,
- spårbarhet för stable IDs, provenance, evidence, origin och unresolved uncertainty,
- no-false-PASS.

En skills-first plugin får därför inte anta att dessa capabilities finns bara för att instruktioner eller referensfiler kan paketeras.

## Tillåtet advisory-beteende

En framtida advisory-plugin får bland annat:

- förklara System Modellers metamodel och modelleringsprinciper,
- resonera om element, relationer, evidens och origin,
- föreslå små change plans,
- analysera användartillhandahållet modellunderlag,
- föreslå vyer och rapportstruktur,
- förklara valideringsfel som användaren tillhandahåller.

Den får inte, utan faktisk capability:

- hävda att scripts eller validering har körts,
- hävda att canonical YAML har muterats,
- behandla chattminne som auktoritativ projektstate,
- hävda att ett komplett projekt-ZIP har skapats,
- hävda att paketering eller teknisk validering har passerat,
- omvandla unrun verification till PASS.

## Aktiveringskriterier

OpenAI Plugin får inte flyttas till aktiv peer runtime förrän en konkret implementation kan demonstrera och CI-verifiera:

1. projektfilåtkomst,
2. tillförlitlig validation before/after,
3. persistent workspace/state,
4. kontrollerad canonical mutation,
5. faktisk runtime-tool execution,
6. komplett projektpaketering.

Fram till dess gäller:

- registry status: `not_active`
- compatibility target: `reduced`
- mode: `advisory_only`
- aktiv distribution: nej
