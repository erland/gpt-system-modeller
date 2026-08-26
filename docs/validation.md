# Validering – Plan A steg A25

## Syfte

`scripts/validate.py` är System Modellers samlade MVP-validator för ett uppackat systemprojekt. Den ska användas före rapport-/vygenerering och efter modelländringar.

## Körning

```bash
python3 scripts/validate.py /path/to/system-project
```

Maskinläsbart resultat:

```bash
python3 scripts/validate.py /path/to/system-project --format json
```

Exit code `0` betyder att inga blockerande fel hittades. Warnings kan finnas. Exit code `1` betyder modellfel och `2` ett fel i körning/validator.

## Teknisk grundvalidering

A25 kontrollerar minst:

- att `project.yaml` finns och följer projektets schema,
- YAML-syntax och shardstruktur,
- att alla ID:n följer formatet och är globala/unika,
- element mot typens JSON Schema,
- relationer mot gemensamt relationsschema,
- brutna referenser över filgränser,
- okända element- och relationstyper,
- tillåtna source/target-typer för relationer enligt metamodellen.

## Enkel semantisk validering

MVP-validatorn rapporterar också arkitekturella kvalitetsfynd. Exempel:

- `UseCase` utan aktör eller Responsibility är **ERROR**,
- `Component` utan modellerad koppling till Responsibility/UseCase är **WARNING**,
- `Interface`/`API` utan provider är **ERROR**,
- `RuntimeUnit` utan `deployed_on` är **WARNING**,
- `InformationObject` utan modellerad användning är **WARNING**,
- relation mellan uppenbart inkompatibla elementtyper är **ERROR**.

Warnings är avsiktligt icke-blockerande: en modell får vara ofullständig under pågående reverse engineering, men osäkerheten ska vara synlig.

## Begränsning i A25

A25 är inte en fullständig regelmotor. Djupare completeness-, architecture-rule-, security- och driftanalyser ligger i senare planer. Validatorn ska framför allt hindra trasig modellstruktur och fånga de vanligaste semantiska misstagen tidigt.
