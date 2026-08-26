# Stabil ID-hantering och grundläggande modelloperationer (A24)

## Syfte

A24 inför deterministiska operationer för att ändra ett System Modeller-projekt utan att en LLM behöver skriva om YAML-filer godtyckligt. Scriptsen är den föredragna vägen för enkla mekaniska ändringar; semantiska beslut görs fortfarande av LLM/användare.

## Stabil identitet

`ids.py` läser prefixregistret i `metamodel/id-prefixes.yaml`, skannar hela projektet och allokerar nästa lediga sekventiella ID per typ. Ett redan tilldelat ID är permanent för objektets identitet.

- namnbyte bevarar ID,
- `update` tillåter inte ID-byte,
- elementtyp kan inte bytas in-place,
- ID:n är globala inom projektet,
- borttagna ID:n återanvänds inte så länge ett högre nummer finns i projektet.

Exempel:

```bash
python3 scripts/ids.py path/to/system-project --type Component
# CMP-000004
```

## Kanoniska shards

`model.py` placerar nya element i en kanonisk fil utifrån typ. Exempel:

- `System`, `Actor`, `ExternalSystem` → `model/context.yaml`
- `UseCase` → `model/use-cases.yaml`
- `InformationObject` → `model/information.yaml`
- `Component`, `Subsystem`, `Service` → `model/structure.yaml`
- `API`, `Interface`, `Message`, `Event` → `model/integrations.yaml`
- `RuntimeUnit`, `DeploymentNode`, `Environment` → `model/deployment.yaml`
- `ArchitectureDecision`, `Constraint` → `model/decisions.yaml`

Implementation, källor och interaktioner kan skapas i sina respektive kataloger även om filen inte fanns i projekttemplaten från A23.

## Operationer

### Hitta

```bash
python3 scripts/model.py PROJECT find CMP-000001
```

### Lista

```bash
python3 scripts/model.py PROJECT list --type Component
```

### Lägg till

ID kan utelämnas och genereras då automatiskt:

```bash
python3 scripts/model.py PROJECT add --json '{"type":"Component","name":"Payment","abstraction_level":"logical"}'
```

### Uppdatera

```bash
python3 scripts/model.py PROJECT update CMP-000001 --json '{"name":"Order Management"}'
```

ID och elementtyp är stabila och kan inte ändras med `update`.

### Ta bort

```bash
python3 scripts/model.py PROJECT delete CMP-000001
```

Borttagning blockeras om relationer refererar till objektet. `--force` får användas explicit för att även ta bort inkommande/utgående relationer.

### Lägg till relation

```bash
python3 scripts/model.py PROJECT add-relation --json '{"type":"uses","source":"CMP-000001","target":"SVC-000001"}'
```

Källa och mål måste finnas och relations-ID genereras automatiskt om det utelämnas.

### Ta bort relation

```bash
python3 scripts/model.py PROJECT delete-relation REL-000001
```

## Avgränsning

A24 gör mekaniska operationer men ersätter inte A25:s fullständigare tekniska och semantiska validering. Scriptet kontrollerar därför främst identitet, existens och säkra basoperationer.
