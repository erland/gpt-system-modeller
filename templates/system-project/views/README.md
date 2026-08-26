# views

Återanvändbara vydefinitioner. Vyer är projektioner av den kanoniska modellen och aldrig en alternativ sanningskälla.

A27-mallen innehåller tio kärnvyer:

- `system-context.yaml`
- `functional-overview.yaml`
- `use-case-overview.yaml`
- `information-overview.yaml`
- `functional-information.yaml`
- `logical-component.yaml`
- `use-case-realization.yaml`
- `integration.yaml`
- `sequence.yaml`
- `deployment.yaml`

Materialisera exempelvis med:

```bash
python3 scripts/view.py /path/to/project --definition /path/to/project/views/system-context.yaml
```

Diagram kan renderas direkt med `--format mermaid` eller `--format plantuml`.
