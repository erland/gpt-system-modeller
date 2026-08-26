# Custom GPT-validering och paritet (A33)

## Syfte

A33 verifierar att den genererade Custom GPT-distributionen är komplett, kompakt, spårbar och funktionellt synkad med Chat-distributionen.

Valideringen förändrar inte någon kanonisk modellkälla. Den kontrollerar byggda distributioner mot repositoryts source-of-truth.

## Validator

```bash
python3 scripts/validate_custom_gpt.py \
  --custom distributions/system-modeller-custom-gpt-v0.1.0.zip \
  --chat distributions/system-modeller-chat-v0.1.0.zip
```

`--custom` kan peka på ZIP eller en materialiserad Custom GPT-katalog. `--chat` är frivillig men ska användas vid release/paritetskontroll.

JSON-output:

```bash
python3 scripts/validate_custom_gpt.py --custom ... --chat ... --json
```

## Kontroller

Validatorn kontrollerar minst:

- korrekt ZIP-root,
- `instructions.md`, `manifest.yaml` och samtliga deklarerade Knowledge-filer,
- att förbjudna utvecklingsfiler (`tests/`, `scripts/`, cache m.m.) inte läckt in,
- att `manifest.yaml` använder samma version som repositoryts `VERSION`,
- att instruktionen är högst 8 000 tecken och innehåller kritiska runtime-ämnen,
- att genererade filers SHA-256 stämmer med manifestet,
- att alla kanoniska source-hashar fortfarande stämmer,
- att samtliga filer under `metamodel/` och `schemas/` ingår i Custom GPT-manifestets parity-spårning,
- att Chat-ZIP innehåller samma `VERSION`, `metamodel/` och `schemas/` byte-identiskt,
- att A31:s deklarerade shared capability-kontrakt finns kvar.

## Paritetsprincip

Paritet betyder inte filidentitet mellan Chat och Custom GPT. Chat-paketet innehåller scripts och repositorystruktur medan Custom GPT innehåller optimerad instruktion och Knowledge.

Pariteten bevisas i stället genom att:

1. båda bygger från samma `VERSION`,
2. Chat innehåller de kanoniska `metamodel/`- och `schemas/`-filerna byte-identiskt,
3. Custom GPT-manifestet innehåller SHA-256 för exakt samma källfiler,
4. A31:s `shared_capabilities` är en explicit del av det genererade manifestet.

## Instruktionsbudget

A33 låser maxgränsen till **8 000 tecken** för den genererade Custom GPT-instruktionen. Buildern ska därför hålla operativa regler i instruktionen och lägga detaljerad metamodell, exempel och guider i Knowledge.

## Resultatnivåer

- `ERROR` blockerar distribution/release.
- `WARNING` är tillåtet men ska granskas.

A33 ska ge exit code `1` vid minst ett `ERROR`, annars `0`.
