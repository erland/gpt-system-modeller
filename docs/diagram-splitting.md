# Automatisk diagramuppdelning

B7 delar materialiserade vyer som överskrider standardprofilens preferred-budget innan de renderas. Den kanoniska YAML-modellen ändras aldrig av uppdelningen.

## När uppdelning sker

`scripts/view_split.py` använder B6-mätningen. En vy delas när:

- vytypen stöds av B7,
- `split_recommended` är `true`,
- standardprofilen har `split_large_views: true`.

Prioriterade vyer är:

- `logical_component`,
- `integration`,
- `deployment`,
- `functional_information`.

## Semantiska ankare

Uppdelningen försöker först använda modellerad struktur:

- Logical Component: `Subsystem`,
- Functional–Information: `Responsibility`,
- Deployment: `Environment`, annars `DeploymentNode`,
- Integration: provider/producer-noder (`System`, `ExternalSystem`, `Component`, `Service`) som deltar i relevanta integrationsrelationer.

Övriga element tilldelas deterministiskt till närmaste ankare i den materialiserade grafen. Vid lika avstånd vinner det lexikografiskt minsta stabila ID:t.

## Fallback

Om semantiska ankare saknas delas elementen i stabil ID-ordning. Chunkningen respekterar både preferred elementbudget och preferred relationsbudget så långt den inducerade delgrafen tillåter.

## Huvudvy och delvyer

En split producerar:

1. en eller flera översiktsvyer,
2. därefter detaljvyer i stabil ordning.

Översikten visar ankare när sådana finns. Vid fallback används en stabil representant per detaljdel. Detaljvyerna täcker samtliga element från ursprungsvyn; endast relationer där båda ändpunkterna finns i samma delvy visas i just den delvyn.

Arkitekturbeskrivningen renderar de separata delvyerna som egna Mermaid-block med underrubriker. Små vyer renderas exakt som tidigare.

## Avgränsning

B7 delar statiska vyer. Sekvensdiagram hanteras separat i B8, där ett Interaction ska generera ett eget diagram.
