# Designprinciper – System Modeller A1

Detta dokument fastställer de övergripande designprinciper som ska gälla genom hela MVP-arbetet. Den normativa detaljeringen av abstraktionsnivåer, begreppsgränser och modelleringsregler finns från steg A3 i [`modeling-principles.md`](modeling-principles.md).

## 1. YAML är sanningskällan

Den kanoniska systemmodellen ska lagras i YAML. Diagram, rapporter, index och exporter ska betraktas som härledda artefakter som kan återskapas.

## 2. Modell och vy är separata

Systemmodellen beskriver fakta och semantik. En vy beskriver vilket urval och vilken abstraktionsnivå som ska presenteras för en viss målgrupp eller fråga.

Det ska därför vara möjligt att skapa flera olika vyer från samma modell utan att duplicera modellinformationen.

## 3. GPT-paket och systemprojekt är separata

**System Modeller-paketet** innehåller regler, schemas, scripts, instruktioner, tester och mallar.

**Systemprojektet** innehåller modellen, källreferenser, vydefinitioner och rapportkonfiguration för ett konkret system.

De två ska kunna versioneras och distribueras oberoende av varandra.

## 4. Stabila ID:n

Alla förstaklassobjekt och relationer ska med tiden få stabila tekniska ID:n. Ett namnbyte får inte innebära att modellobjektets identitet ändras.

Den konkreta ID-strategin definieras i senare Plan A-steg.

## 5. Evidens och osäkerhet är förstaklasskoncept

Modellen ska kunna skilja mellan sådant som:

- uttryckligen anges av användaren,
- finns dokumenterat,
- observeras i kod eller konfiguration,
- härleds av LLM:n,
- ännu är osäkert eller motsägelsefullt.

Viktiga modellpåståenden ska kunna spåras till sitt underlag.

## 6. Systemförståelse före maximal detalj

System Modeller ska i första hand hjälpa en människa att förstå:

- vad systemet gör,
- för vem,
- vilken information det hanterar,
- hur det är uppbyggt,
- hur huvuddelarna samverkar,
- hur det övergripande körs och deployas.

Källkodens klass-, metod- och filstruktur ska därför inte automatiskt bli den logiska arkitekturen.

## 7. Flera abstraktionsnivåer ska kunna samexistera

MVP:n kommer successivt att stödja minst:

- konceptuell nivå,
- logisk nivå,
- runtime/deploymentnivå,
- implementationsnivå.

Relationer mellan nivåerna ska bevara spårbarhet utan att blanda ihop deras semantik.

## 8. Fakta och inferens hålls isär

Ett påstående som är observerat i kod är inte samma sak som ett modellerat arkitekturansvar. En LLM-baserad gruppering eller tolkning ska därför markeras som inferens tills den bekräftats eller har tillräcklig evidens.

## 9. Determinism där det är möjligt

Operationer som exempelvis validering, ID-hantering, paketering och senare queries ska i första hand implementeras i deterministiska scripts.

LLM:n används där semantisk tolkning och abstraktion krävs.

## 10. Komplett ZIP som arbetsenhet

I Chat-distributionen ska ett ändrat projekt normalt returneras som ett komplett ZIP-paket som kan användas som ingång i nästa konversation eller utvecklingssteg.
