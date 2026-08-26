# Informationsanvändning – A9

## Syfte

A9 gör användningen av konceptuell information explicit. Det räcker inte att veta att ett use case eller en systemdel är relaterad till **Order**; modellen ska kunna uttrycka om informationen skapas, läses, uppdateras, tas bort, ägs, mastras, lagras eller utbyts.

## Kanonisk riktning

För alla informationsanvändningsrelationer är `source` det arkitekturelement som utför handlingen eller bär ansvaret och `target` ett `InformationObject`.

Exempel:

```yaml
- id: REL-000010
  type: creates_information
  source: UC-000001
  target: INFO-000001
```

## Relationer

- `creates_information` – skapar information.
- `reads_information` – läser/konsumerar information.
- `updates_information` – förändrar information.
- `deletes_information` – tar bort/avslutar information.
- `owns_information` – har övergripande informationsansvar.
- `masters_information` – är master/auktoritativ källa.
- `stores_information` – lagrar information.
- `exchanges_information` – deltar i utbyte av information.

## Aktivt stöd i A9

Relationerna kan användas med de typer som redan finns: `System`, `ExternalSystem`, `Actor`, `Responsibility` och `UseCase`, när semantiken är meningsfull. `stores_information` hålls i A9 främst till systemnivå tills `DataStore` införs.

Planen kräver också koppling till `Component`, `Service`, `API` och `DataStore`. Dessa par är därför deklarerade i metamodellen nu, men full schema- och typvalidering aktiveras först i A10, A11 respektive A13.

## Relation till UseCase.related_information

`UseCase.related_information` är fortsatt en enkel relevanslista. Den ska inte användas som ersättning för känd CRUD-semantik. Om use caset faktiskt skapar Order ska `creates_information` användas. Om den exakta användningen är okänd kan `related_information` räcka tills modellen kan förfinas.

## Abstraktionsregel

Relationerna beskriver verksamhetsmässig informationsanvändning. De ska inte användas för att modellera att en klass läser en tabell eller att ett API råkar serialisera ett visst DTO-format. Sådant hör till implementations- eller evidenslagret.
