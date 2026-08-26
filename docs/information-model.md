# Informationsmodell – A8

## Syfte

`InformationObject` beskriver verksamhetsmässigt betydelsefull information som behövs för att förstå vad systemet hanterar. Modellen ska ligga på konceptuell nivå och får inte reduceras till tekniska lagrings- eller kodstrukturer.

## InformationObject

Exempel på bra informationsobjekt är **Kund**, **Order**, **Produkt**, **Betalning** och **Leverans**. Ett informationsobjekt ska vara begripligt även för en läsare som inte känner implementationen.

Följande är normalt inte InformationObject i sig:

- databastabellen `ORDER_T`,
- klassen `OrderEntity`,
- DTO:n `CreateOrderRequest`,
- JSON-filen `orders.json`.

De kan senare fungera som implementation eller evidens för informationsobjektet **Order**. Därför gäller antimönstret **Table = InformationObject** inte.

## Egenskaper

Utöver den gemensamma modellbasen kan InformationObject använda:

- `owner` – den del som har informationsansvar, om känt,
- `master` – den del som är master/auktoritativ för informationen, om känt,
- `lifecycle` – relevanta verksamhetsmässiga livscykelfaser,
- `classification` – enkel MVP-klassificering,
- `authoritative_source` – referens till auktoritativ källa när den är känd,
- `related_stores` – framtida koppling till DataStore.

Egenskaper som inte är tillräckligt kända ska hellre utelämnas än gissas. Evidens och confidence formaliseras i A21–A22.

## Informationsrelationer

A8 introducerar fyra relationer mellan informationsobjekt:

- `contains_information` – komposition/innehåll,
- `references_information` – referens utan komposition,
- `relates_to_information` – generell semantisk relation,
- `derived_from_information` – härledd information.

Relationerna ska användas sparsamt. Om relationen egentligen beskriver hur en funktion eller komponent använder information ska det senare uttryckas genom informationsanvändningsrelationerna i A9.

## Abstraktionsregel

Informationsmodellen ska svara på **vilken information systemet hanterar**, inte hur informationen råkar vara lagrad eller representerad i kod. Flera tabeller, klasser eller meddelandescheman kan därför stödja samma konceptuella InformationObject.
