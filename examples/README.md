# examples

Denna katalog etablerades i Plan A steg A1.

Innehållet byggs ut i senare steg. A1 låser ingen domänmetamodell eller slutlig runtime-design i förtid.


## A5

`a05-context-model.yaml` visar ett minimalt systemkontext-exempel med System, Actor, ExternalSystem och relationer.

- `a07-use-case-model.yaml` visar hur Actor, Responsibility och UseCase binds samman utan implementationstekniska detaljer.

- `a08-information-model.yaml` – konceptuell informationsmodell med Order, Orderrad och härledd information.

- `a10-logical-architecture.yaml` – A10: exempel på Subsystem, Component och Service.
- `a12-messages-events.yaml` – synkront Message och asynkront Event.
- `a13-data-stores.yaml` – logiskt datalager, lagrad information, åtkomst och ägarskap.
- `a14-scenarios.yaml` – konceptuellt end-to-end-scenario.
- `a15-interactions.yaml` – dynamisk Interaction med arkitekturella deltagare.

- `a18-deployment-context.yaml` – miljöer, klientnod, containerplattform och databasplattform på övergripande deploymentnivå.

- `a20-decisions-constraints.yaml` – arkitekturbeslut, constraints och påverkade modelelement.

- `a21-provenance-evidence.yaml` – spårbarhet från arkitekturelement och relationer via Evidence och SourceReference till dokumentation, kod och användaruppgift.

- `a22-origin.yaml` – exempel på declared, observed, inferred och kombinerade origin-värden tillsammans med A21-evidens.

- `a23-system-project/` – komplett minimalt systemprojekt med manifest och modellshards.
