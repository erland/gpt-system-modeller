# Custom GPT-builder

## Syfte

A32 implementerar den deterministiska builder som materialiserar A31:s distributionskontrakt. Custom GPT-paketet är en **genererad projektion** och får aldrig bli en separat källa att underhålla.

## Kommando

```bash
python3 scripts/package_custom_gpt.py
```

Standardresultatet är:

```text
distributions/system-modeller-custom-gpt-v0.1.0.zip
```

För granskning kan samma build även materialiseras i en katalog:

```bash
python3 scripts/package_custom_gpt.py \
  --directory /tmp/system-modeller-custom-gpt \
  --output /tmp/system-modeller-custom-gpt-v0.1.0.zip
```

## Genererat innehåll

```text
system-modeller-custom-gpt/
├── instructions.md
├── manifest.yaml
└── knowledge/
    ├── 01-modeling-core.md
    ├── 02-metamodel-reference.md
    ├── 03-project-format-and-validation.md
    ├── 04-views-and-architecture-description.md
    ├── 05-source-analysis-and-evidence.md
    └── 06-reference-example.md
```

`instructions.md` använder den kompakta Chat-runtimeinstruktionen och källanalysinstruktionen som operativ kärna och pekar vidare mot den genererade Knowledge-vägledningen. Knowledge-filerna byggs från A31-kartan och sammanfogar bara kanoniska repositorykällor.

## Manifest och spårbarhet

`manifest.yaml` innehåller:

- versionsnummer från `VERSION`,
- hash för alla källor som faktiskt användes,
- hash och storlek för varje genererad fil,
- A31:s parity-kontrakt,
- generatorns sökväg.

Det gör det möjligt för A33 att verifiera att en Custom GPT-distribution verkligen motsvarar den aktuella repositoryversionen.

## Determinism

ZIP-filer byggs med:

- stabil filordning,
- fast ZIP-timestamp,
- fasta filrättigheter,
- inga utvecklings- eller cachefiler.

Två builds från identiska källor ska därför bli byte-identiska.

## Vad A32 inte gör

A32 validerar builderns struktur och determinism men inför ännu inte den fullständiga Custom GPT/parity-validatorn. Den kommer i A33.
