# DataStore – A13

## Syfte

`DataStore` beskriver **arkitekturellt relevant lagring på logisk nivå**. Målet är att visa var centrala `InformationObject` bevaras och vilka systemdelar som använder lagret, utan att blanda in varje tabell, collection eller fysisk databasinstans.

## DataStore

Ett DataStore har stabilt `DS-*`-ID, `abstraction_level: logical` och en `store_kind`. MVP:n stödjer:

- `relational_database`
- `document_store`
- `object_storage`
- `search_index`
- `cache`
- `file_storage`
- `message_store`
- `other`

Valfria egenskaper är `owner`, `technology` och `authoritative_for`. `technology` är tills vidare text, så exempelvis PostgreSQL kan anges utan att teknikmodellen behöver finnas ännu.

## Relationer

### stores_information

`DataStore → InformationObject` visar vilken konceptuell information som lagras. Relationens mål är alltid ett `InformationObject`, inte en tabell eller DTO.

### accesses

`System | ExternalSystem | Component | Service → DataStore` visar arkitekturellt relevant åtkomst. Relationens syfte är systemförståelse, inte kodnära dependency mapping.

### owns_data_store

`System | Component → DataStore` visar arkitekturellt ägaransvar. Det kan komplettera `owner`-fältet när traverserbar relation behövs. De två representationerna får inte motsäga varandra.

## Information ownership

`authoritative_for` kan markera att lagret är auktoritativ lagringsplats för ett eller flera `InformationObject`. Detta ska inte förväxlas med verksamhetsmässigt ägarskap av informationen; sådant uttrycks med informationsmodellens ownership/mastering-semantik.

## Abstraktionsregel

En fysisk PostgreSQL-instans, Kubernetes StatefulSet eller molndatabastjänst är inte automatiskt samma objekt som det logiska DataStore. A17–A19 inför runtime/deployment och kan senare visa var lagringen faktiskt körs.

En `DatabaseTable` tillhör implementationsnivån och får endast användas som evidens för ett DataStore eller InformationObject om abstraktionen är motiverad.
