# Vyer och diagram

System Modeller-vyer är **projektion av den kanoniska YAML-modellen**. De får filtrera och härleda presentation, men aldrig bli en alternativ sanningskälla.

## Generellt vyformat

En vy anger bland annat `type`, syfte, målgrupp, detaljnivå, notation och valfria filter. `scripts/view.py` kan materialisera en standardvy med `--type` eller en återanvändbar definition i projektets `views/`.

## Kärnvyer efter A27

1. **System Context** – systemgräns, aktörer och externa system.
2. **Functional Overview** – systemets funktionella ansvar.
3. **Use Case Overview** – aktörer, ansvar och use cases.
4. **Information Overview** – centrala informationsobjekt.
5. **Functional–Information View** – funktioners/use cases informationsanvändning.
6. **Logical Component View** – subsystem, komponenter, tjänster, interfaces och datalager.
7. **Use Case Realization View** – Actor → UseCase → Responsibility → Component/Service → Information.
8. **Integration View** – API:er/interfaces, messages/events, producenter/konsumenter och information.
9. **Sequence View** – deltagare och ordnade `InteractionMessage` från ett `Interaction`.
10. **Deployment View** – RuntimeUnit, DeploymentNode, Environment, DataStore/ExternalSystem och huvudkommunikation.

## Härledda länkar

Vymotorn får härleda länkar från kanoniska referensfält, exempelvis `UseCase.primary_actor`, `UseCase.realized_by`, `API.provider`, `API.consumers`, `Message.producer` och `Event.consumers`. Sådana länkar märks `derived: true` och skrivs inte tillbaka till modellen.

## Sequence View

`sequence` materialiserar `Interaction.participants` och `Interaction.messages`. Med `filters.interaction_id` kan en vy begränsas till en specifik interaktion. Meddelanden sorteras på `order`.

## Deployment View

Deployment-vyn håller MVP-abstraktionen: **vad körs, var körs det, i vilken miljö och vilka huvudsakliga kommunikationsvägar finns**. Pods, replicas och motsvarande detaljobjekt ska inte introduceras om de inte behövs för systemförståelsen.

## Diagramformat

A27 stödjer direkt rendering till:

- YAML – neutral materialisering
- JSON – neutral materialisering
- Mermaid – diagramtext
- PlantUML – diagramtext

Exempel:

```bash
python3 scripts/view.py /path/to/project --definition /path/to/project/views/deployment.yaml --format mermaid
python3 scripts/view.py /path/to/project --type sequence --format plantuml
```

Mermaid/PlantUML är härledd export och kan alltid återskapas.

## Nästa steg

A28 använder dessa vyer som byggblock i den första samlade arkitekturbeskrivningen.
