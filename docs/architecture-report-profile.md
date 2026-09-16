# Canonical architecture report profile

Plan B steg B5 inför en intern deklarativ standardprofil för arkitekturbeskrivningen.

Profilen finns i `metamodel/report-profiles/standard.yaml` och är den normativa presentationskonfigurationen för standardrapporten. Den kanoniska YAML-modellen för ett system är fortsatt sanningskälla; rapportprofilen styr endast hur modellen presenteras.

## Standardprofil

Profilen låser ordningen och rubrikerna för rapportens tolv sektioner samt vilka standardvyer som hör till respektive sektion. Den innehåller även narrativ stil och diagramregler.

Diagramdelen deklarerar följande budgetar för kommande Plan B-steg:

- preferred max 12 element,
- hard max 20 element,
- preferred max 18 relationer,
- hard max 30 relationer,
- stora vyer ska delas i stället för att enbart krympas,
- sekvensdiagram ska på sikt vara ett Interaction per diagram.

B5 inför kontraktet men **verkställer ännu inte komplexitetsbudgetarna**. Mätning införs i B6 och automatisk uppdelning i B7. Scenario-specifika sekvensdiagram genomförs i B8.

## Intern profil

`user_selectable: false` är avsiktligt. B5 ska ge en enda stabil standard innan stöd för alternativa strukturer eller detaljnivåer övervägs i B11.

`scripts/report_profile.py` laddar och validerar profilen deterministiskt. Regressionstestet verifierar att dagens arkitekturbeskrivning fortfarande följer profilens sektionsstruktur, vilket gör införandet bakåtkompatibelt med A28-rapporten.

## Designregel

Nya presentationsregler som gäller hela arkitekturbeskrivningen ska i första hand uttryckas i standardprofilen och därefter implementeras av rapport-/vymotorn. Regler ska inte spridas som separata, motsägande hårdkodade konstanter.
