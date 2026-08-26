# Changelog
## 0.1.0-dev.39

- A39: isolate regression tests from outer GitHub release/tag environment.
- Prevent historical fallback-version tests such as A32/A34/A35 from being reinterpreted during `release.published` jobs.
- Preserve explicit release/tag coverage in A36-A38 through test-local environment injection.


## 0.1.0-dev.35 – A35

- Added `scripts/release_check.py` for deterministic double-build, parity, checksum and ZIP-hygiene release verification.
- Added `release-readiness.yaml` as machine-readable readiness output.
- Added v0.1.0 release notes and release-readiness documentation.
- Kept the repository on a development version until an actual release commit/tag is made.
- Explicitly separated local release readiness from real GitHub Actions hosted-runner verification.
- Added A35 regression coverage.


## 0.1.0-dev.34 – A34

- Added `.github/workflows/build-distributions.yml` for pull request, main branch and manual CI.
- Added `requirements-ci.txt` and `scripts/ci_build.py`.
- CI now runs regression tests, builds Chat and Custom GPT distributions, validates parity and uploads both artifacts plus a build manifest.
- Chat distribution default filename is now derived from `VERSION`, matching the Custom GPT builder.
- Added A34 documentation and regression coverage.

## 0.1.0-dev.32 – A32

- Added deterministic `scripts/package_custom_gpt.py`.
- Generates compact Custom GPT `instructions.md`, six Knowledge files and `manifest.yaml` from the A31 distribution map.
- Added source and generated-file SHA-256 traceability to the Custom GPT manifest.
- Added deterministic Custom GPT ZIP packaging and optional materialized build directory.
- Added builder documentation and A32 regression tests.

## 0.1.0-dev.31 – Steg A31

- Definierat Custom GPT-distributionen som en genererad projektion av samma kanoniska källor som Chat-distributionen.
- Fastställt `VERSION` som enda versionskälla och `metamodel/`, `schemas/`, `docs/` samt delade runtime-instruktioner som source of truth.
- Lagt till deklarativ `templates/custom-gpt-distribution.yaml` som mappar kanoniska sources till kompakt instruktion, sex Knowledge-filer och manifest.
- Dokumenterat funktionell parity mellan Chat och Custom GPT utan krav på identiskt ZIP-innehåll.
- Dokumenterat vad som ska exkluderas från Custom GPT Knowledge och krav för kommande A32-builder/A33-validator.
- Lagt till A31-regressionstest för source mapping, version source, Knowledge-bundle och distributionskontrakt.

## 0.1.0-dev.30 – Steg A30 / Plan A MVP komplett

- Skapat realistiskt Order System-referensunderlag med dokumentation, Java/TypeScript, OpenAPI, SQL och deploymentkonfiguration.
- Skapat kvalitetssäkrad golden System Modeller-modell med evidens och declared/observed/inferred.
- Låst golden-resultat för samtliga tio MVP-vyer och den kompletta A28-arkitekturbeskrivningen.
- Lagt till deterministisk `scripts/package_project.py` för portabla systemprojekt-ZIP.
- Lagt till `SYSTEM-MODELLER-CHAT.md`, `instructions/chat-runtime.md` och deterministisk `scripts/package_chat.py`.
- Lagt till A30 end-to-end-test från inventering via validering/vyer/rapport till projekt-ZIP och Chat-ZIP.
- Plan A är därmed komplett och första `system-modeller-chat-v0.1.0.zip` kan användas för praktiskt runtime-test.


## 0.1.0-dev.29 – Steg A29

- Infört normativt analyslager med `Observation` och inbäddade `candidate_concepts`.
- Lagt till `scripts/analyze.py` för deterministisk inventering och prioritering av källkod, dokumentation, API-, databas-, build- och deploymentartefakter.
- Lagt till runtime-instruktioner för hur LLM:n ska skilja observerade fakta från infererad arkitektur och deduplicera mot befintlig modell.
- Utökat validatorn med schema för Observation och projektmallen med `sources/observations.yaml`.
- Dokumenterat MVP-flödet Source → Observation → Evidence → Candidate → Canonical model samt centrala anti-patterns Class=Component, Endpoint=UseCase och Table=InformationObject.
- Lagt till A29-regressionstest med både dokument- och kodinventering samt validering av observationer.

## 0.1.0-dev.26 – Plan A steg A26

## 0.1.0-dev.27

- Added Use Case Realization, Integration, Sequence and Deployment views.
- Extended the reusable view schema/templates from six to ten MVP architecture views.
- Added dynamic materialization of Interaction participants/messages for sequence views.
- Added derived integration/use-case-realization links from canonical reference fields.
- Added Mermaid and PlantUML rendering to `scripts/view.py`.

- Definierar generellt vyformat och schema.
- Implementerar sex kärnvyer: System Context, Functional Overview, Use Case Overview, Information Overview, Functional–Information och Logical Component.
- Lägger till `scripts/view.py` för neutral materialisering av vyer i YAML/JSON.
- Lägger till standarddefinitioner, dokumentation, exempel och regressionstest.
# Changelog

## 0.1.0-dev.23 – Steg A23

- Definierat ett portabelt systemprojektformat separat från GPT-paketet.
- Infört obligatorisk `project.yaml` med projekt-ID, schema/model-version, språk och standardvyprofil.
- Definierat kanoniska YAML-shards under `model/` och globala ID-/referensregler över filgränser.
- Definierat kataloger för interactions, implementation, sources, views, reports, issues och exports.
- Fastställt att `exports/` endast innehåller genererade artefakter och aldrig är kanonisk modellkälla.
- Lagt till `schemas/project.schema.json`, `metamodel/project-format.yaml`, normativ guide, systemprojektmall, exempelprojekt och A23-regressionstest.

## 0.1.0-dev.22 – Steg A22

- Gjort `origin` till en normativ och maskinvaliderad dimension på modellobjekt och relationer.
- Infört värdena `declared`, `observed`, `inferred`, `user_confirmed` och `unresolved`.
- Tillåtit flera origin-värden så samma kanoniska påstående exempelvis kan vara både dokumenterat och observerat.
- Dokumenterat tydlig separation mellan `origin` och A21:s `Evidence.status`.
- Definierat regler för infererad arkitektur, användarbekräftelse och unresolved-status.
- Lagt till `metamodel/origin.yaml`, `schemas/origin.schema.json`, normativ dokumentation, exempel och A22-regressionstest.

## 0.1.0-dev.21 – Steg A21

- Infört separat provenance-lager med `Source`, `SourceReference` och `Evidence`.
- Aktiverat `SRC-*`, `REF-*` och `EVD-*` i ID-registret.
- Infört källtyper för kod, dokumentation, användaruppgift, API-specifikation, databasschema och konfiguration.
- Infört exakta locator-fält för kod och dokument.
- Infört evidence-status `source_confirmed`, `user_confirmed`, `inferred`, `assumed`, `unresolved` samt confidence.
- Fastställt att modellobjekt/relationer refererar Evidence med EVD-ID, medan provenance-poster hålls utanför arkitekturens abstraktionsnivåer.
- Lagt till normativ guide, JSON Schema, exempel och A21-regressionstest.

## 0.1.0-dev.20 – Steg A20

- Infört `ArchitectureDecision` och `Constraint` som förstaklassobjekt.
- Infört beslutstatus, context, decision, rationale, alternatives och consequences för arkitekturbeslut.
- Infört constraint-kategorier och explicit regel/statement.
- Infört `affects` samt `affected_elements` för spårbar påverkan på modellen.
- Aktiverat `ADR-*` och `CON-*` i ID-registret.
- Lagt till normativ guide, JSON Schema, exempel och A20-regressionstest.

## 0.1.0-dev.19 – Steg A19

- Aktiverat `deployed_on` från `RuntimeUnit` till `DeploymentNode`.
- Aktiverat `belongs_to` från `DeploymentNode` till `Environment`.
- Infört `connects_to` från `RuntimeUnit` till `RuntimeUnit`, `DataStore` eller `ExternalSystem`.
- Lagt till frivilliga kommunikationsegenskaper för protokoll, riktning, kryptering, syfte och utbytta `InformationObject`.
- Fastställt riktning och abstraktionsregler för en övergripande deployment-vy utan onödig infrastrukturdetalj.
- Lagt till normativ guide, uppdaterat schema, A19-exempel och regressionstest.

## 0.1.0-dev.18 – Steg A18

- Infört `Environment` på runtime-nivån med development, test, staging, production och other.
- Infört `DeploymentNode` på runtime-nivån med övergripande nodtyper för klient, server, VM, containerplattform, molntjänst, databasplattform och extern plattform.
- Aktiverat stabila `ENV-*`- och `NODE-*`-ID:n.
- Reserverat `deployed_on` och `belongs_to` till A19 för att hålla elementdefinition och deploymenttopologi separerade.
- Lagt till normativ guide, JSON Schema, exempel och A18-regressionstest.

## 0.1.0-dev.17 – Steg A17

- Infört `RuntimeUnit` på runtime-abstraktionsnivån.
- Infört runtime-typer för web application, application service, background service, batch job, database, message broker och function.
- Infört den kanoniska relationen `realized_as` från `Component`, `Service` och `DataStore` till `RuntimeUnit`.
- Fastställt gränsdragningen mellan logisk arkitektur, runtime och kommande deploymentnoder.
- Lagt till frivilliga runtime-attribut för purpose, technology, artifact och instance scope.
- Aktiverat `RUN-*` i ID-registret och lagt till schema, normativ guide, exempel och A17-regressionstest.

## 0.1.0-dev.16 – Steg A16

- Infört `InteractionMessage` som inbäddat dynamiskt objekt i `Interaction`.
- Infört stabila `IM-*`-ID:n och explicit `order` för sekvensordning.
- Infört `sender`, `receiver`, `label`, `operation` och synkron/asynkron kommunikationssemantik.
- Infört valfri koppling till `InformationObject`, villkor samt A12 `Message`/`Event` via `message_ref`.
- Fastställt att sender/receiver ska vara deltagare i samma Interaction och att stegen ska hållas på arkitekturellt relevant detaljnivå.
- Lagt till uppdaterat schema, normativ guide, A16-exempel och regressionstest.

## 0.1.0-dev.14 – Steg A14

- Infört `Scenario` på konceptuell abstraktionsnivå.
- Infört kopplingar till UseCase, Actor, InformationObject, Component och ExternalSystem.
- Infört frivillig trigger och obligatoriskt outcome för begripligt end-to-end-syfte.
- Infört relationerna `scenario_for`, `involves` och `involves_information`.
- Lagt till schema, normativ guide, exempel och A14-regressionstest.

## 0.1.0-dev.13 – Steg A13

- Infört `DataStore` på logisk abstraktionsnivå.
- Infört lagringstyper för relationsdatabas, dokumentlager, objektlagring, sökindex, cache, fillagring och meddelandelager.
- Infört `owner`, frivillig `technology` och `authoritative_for`.
- Infört relationerna `stores_information`, `accesses` och `owns_data_store`.
- Aktiverat A9:s informationsanvändningspar för `DataStore` och städat kvarvarande planmarkering för API från A11.
- Lagt till schema, normativ guide, exempel och A13-regressionstest.

## 0.1.0-dev.12 – Steg A12

- Infört `Message` och `Event` på logisk abstraktionsnivå.
- Infört producent/konsument-modellering och explicit `communication_mode` för meddelanden.
- Fastställt att events är asynkrona i MVP:n.
- Infört relationerna `sends`, `receives`, `publishes` och `subscribes`.
- Lagt till koppling till konceptuella `InformationObject` via `exchanged_information`.
- Lagt till frivilliga `channel`, `topic` och `protocol` utan att ännu göra fysisk messaging-infrastruktur till egna modellobjekt.
- Lagt till schema, normativ guide, exempel och A12-regressionstest.

## 0.1.0-dev.10 – Steg A10

- Infört `Subsystem`, `Component` och `Service` på logisk abstraktionsnivå.
- Infört strukturella relationer `contains`, `part_of`, `depends_on`, `uses` och `provides`.
- Aktiverat realisering mellan `Responsibility` och `Component` via `realized_by`/`realizes`.
- Aktiverat A9:s informationsanvändningsrelationer för `Component` och `Service`.
- Dokumenterat tydliga gränser mot kodstruktur och framtida runtime/deploymentmodell.
- Lagt till logiskt schema, normativ guide, exempel och A10-regressionstest.


## 0.1.0-dev.9 – Steg A9

- Infört explicita informationsanvändningsrelationer för create/read/update/delete.
- Infört relationer för ownership, mastering, storage och exchange av `InformationObject`.
- Fastställt kanonisk riktning: arkitekturelement → InformationObject.
- Deklarerat framtida relationspar till Component, Service, API och DataStore utan att aktivera ännu ej införda elementtyper i schemat.
- Dokumenterat hur `UseCase.related_information` samspelar med mer precisa informationsrelationer.
- Lagt till schema, exempel och A9-regressionstest.
## 0.1.0-dev.8 – A8

- Added normative `InformationObject` metamodel and schema.
- Added conceptual information relationships: `contains_information`, `references_information`, `relates_to_information`, `derived_from_information`.
- Added information modeling guide and example.
- Tightened `UseCase.related_information` to INFO references now that InformationObject exists.
- Added A8 regression tests.


Alla väsentliga ändringar i **System Modeller** dokumenteras här.

## 0.1.0-dev.1 – Steg A1

- Skapat grundrepository för System Modeller.
- Etablerat katalogstruktur för instruktioner, metamodell, schemas, scripts, mallar, exempel, tester, dokumentation och distributioner.
- Dokumenterat grundläggande designprinciper för MVP:n.
- Lagt till versionsfil och statusdokument.
- Lagt till deterministiskt paketeringsscript för utvecklings-ZIP.
- Lagt till grundläggande strukturkontroll och smoke test.

## 0.1.0-dev.2 – Steg A2

- Definierat normativ MVP-målbild och scope för Plan A.
- Dokumenterat primära målgrupper och användningsfall.
- Fastställt kärnkoncept och arkitekturvyer som ska stödjas i MVP:n.
- Fastställt att en övergripande runtime- och deploymentmodell ingår i MVP:n.
- Dokumenterat relationen till UML, C4 och klassiska arkitekturvyer.
- Dokumenterat explicit out-of-scope för Plan A för att hålla MVP:n avgränsad.
- Fastställt Definition of Done och designbeslut som A2 låser inför kommande steg.
- Rättat A1-paketeringskontraktet så att genererade `distributions/` inte krävs efter uppackning och exekverbara scripts behåller körbar filrättighet i ZIP.

## 0.1.0-dev.3 – Steg A3

- Definierat normativa abstraktionsnivåer: conceptual, logical, runtime och implementation.
- Definierat gränsdragning mellan System, ExternalSystem, Subsystem, Component, Service, Module och Responsibility/SystemFunction.
- Definierat modelleringsregler för UseCase, Actor och InformationObject.
- Definierat hur Scenario/Interaction samt RuntimeUnit, DeploymentNode och Environment ska användas på MVP-nivå.
- Definierat en explicit abstraktionsprocess från kodobservationer till logiska och konceptuella modellkandidater.
- Dokumenterat regler för gruppering, deduplicering, osäkerhet och namngivning.
- Dokumenterat vy-specifika regler och centrala antimönster såsom Class=Component, Endpoint=UseCase och Table=InformationObject.
- Fastställt beslutsregeln att välja högsta abstraktionsnivå som bevarar nödvändig systemförståelse.

## 0.1.0-dev.4 – Steg A4

- Definierat gemensam baskonstruktion för alla modellobjekt.
- Infört formellt JSON Schema för stabila ID:n, abstraktionsnivåer, modellobjekt och relationer.
- Definierat relationer som förstaklassobjekt med egna ID:n, source/target och stöd för evidens/metadata.
- Infört provisoriskt prefixregister för Plan A:s förväntade modelltyper.
- Dokumenterat stabil ID-strategi, referensintegritet och extensionsprincip.
- Lagt till ett A4-exempel som valideras mot basschemat.
- Lagt till A4-regressionstester för schema, ID-regler, metamodell och dokumentationskontrakt.
- Gjort A3-versionstestet regressionssäkert för senare Plan A-versioner.

## 0.1.0-dev.5 – Steg A5

- Definierat `System`, `ExternalSystem` och `Actor` som första domänspecifika konceptuella modelltyper.
- Fastställt `ACT`, `SYS` och `EXT` som typade ID-prefix i kontextmodellen.
- Definierat Actor-kategorierna person, role, organization och external_technical_actor.
- Infört kontextrelationerna `uses`, `interacts_with` och `exchanges_information_with` med tillåtna source/target-par.
- Dokumenterat systemgräns, klassificeringsregler och anti-dubblettprincip för Actor kontra ExternalSystem.
- Lagt till `schemas/context.schema.json`, `metamodel/context.yaml` och ett validerat kontextexempel.
- Lagt till A5-regressionstest och uppdaterat README/status för nästa Plan A-steg.


## 0.1.0-dev.6 – Steg A6

- Definierat `Responsibility` som kanonisk modelltyp med `SystemFunction` som synonymbegrepp.
- Fastställt att Responsibility ligger på konceptuell nivå och beskriver vad systemet ansvarar för, inte hur det implementeras.
- Infört relationen `has_responsibility` mellan `System` och `Responsibility`.
- Dokumenterat framtida relation till `UseCase` (A7) och `Component` (A10) utan att aktivera typerna i förtid.
- Lagt till `metamodel/functions.yaml`, `schemas/functions.schema.json`, normativ dokumentation och validerat exempel.
- Lagt till A6-regressionstest.
- Gjort A5-versionstestet regressionssäkert för senare Plan A-versioner.

## 0.1.0-dev.7 – Steg A7

- Definierat `UseCase` som konceptuell modelltyp för mål- och värdeorienterat systembeteende.
- Gjort `primary_actor`, `responsibility` och `outcome` obligatoriska i MVP-formatet.
- Lagt till valfritt stöd för supporting actors, trigger, preconditions och postconditions utan krav på fullständig use-case-specifikation.
- Infört relationerna `performs` och `groups_use_case` samt valfria UML-liknande `includes`, `extends` och `specializes`.
- Dokumenterat att endpoints, knapptryckningar och service-metoder är evidens snarare än automatiska use cases.
- Förberett stabila framåtreferenser till information och teknisk realisering som typvalideras i senare steg.
- Lagt till `metamodel/use-cases.yaml`, `schemas/use-cases.schema.json`, normativ use-case-guide, exempel och A7-regressionstest.

## 0.1.0-dev.15 – Steg A15

- Definierat `Interaction` som logisk dynamisk realisering av ett konceptuellt `Scenario`.
- Definierat `Participant` som inbäddad referens/roll till befintliga Actor, System, ExternalSystem, Component, Service eller DataStore i stället för som duplicerat modellobjekt.
- Infört relationerna `realizes_scenario` och `has_participant` för grafbaserade vyer och frågor.
- Fastställt minst två deltagare per Interaction i MVP-formatet samt tydlig gräns mot ordnade `InteractionMessage` som införs i A16.
- Lagt till `metamodel/interactions.yaml`, `schemas/interactions.schema.json`, normativ dokumentation, validerat exempel och A15-regressionstest.

## 0.1.0-dev.24 – Plan A steg A24

- Implementerar stabil typbaserad ID-allokering i `scripts/ids.py`.
- Implementerar deterministiska grundoperationer i `scripts/model.py`: find/list/add/update/delete och relationshantering.
- Bevarar ID vid namnbyte och blockerar ID-/typbyte via update.
- Blockerar osäker borttagning av refererade objekt om inte `--force` används explicit.
- Dokumenterar kanonisk shardplacering och scriptens avgränsning inför A25.
- Lägger till A24-regressionstest.

## 0.1.0-dev.33 – A33

- Added `scripts/validate_custom_gpt.py` for Custom GPT package validation.
- Added Chat/Custom parity validation against shared `metamodel/` and `schemas/` sources.
- Tightened Custom GPT instruction budget to 8,000 characters.
- Extended Custom GPT manifest source hashes to cover all parity-critical metamodel/schema files.
- Added `docs/custom-gpt-validation.md` and A33 regression tests.

## 0.1.0-dev.36 – A36

- Infört gemensam versionsresolver i `scripts/versioning.py`.
- Gjort GitHub release/tagg `vX.Y.Z` auktoritativ för releasebyggen.
- Behållit `VERSION` som fallback för lokal utveckling och vanliga branch/PR-builds.
- Lagt till `--release-version` och `SYSTEM_MODELLER_RELEASE_VERSION` för lokal releasesimulering.
- Säkerställt att taggen styr Chat-ZIP, Custom GPT-ZIP, inbäddad Chat `VERSION`, Custom GPT-instruktion/manifest och build-manifest.
- Utökat GitHub Actions-workflowen med taggtrigger och validerad taggexport.
- Lagt till dokumentation och A36-regressionstest.

### Repository cleanup after A36
- Removed the superseded `examples/a23-system-project/`; the maintained system-project template and A30 reference project cover the same purpose.
- Removed the generated binary `examples/reference-order-system/golden/reference-order-system.zip`; A30 now verifies deterministic project packaging by comparing two independently generated ZIPs.
- Removed transient Python/macOS/editor artifacts where present.
- Retained step-labelled regression tests and focused YAML examples because they are still actively referenced by the regression suite and document isolated metamodel features.

## 0.1.0-dev.37 – A37

- Ändrat GitHub Actions-trigger från tagg-push till `release: types: [published]` för normala releaser.
- Behållit verifiering vid `pull_request`, push till `main` och manuell `workflow_dispatch`.
- Delat workflowen i read-only `verify`, read-only `build-check` och ett separat release-jobb med `contents: write`.
- Låtit release-jobbet checka ut exakt release-taggen och använda den som auktoritativ versionskälla.
- Lagt till uppladdning av Chat-ZIP, Custom GPT-ZIP och `build-manifest.yaml` som riktiga GitHub Release-assets via `gh release upload`.
- Utökat `scripts/versioning.py` med `github_release` som explicit versionskälla.
- Lagt till A37-regressionstest och uppdaterad CI/releasedokumentation.


## 0.1.0-dev.38 – A38

- Rättat CI-eftervalideringen så utvecklingsversioner som `0.1.0-dev.38` accepteras som distributionsversioner vid push till `main` och manuell build.
- Behållit strikt `vX.Y.Z`/`X.Y.Z`-validering för faktiska release-taggar.
- Infört `normalize_distribution_version()` som skiljer redan resolverade distributionsversioner från release-taggar.
- Uppdaterat `validate_custom_gpt.py` att använda distributionsvalidering för `--expected-version`.
- Lagt till regressionstest som reproducerar A36-felet och verifierar både dev- och releaseväg.