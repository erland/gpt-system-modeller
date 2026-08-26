# Interaction, Participant och InteractionMessage

`Interaction` beskriver **hur ett viktigt Scenario realiseras genom samverkan mellan arkitekturellt relevanta deltagare**. Den ligger på `logical`-nivån. A16 kompletterar A15 med `InteractionMessage`, vilket gör att interaktionen kan bära ett ordnat huvudflöde och senare generera en Sequence View.

## Interaction

En Interaction har egen stabil identitet (`INT-*`) och ska i MVP:n normalt referera till exakt ett `Scenario`.

Obligatoriskt:

- `scenario` – det Scenario som realiseras,
- `participants` – minst två deltagare.

Valfritt:

- `purpose` – vad interaktionen ska förklara,
- `messages` – ordnade arkitekturella kommunikationssteg.

Interaction ska modellera arkitekturellt relevant samverkan. Metodanrop, framework hooks och andra implementationsdetaljer ska inte lyftas upp bara för att de går att observera i koden.

## Participant

`Participant` är **inte ett eget duplicerat arkitekturobjekt**. Det är en inbäddad referens/roll till ett redan befintligt element.

Tillåtna deltagartyper i MVP:n är:

- `Actor`
- `System`
- `ExternalSystem`
- `Component`
- `Service`
- `DataStore`

`role` och `alias` påverkar hur deltagaren kan beskrivas i just interaktionen men ändrar inte det refererade objektets identitet.

## InteractionMessage

`InteractionMessage` beskriver ett **arkitekturellt relevant steg mellan två deltagare** i samma Interaction. Det är ett inbäddat dynamiskt objekt, inte ett nytt top-level arkitekturelement.

Varje InteractionMessage har:

- `id` – stabilt `IM-*`-ID,
- `order` – explicit sekvensnummer,
- `sender` – referens till en deltagare,
- `receiver` – referens till en deltagare,
- `label` – begriplig beskrivning av utbytet,
- `communication_mode` – `synchronous` eller `asynchronous`.

Valfritt kan det ha:

- `operation` – relevant operation/kontraktsnamn,
- `information` – ett eller flera `InformationObject`,
- `condition` – villkor för steget,
- `message_ref` – referens till ett arkitekturellt `Message` eller `Event` från integrationsmodellen.

Exempel:

```yaml
messages:
  - id: IM-000001
    order: 1
    sender: ACT-000001
    receiver: CMP-000001
    label: Submit order
    operation: placeOrder
    communication_mode: synchronous
    information: [INFO-000001]
```

## Ordning och konsistens

`order` är den kanoniska sekvensordningen. Listordning får inte användas som enda semantik. `order` ska vara unikt inom en Interaction.

`sender` och `receiver` måste båda finnas i samma Interactions `participants`-lista. En framtida semantisk validator kan kontrollera detta deterministiskt; A16-testet verifierar regeln på referensexemplet.

## Informationskoppling

`information` refererar till konceptuella `InformationObject`. En payload-klass, DTO eller databastabell ska inte ersätta informationsbegreppet bara för att den förekommer i implementationen.

## Förhållande till Message och Event

A12:s `Message` och `Event` beskriver återanvändbara arkitekturella integrationskontrakt eller händelser. Ett `InteractionMessage` är ett steg i ett specifikt scenarioflöde.

Om steget realiserar ett redan modellerat Message/Event kan `message_ref` användas. Annars räcker ett begripligt `label` och relevanta informationsreferenser i MVP:n.

## Detaljnivå

InteractionMessage ska inte bli ett kodspår. Ta med de steg som behövs för att förstå systemets beteende och ansvarsfördelning. Interna getters, ramverkscallbacks, serialisering, ORM-anrop och liknande implementationsbrus ska normalt lämnas utanför.

## Relationer

För grafbaserade vyer eller frågor kan deltagarreferenserna materialiseras som:

- `realizes_scenario`: `Interaction → Scenario`
- `has_participant`: `Interaction → Actor/System/ExternalSystem/Component/Service/DataStore`

InteractionMessage ligger inbäddat i Interaction och behöver därför ingen separat top-level relation i A16.
