# Scenario

`Scenario` beskriver ett viktigt **end-to-end-förlopp** på konceptuell nivå. Det används för att förklara hur systemet fungerar utan att ännu gå ned på ordnade tekniska meddelanden; den detaljen kommer i `Interaction` i A15–A16.

Ett scenario bör väljas när det realiserar ett centralt `UseCase`, korsar viktiga system- eller komponentgränser, visar ett viktigt integrationsflöde eller på annat sätt gör arkitekturen lättare att förstå.

## Referenser

Ett Scenario kan knytas till `UseCase`, `Actor`, `InformationObject`, `Component` och `ExternalSystem`. De kan uttryckas i scenariofält för kompakt läsning och materialiseras som relationerna `scenario_for`, `involves` och `involves_information` för vyer och frågor. Dessa representationer ska vara konsistenta.

## Fält

- `outcome` är obligatoriskt och beskriver det meningsfulla resultatet.
- `trigger` är valfritt.
- `use_case` är valfri referens till ett `UseCase`.
- `actors`, `information`, `components` och `external_systems` är valfria referenslistor.

## Avgränsning

Scenario är inte ett komplett processdiagram och ska inte beskriva varje teknisk gren. Ordning, sender/receiver och synkron/asynkron kommunikation hör till kommande `Interaction`/`InteractionMessage`.
