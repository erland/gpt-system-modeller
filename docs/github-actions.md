# GitHub Actions – test och distributionsbygge

Steg A34 introducerar `.github/workflows/build-distributions.yml` som den gemensamma CI-vägen för System Modeller.

## Triggers

Workflowen körs på:

- push till `main`,
- pull requests,
- manuell `workflow_dispatch`.

A35 kan senare komplettera detta med själva GitHub Release-publiceringen utan att ändra hur distributionerna byggs.

## CI-kontrakt

Jobbet ska i denna ordning:

1. checka ut repositoryt,
2. installera Python och `requirements-ci.txt`,
3. köra hela `scripts/test.sh`,
4. köra `scripts/ci_build.py`,
5. validera Chat/Custom-paritet igen direkt mot de genererade ZIP-filerna,
6. ladda upp Chat-ZIP, Custom GPT-ZIP och build-manifest som separata GitHub Actions artifacts.

Builden har endast `contents: read`. Den behöver inga secrets och gör inga repository-writes.

## Versionsprincip

`VERSION` är fortsatt enda versionskälla. Om repositoryversionen exempelvis är `0.1.0-dev.34` producerar CI:

- `system-modeller-chat-v0.1.0.zip`
- `system-modeller-custom-gpt-v0.1.0.zip`

Det gör att releasefilnamn inte behöver hårdkodas i workflowen.

## Gemensam lokal CI-builder

```bash
python scripts/ci_build.py --output-dir dist
```

Buildern:

- bygger båda distributionsformerna,
- kör A33-paritetsvalideringen programmässigt,
- skriver `dist/build-manifest.yaml`,
- lagrar SHA-256 och filstorlek för båda ZIP-filerna.

Den lokala buildern och GitHub Actions använder därmed samma distributionskod.

## Action-versioner

A34 använder de aktuella stora versionerna `actions/checkout@v7`, `actions/setup-python@v7` och `actions/upload-artifact@v7`. Versionsvalet är avsiktligt explicit så CI-testet kan upptäcka oavsiktliga nedgraderingar.
