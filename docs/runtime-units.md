# RuntimeUnit – A17

## Syfte

`RuntimeUnit` beskriver **vad som faktiskt körs**. Den ligger på abstraktionsnivån `runtime` och bildar bryggan mellan den logiska arkitekturen och den deploymentmodell som införs i A18–A19.

En RuntimeUnit ska vara begriplig på arkitekturnivå. Den är inte automatiskt samma sak som en klass, process, pod, containerinstans eller fysisk server.

## Tillåtna runtime-typer i MVP

- `web_application`
- `application_service`
- `background_service`
- `batch_job`
- `database`
- `message_broker`
- `function`

## Koppling till logisk arkitektur

Den kanoniska relationen är:

```text
Component / Service / DataStore
            |
       realized_as
            v
       RuntimeUnit
```

Exempel: den logiska komponenten `Order Management` kan realiseras som runtime-enheten `Order API`. Ett logiskt `DataStore` kan realiseras som en körande databasinstans på runtime-nivå.

## Viktig gränsdragning

`Component` beskriver **logiskt ansvar**. `RuntimeUnit` beskriver **körbar realisering**. `DeploymentNode`, som införs i A18, beskriver **var** RuntimeUnit körs.

```text
Component -> RuntimeUnit -> DeploymentNode
   vad          vad körs       var körs det
```

En deploybar mikrotjänst kan därför vara en RuntimeUnit, medan den logiska Service som den erbjuder är ett separat objekt. Om den tekniska skillnaden inte bidrar till systemförståelsen ska modellen hållas enklare.

## Detaljnivå

MVP:n ska normalt inte modellera varje replica, pod eller processinstans. Modellera den runtime-enhet som behövs för att en läsare ska förstå systemets övergripande körstruktur och senare Deployment View.

## Teknik och artifact

`technology` och `artifact` är frivilliga enkla attribut i A17. En mer strukturerad teknikmodell kommer senare. De ska användas sparsamt när de hjälper förståelsen, exempelvis `Java/Quarkus` eller `order-api.jar`.
