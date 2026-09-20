# GitHub Actions – verifiering och releasepublicering

Workflowen `.github/workflows/build-distributions.yml` separerar repository-verifiering, unified build-kontroll och faktisk GitHub Release-publicering.

## Triggers

Workflowen reagerar på:

- `pull_request`,
- `push` till `main`,
- `release` med `types: [published]` (publicerad GitHub Release),
- `workflow_dispatch`.

## Verify

`Verify repository` kör instruktionsefterlevnad och hela regressionstestsviten. Jobbet använder endast `contents: read`.

## Build and validate distributions

På PR, push till `main` och manuell körning bygger `scripts/ci_build.py` hela den unified leveransen:

- source project ZIP,
- Chat ZIP,
- Custom GPT ZIP,
- Claude Project ZIP,
- OpenCode ZIP,
- `runtime-parity.yaml`,
- `SHA256SUMS.txt`,
- `build-manifest.yaml`.

Custom GPT/Chat, Claude och OpenCode valideras därefter på nytt direkt från de genererade ZIP-filerna. Hela leveransen laddas upp som ett gemensamt Actions artifact, `system-modeller-unified-build`.

## GitHub Release

När en GitHub Release publiceras checkar release-jobbet ut exakt `github.event.release.tag_name`. Taggen är auktoritativ versionskälla.

Release-jobbet bygger och återvaliderar samma unified leverans och laddar upp den både som Actions artifact och som assets på GitHub Release-sidan:

- `system-modeller-project-vX.Y.Z.zip`
- `system-modeller-chat-vX.Y.Z.zip`
- `system-modeller-custom-gpt-vX.Y.Z.zip`
- `system-modeller-claude-vX.Y.Z.zip`
- `system-modeller-opencode-vX.Y.Z.zip`
- `runtime-parity.yaml`
- `SHA256SUMS.txt`
- `build-manifest.yaml`

Endast release-jobbet har `contents: write`; workflowens default och övriga jobb är read-only.

## Versionsprincip

Versionsresolvern prioriterar:

1. publicerad GitHub Release (`github_release`),
2. explicit releaseversion,
3. Git-tagg (`github_tag`),
4. annars `VERSION` som utvecklingsfallback.

## Lokal kontroll

Vanlig unified build:

```bash
python scripts/ci_build.py --output-dir dist
```

Simulerad release:

```bash
GITHUB_EVENT_NAME=release \
GITHUB_EVENT_RELEASE_TAG_NAME=v1.2.3 \
python scripts/ci_build.py --output-dir dist
```

## Test environment isolation

Regressionstester körs isolerat från omgivande release/tag-versionvariabler. Tester som verifierar releasebeteende injicerar sin egen explicita miljö.
