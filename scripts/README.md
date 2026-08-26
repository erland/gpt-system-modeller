# scripts

Deterministiska hjälpscript för System Modeller.

Nuvarande scripts:

- `check_structure.py` – verifierar repositorykontraktet genom aktuellt Plan A-steg.
- `test.sh` – kör strukturkontroll och samtliga `tests/test_*.py` som regressionstest.
- `package.py` – bygger en deterministisk utvecklings-ZIP.

Modelloperationer och ID-generering implementeras först i A24; A4 definierar endast formatet och reglerna.

## A24 – modelloperationer

- `ids.py` – allokerar nästa stabila typade ID i ett systemprojekt.
- `model.py` – find/list/add/update/delete samt add/delete relation över projektets YAML-shards.

Se `docs/model-operations.md`.

## validate.py

Validerar ett uppackat systemprojekt tekniskt och semantiskt enligt A25. Se `docs/validation.md`.

```bash
python3 scripts/validate.py /path/to/project
```

## A26 – view.py

Materialiserar de sex kärnvyerna från en systemmodell utan att duplicera kanonisk modellinformation.

```bash
python3 scripts/view.py /path/to/project --type system_context
python3 scripts/view.py /path/to/project --definition /path/to/project/views/system-context.yaml --format json
```

Se `docs/views.md`.

- `view.py`: materialiserar A26/A27-vyer och kan rendera YAML, JSON, Mermaid eller PlantUML.

## report.py

Genererar A28:s första samlade arkitekturbeskrivning i Markdown från ett systemprojekt.

## analyze.py (A29)

`python3 scripts/analyze.py inventory <source-path> [--output inventory.yaml]`

Skapar en deterministisk filinventering för LLM-baserad analys. Scriptet gör ingen semantisk arkitekturinferens; den sker enligt `instructions/source-analysis.md` och `docs/source-analysis.md`.
- `package_custom_gpt.py` – builds the deterministic Custom GPT instructions/Knowledge distribution from the A31 source map.

## `validate_custom_gpt.py` (A33)

Validerar byggd Custom GPT-distribution och, när `--chat` anges, funktionell source-paritet mot Chat-distributionen. Se `docs/custom-gpt-validation.md`.


## CI-build (A34)

`python3 scripts/ci_build.py --output-dir dist` bygger både Chat- och Custom GPT-ZIP, validerar deras paritet och skapar `build-manifest.yaml` med SHA-256. GitHub Actions använder samma entry point.
