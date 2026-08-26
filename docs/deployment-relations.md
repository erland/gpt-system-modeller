# Deployment- och kommunikationsrelationer (A19)

Detta dokument är normativt för Plan A steg A19.

A18 definierade **RuntimeUnit**, **DeploymentNode** och **Environment**. A19 kopplar ihop dem till en övergripande deploymenttopologi och lägger till de viktigaste kommunikationsvägarna.

## `deployed_on`

`RuntimeUnit → DeploymentNode`

Används för att beskriva **var en körbar enhet är deployad**.

Exempel:

```text
Order API → deployed_on → OpenShift Production
```

Relationen ska ligga på arkitekturnivå. En runtime-enhet ska normalt inte modelleras som deployad på varje enskild pod eller replika.

## `belongs_to`

`DeploymentNode → Environment`

Anger vilken miljö en deploymentnod tillhör.

Exempel:

```text
OpenShift Production → belongs_to → Production
```

Miljö och nod är separata koncept: `Production` beskriver livscykel-/runtimekontext, medan `OpenShift Production` beskriver var körning sker.

## `connects_to`

Kanoniska MVP-par:

```text
RuntimeUnit → RuntimeUnit
RuntimeUnit → DataStore
RuntimeUnit → ExternalSystem
```

Relationen beskriver en **arkitekturellt relevant kommunikationsväg**. Den ska inte användas för varje tekniskt nätverksanrop.

### Valfria egenskaper

- `protocol` – exempelvis HTTPS, AMQP eller JDBC
- `direction` – `source_to_target` eller `bidirectional`
- `encryption` – exempelvis TLS eller mTLS
- `purpose` – kort arkitekturellt syfte
- `exchanged_information` – referenser till konceptuella `InformationObject`

`source_to_target` är normalfallet. `bidirectional` används endast när båda riktningarna är en del av samma relevanta kommunikationsväg.

## Informationsutbyte

`exchanged_information` ska referera till konceptuella informationsobjekt, exempelvis `Order` eller `Payment`, inte till DTO-klasser, JSON-filer eller databastabeller.

## Deployment-vyn i MVP

A19 ger tillräckligt underlag för en övergripande vy av typen:

```text
[Customer browser]
        |
        | HTTPS / TLS
        v
[OpenShift Production]
        |
        +-- Order Web
        +-- Order API ---- JDBC ----> [Order Database]
              |
              +---- HTTPS ----> [Payment Provider]
```

Syftet är att svara på:

1. Vad körs?
2. Var körs det?
3. I vilken miljö?
4. Vilka huvudkommunikationsvägar finns?
5. Vilken central information utbyts?

Detaljer som portar, routes, podnamn, repliker och nätverkspolicyer hör normalt inte hemma i MVP-vyn.
