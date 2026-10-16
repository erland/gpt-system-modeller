# Fas 8 – System Modeller (GPT Byggaren 1.6.25)

**Status:** Arbetskopia, inte godkänd releasekandidat.

## Genomförd migrering

- Åtta nya 1.6.25-kontrakttester i `tests/test_migration_1625.py`, som motsvarar de historiska A34, A39, B12, C1, C2, C5, C6, C7 på kontraktsnivå. Gamla källtester bevaras och är inte omdöpta till godkända tester.
- Muterande modellverktyg har fått `approval_required: true` i projektkontraktet och tillhörande JSON-schema accepterar explicit godkännande.
- CI/release-rättigheter, fem moderna distributionsmål, runtimeparitetskonfiguration och release-spärr testas utan Custom GPT-beroende.

## Faktiska kontroller

- 15 pytest-tester PASS (inklusive åtta nya kontroller), två deprecationsvarningar.
- `validate_project_contract.py`: PASS.
- `lint_gpt_project.py`: PASS, 0 fel och 0 varningar efter rensning av genererade cachefiler.
- `build_distributions.py --version 0.1.0-phase8`: PASS, fem distributioner och en projekt-ZIP.
- `validate_distributions.py`: PASS.
- A/B/C-standalone regression: INTE VERIFIERAD; körningen överskred den tillgängliga körgränsen. Ingen falsk grönmarkering eller dispens.

## Kvarstår före release

1. Fullfölj den tidsbudgeterade A/B/C-körningen i CI med separata loggar och identifiera faktiska fel kontra långsam exekvering.
2. Verifiera funktionsmässig runtimeparitet, inte bara arkivstruktur och konfigurationskontrakt.
3. Kör full releasekedja inklusive slutliga checksums och provinstallation.

Ingen GitHub-publicering har gjorts.
