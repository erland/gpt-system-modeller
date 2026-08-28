# MVP-referens och end-to-end-test (A30)

A30 avslutar Plan A genom att låsa ett litet men komplett referenssystem och ett reproducerbart end-to-end-test för System Modeller v0.1.0 MVP.

## Referenssystem

`examples/reference-order-system/` innehåller tre lager:

- `input/` – liten dokumentations-, kod-, API-, SQL- och deploymentbas som representerar det material en LLM kan analysera,
- `project/` – den kvalitetssäkrade kanoniska System Modeller-modellen,
- `golden/` – förväntad inventering, tio materialiserade vyer, arkitekturbeskrivning och portabel projekt-ZIP.

Systemet omfattar kund, order, betalning, leverans, logiska komponenter, REST-API, event, datalager, scenario/interaktion och övergripande deployment.

## End-to-end-kedja

A30-testet verifierar:

```text
Input material
  ↓ scripts/analyze.py inventory
Source inventory
  ↓ LLM-semantik representerad av golden model
Canonical YAML model
  ↓ scripts/validate.py
Validated project
  ↓ scripts/view.py
10 architecture views
  ↓ scripts/report.py
Architecture description
  ↓ scripts/package_project.py
Portable system-project ZIP
```

Det semantiska LLM-steget testas i A30 genom en manuellt kvalitetssäkrad golden model. Det är avsiktligt: MVP:n ska kunna bedöma om en LLM producerar rätt abstraktionsnivå utan att låtsas att deterministiska scripts gör semantisk inferens.

## Golden-vyer

Följande vyer finns både som neutral YAML och Mermaid:

1. System Context
2. Functional Overview
3. Use Case Overview
4. Information Overview
5. Functional–Information
6. Logical Component
7. Use Case Realization
8. Integration
9. Sequence
10. Deployment

## Chat-ZIP

`scripts/package_chat.py` bygger `system-modeller-chat-v0.1.0.zip`.

Chat-ZIP:en innehåller runtime-instruktioner, metamodell, schemas, relevanta runtime-scripts, mallar, exempel och runtime-relevant dokumentation. Utvecklingstester, CI/releaseverktyg och release-dokumentation exkluderas. `SYSTEM-MODELLER-CHAT.md` är startpunkten när paketet bifogas i en vanlig chat.

Chat-ZIP och systemprojekt-ZIP är olika artefakter och får inte blandas ihop.

## Godkännandekriterium

Plan A är tekniskt godkänd när:

- referensprojektet validerar med 0 errors och 0 warnings,
- alla tio vyer reproducerar golden-resultatet,
- arkitekturbeskrivningen reproduceras byte-identiskt,
- projekt-ZIP kan packas upp och valideras på nytt,
- två Chat-ZIP-builds blir byte-identiska,
- hela A1–A30-regressionssviten passerar.

Det praktiska nästa testet är att starta en ny chat med Chat-ZIP:en och ge den ett verkligt systemunderlag.
