# Message och Event – normativ guide för A12

## Syfte

A12 inför ett enkelt meddelande- och eventperspektiv för integrationsarkitekturen. Målet är att kunna beskriva **arkitekturellt betydelsefull kommunikation** utan att modellera varje teknisk payload, handler eller broker-detalj.

Både `Message` och `Event` ligger på abstraktionsnivån `logical`.

## Message

`Message` används när ett namngivet informationsutbyte eller kommando behöver synliggöras mellan system eller logiska systemdelar.

Exempel:

- `ReserveInventory`
- `PaymentRequest`
- `DeliveryInstruction`

Ett Message har:

- exakt en `producer`,
- minst en `consumer`,
- `communication_mode`: `synchronous` eller `asynchronous`,
- valfri koppling till `InformationObject`,
- valfritt `channel`, `topic` och `protocol`.

`Message` ska inte skapas för varje metodanrop eller intern DTO. Om kommunikationen inte hjälper en läsare att förstå systemets arkitektur bör den utelämnas från den logiska modellen.

## Event

`Event` används när kommunikationen uttrycker att **något har inträffat** och andra systemdelar eller externa system kan reagera på detta.

Exempel:

- `OrderCreated`
- `PaymentCompleted`
- `ShipmentDispatched`

Events betraktas som **asynchronous** i MVP:n. `communication_mode` kan anges som `asynchronous` för tydlighet men får inte vara något annat.

Ett Event har:

- exakt en `producer`,
- minst en `consumer`,
- valfri koppling till `InformationObject`,
- valfritt `channel`, `topic` och `protocol`.

## Producenter och konsumenter

I A12 får `producer` och `consumers` referera till:

- `System`
- `ExternalSystem`
- `Component`
- `Service`

Tekniska implementationsobjekt som Java-klasser, event handlers eller consumers i koden ska inte automatiskt lyftas till logiska producenter/konsumenter.

## Relationer

För Message används:

- `sends`: arkitekturelement → Message
- `receives`: arkitekturelement → Message

För Event används:

- `publishes`: arkitekturelement → Event
- `subscribes`: arkitekturelement → Event

Fälten `producer`/`consumers` gör modellen lätt att läsa och relationerna gör graftraversering enkel. Om båda representationerna finns ska de beskriva samma faktum.

## Informationskoppling

`exchanged_information` refererar alltid till konceptuella `InformationObject`.

Exempel:

```yaml
exchanged_information:
  - INFO-000001
```

Det betyder inte att hela det konceptuella informationsobjektet måste serialiseras i meddelandet. Det anger vilken verksamhetsinformation meddelandet eller eventet huvudsakligen handlar om.

## Channel och topic

`channel` och `topic` är enkla strängfält i A12.

Exempel:

```yaml
channel: Kafka
topic: order-events
```

De är avsiktligt inte egna modellobjekt ännu. Om fysisk meddelandeinfrastruktur senare behöver bli en viktig arkitekturvy kan metamodellen utökas utan att A12-modellen behöver göras om.

## Message eller API?

Använd `API` när det arkitekturellt viktiga är det exponerade kontraktet/gränssnittet.

Använd `Message` eller `Event` när det viktiga är ett namngivet informationsutbyte, kommando eller en händelse i kommunikationsflödet.

Samma integration kan därför i vissa fall ha både ett API och ett Message, men bara om båda perspektiven tillför systemförståelse.

## Abstraktionsregel

Välj den högsta nivå som fortfarande förklarar systemets beteende. En kodbas kan innehålla hundratals meddelandeklasser men systemmodellen bör normalt bara innehålla de meddelanden/events som är relevanta för centrala integrationer, use cases eller scenarier.
