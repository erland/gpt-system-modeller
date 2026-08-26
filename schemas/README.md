# schemas

Här finns formella JSON Schemas för YAML-modellen. YAML används som primärt lagringsformat, men valideras mot JSON Schema eftersom YAML-data kan representeras som JSON-kompatibla strukturer.

## A4

`common.schema.json` definierar den återanvändbara basen:

- stabila ID:n,
- abstraktionsnivåer,
- gemensamma modellobjekt,
- relationer som förstaklassobjekt.

Senare schemas ska återanvända `$defs` från denna bas i stället för att duplicera reglerna.


## A5

`context.schema.json` specialiserar A4-basen för `System`, `ExternalSystem` och `Actor` och begränsar kontextrelationerna till A5:s relationsvokabulär.


## A6

- `functions.schema.json` validerar kontextobjekten tillsammans med `Responsibility` och de relationsformer som är aktiva till och med A6.

## A7

- `use-cases.schema.json` validerar kontext, Responsibility och UseCase inklusive primär aktör, ansvar, outcome och valfria use-case-detaljer.

- `information.schema.json` – validering av InformationObject och informationsrelationer (A8).

## A9

- `information-usage.schema.json` validerar modellen genom A9 och tillåter de explicita informationsanvändningsrelationerna.

- `logical-structure.schema.json` – A10: validering av logisk systemstruktur.
- `messaging.schema.json` – Message/Event-modell genom A12.
- `data-stores.schema.json` – A13: validering av DataStore och dess relationer.

- `scenarios.schema.json` – A14: validering av Scenario.
- `interactions.schema.json` – A15: validering av Interaction och Participant-referenser.

- `runtime.schema.json` – A17: validering av RuntimeUnit och logisk-till-runtime-realisering.

- `deployment.schema.json` – A18: validering av Environment och DeploymentNode tillsammans med modellen genom A17.

- `decisions.schema.json` – A20: validering av ArchitectureDecision, Constraint och `affects`.

## A21

- `provenance.schema.json` validerar modellen genom A21 och lägger till separata `sources`, `source_references` och `evidence`-samlingar.

## A22

- `origin.schema.json` validerar modellen genom A22; `common.schema.json` begränsar nu `origin` till den normativa värdemängden.


## A23

- `project.schema.json` validerar `project.yaml` för ett portabelt System Modeller-systemprojekt.
