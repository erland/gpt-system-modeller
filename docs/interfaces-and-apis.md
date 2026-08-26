# Interface och API

## Syfte

A11 inför ett logiskt kontraktslager mellan konsumenter och providers. Ett **Interface** beskriver en arkitekturellt relevant åtkomstpunkt eller ett kontrakt. Ett **API** är en specialisering för maskinläsbara API:er.

## Abstraktionsnivå

Båda ligger på `logical`-nivån. Enskilda endpoints, controllers eller metoder är implementationsdetaljer och ska inte automatiskt bli Interface/API i arkitekturmodellen.

## Provider och consumers

Varje Interface/API ska i MVP ha en logisk `provider`. `consumers` är valfritt och kan innehålla flera System, ExternalSystem, Component eller Service.

Relationerna `exposes`/`provides_interface` och `consumes_interface` kan användas när explicit graftraversering är värdefull. Samma faktum bör inte dupliceras i flera alternativa relationsriktningar.

## API

API används när egenskaper som `api_style`, `protocol`, `version` och `authentication` är relevanta. Tillåtna MVP-stilar är REST, GraphQL, SOAP, gRPC och `other`.

## Informationsutbyte

`exchanged_information` refererar till `InformationObject`. Modellen ska beskriva betydelsefull information, exempelvis Order eller Customer, inte varje DTO eller schemafält.

## Exempel

```yaml
- id: API-000001
  type: API
  name: Order API
  abstraction_level: logical
  provider: CMP-000001
  consumers:
    - CMP-000002
  api_style: REST
  protocol: HTTPS
  version: v1
  authentication: OIDC
  exchanged_information:
    - INFO-000001
```
