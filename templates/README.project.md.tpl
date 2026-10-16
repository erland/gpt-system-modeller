# {{GPT_NAME}}

{{PROJECT_DESCRIPTION}}

## Distributioner

Projektet bygger normalt två runtime-distributioner från samma canonical kontrakt:

- Chat ZIP
- Custom GPT

Dessutom byggs en komplett projekt-ZIP.

## Lokal validering

```bash
python scripts/lint_gpt_project.py --project-root .
python -m pytest -q -p no:cacheprovider
python scripts/build_distributions.py --project-root . --version 0.0.0-dev --targets project,chat,custom-gpt
python scripts/validate_distributions.py --project-root .
```

## GitHub Actions

CI körs vid push och pull request. En publicerad GitHub Release med tagg som `v1.0.0` bygger releaseartefakterna med versionen från taggen och bifogar dem till releasen.
