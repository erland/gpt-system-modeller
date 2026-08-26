# DeploymentNode och Environment – A18

## Syfte

A18 kompletterar `RuntimeUnit` med två begrepp som behövs för en övergripande deploymentbild: `DeploymentNode` och `Environment`.

`RuntimeUnit` svarar på **vad som körs**. `DeploymentNode` svarar på **var det kan eller faktiskt körs på arkitekturnivå**. `Environment` anger **vilken livscykel-/runtime-miljö** deploymenten hör till.

```text
Component / Service
        |
   realized_as
        v
   RuntimeUnit
        |
   deployed_on       (A19)
        v
 DeploymentNode
        |
   belongs_to        (A19)
        v
   Environment
```

## Environment

`Environment` är ett runtime-kontextobjekt och representerar exempelvis:

- `development`
- `test`
- `staging`
- `production`
- `other`

Environment ska inte användas som synonym för server, kluster eller plattform.

## DeploymentNode

Tillåtna nodtyper i MVP:n är:

- `client_device`
- `server`
- `virtual_machine`
- `container_platform`
- `cloud_service`
- `database_platform`
- `external_platform`

Frivilliga attribut `platform`, `technology` och `location_hint` kan användas när de förbättrar förståelsen. De ska inte göra deploymentmodellen till ett inventarium över fysisk infrastruktur.

## Abstraktionsnivå

MVP:n eftersträvar en **övergripande deploymentvy**. Modellera exempelvis `OpenShift Production`, inte varje pod, replica set och worker node, när dessa detaljer inte behövs för att förstå arkitekturen.

Ett klientperspektiv kan modelleras som en `DeploymentNode` av typen `client_device`, medan en extern SaaS- eller molnplattform kan vara `external_platform` eller `cloud_service` beroende på vad som bäst beskriver arkitekturen.

## Relation till A19

A18 definierar endast själva elementen. Följande kanoniska relationer införs i A19:

- `RuntimeUnit -> deployed_on -> DeploymentNode`
- `DeploymentNode -> belongs_to -> Environment`
- övergripande kommunikationsrelationer mellan runtime-enheter, datalager och externa system

Detta undviker att blanda ihop elementdefinition med deploymenttopologi innan relationssemantiken är definierad.
