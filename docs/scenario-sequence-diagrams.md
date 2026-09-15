# Scenario-specifika sekvensdiagram

B8 gör sekvensdiagrammen i arkitekturbeskrivningen deterministiska och avgränsade. När standardprofilen har `one_interaction_per_diagram: true` materialiseras exakt en `Interaction` per diagram.

## Regler

- `scripts/sequence_diagrams.py` inventerar kanoniska `Interaction`-element.
- Varje vy använder den befintliga `sequence`-vyn med `filters.interaction_id`.
- Diagram ordnas stabilt efter scenario, därefter Interaction-namn och stabilt ID.
- Titeln är `Scenario – Interaction` när scenario finns, annars Interaction-namnet.
- Deltagare och meddelanden kommer endast från den aktuella Interaction.
- Ingen ny kanonisk information skapas; diagrammen är härledda presentationer.
- Om det inte finns någon Interaction genereras inget sekvensdiagram.

Detta förhindrar att orelaterade scenarier eller interaktioner slås samman till ett enda sekvensdiagram.

## CLI

```bash
python3 scripts/sequence_diagrams.py path/to/system-project
```

Utdata sammanfattar diagramordning, Interaction/Scenario-ID samt antal deltagare och meddelanden. `--format json` ger motsvarande JSON.

## Rapport

`scripts/report.py` använder samma materialisering i kapitlet *Viktiga scenarier*. Varje relevant Interaction får en egen underrubrik och ett eget Mermaid-block.
