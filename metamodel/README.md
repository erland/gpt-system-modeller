# metamodel

Den normativa metamodellen byggs stegvis under Plan A.

## A4 – gemensam bas

- `common.yaml` beskriver gemensamma fält och konventioner för modellobjekt och relationer.
- `id-prefixes.yaml` innehåller det provisoriska registret över stabila typ-prefixer.

Domänspecifika elementtyper börjar introduceras i A5.


## A5 – kontext

- `context.yaml` definierar `System`, `ExternalSystem`, `Actor` och deras tillåtna kontextrelationer.


## A6 – funktionella ansvarsområden

- `functions.yaml` definierar `Responsibility / SystemFunction`, `has_responsibility` och de semantiska bryggorna till kommande UseCase- och Component-steg.

## A7 – use cases

- `use-cases.yaml` definierar `UseCase`, dess obligatoriska aktörs-/ansvarsreferenser och relationerna `performs`, `groups_use_case`, `includes`, `extends` och `specializes`.

- `information.yaml` – InformationObject och konceptuella informationsrelationer (A8).

## A9 – informationsanvändning

- `information-usage.yaml` definierar create/read/update/delete, ownership/mastering, storage och exchange mot `InformationObject`, inklusive deklarerade framtida par till A10/A11/A13.

- `logical-structure.yaml` – A10: Subsystem, Component, Service och logiska relationer.
- `messaging.yaml` – Message/Event och meddelanderelationer (A12).
- `data-stores.yaml` – A13: DataStore, lagrad information, åtkomst och ägarskap.

- `scenarios.yaml` – A14: konceptuella end-to-end-scenarier.
- `interactions.yaml` – A15: Interaction och inbäddade Participant-referenser för dynamisk realisering.

- `runtime.yaml` – A17: RuntimeUnit och relationen `realized_as` från logisk arkitektur till runtime.

- `deployment.yaml` – A18: Environment och DeploymentNode; deploymentrelationer reserveras till A19.

- `decisions.yaml` – A20: ArchitectureDecision, Constraint och påverkan via `affects`.

## A21 – provenance och evidens

- `provenance.yaml` – Source, SourceReference och Evidence.

## A22 – origin

- `origin.yaml` definierar `declared`, `observed`, `inferred`, `user_confirmed` och `unresolved` som separat ursprungsdimension för modellobjekt och relationer.
