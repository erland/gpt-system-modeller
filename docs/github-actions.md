# GitHub Actions – verifiering och releasepublicering

Steg A37 separerar kontinuerlig verifiering från faktisk releasepublicering.

## Triggers

Workflowen `.github/workflows/build-distributions.yml` reagerar på:

- `pull_request` – verifierar varje ny/uppdaterad PR,
- `push` till `main` – verifierar och gör ett distributionsbygge/paritetskontroll,
- `release` med `types: [published]` – verifierar, bygger och publicerar releaseartefakter,
- `workflow_dispatch` – verifierar och gör distributionsbygge manuellt.

En publicerad GitHub Release är därmed den normala release-triggern. En separat tagg-push behövs inte för att workflowen ska starta.

## Jobb 1 – verify

Körs på alla triggers och har endast `contents: read`.

1. checkout,
2. Python/CI-beroenden,
3. hela regressionstestsviten (`scripts/test.sh`).

PR:er bygger alltså inte fulla distributionsartefakter i onödan, men hela kodbasens regression verifieras när PR:n skapas och när nya commits pushas till den.

## Jobb 2 – build-check

Körs efter `verify` på:

- push till `main`,
- `workflow_dispatch`.

Jobbet:

1. bygger Chat och Custom GPT med `scripts/ci_build.py`,
2. kör A33-paritetsvalideringen direkt mot ZIP-filerna,
3. laddar upp Chat, Custom GPT och `build-manifest.yaml` som Actions artifacts.

Det ger en extra distributionskontroll efter merge/direct commit till `main` utan write-behörighet.

## Jobb 3 – release

Körs endast när en GitHub Release publiceras och efter att `verify` gått grönt.

Jobbet:

1. checkar ut exakt `github.event.release.tag_name`,
2. validerar att taggen följer `vX.Y.Z`,
3. använder release-taggen som auktoritativ versionskälla,
4. bygger Chat och Custom GPT,
5. kör paritetsvalidering,
6. laddar upp samma filer som Actions artifact,
7. bifogar Chat-ZIP, Custom GPT-ZIP och `build-manifest.yaml` som assets på själva GitHub Release-sidan via `gh release upload`.

Endast release-jobbet har `contents: write`; övriga jobb använder read-only-behörighet.

## Versionsprincip

Versionsresolvern känner i A37 till tre releasekontexter i prioriteringsordning:

1. publicerad GitHub Release (`github_release`),
2. explicit releaseversion för lokal simulering,
3. Git-tagg (`github_tag`),
4. annars `VERSION` som utvecklingsfallback.

För en GitHub Release `v1.2.3` byggs därför:

```text
system-modeller-chat-v1.2.3.zip
system-modeller-custom-gpt-v1.2.3.zip
build-manifest.yaml
```

och manifestet anger `version_source: github_release` samt `release_tag: v1.2.3`.

## Lokal kontroll

Vanlig distributionskontroll:

```bash
python scripts/ci_build.py --output-dir dist
```

Simulerad release kan testas genom att sätta releaseeventets miljövariabler:

```bash
GITHUB_EVENT_NAME=release \
GITHUB_EVENT_RELEASE_TAG_NAME=v1.2.3 \
python scripts/ci_build.py --output-dir dist
```


## Test environment isolation

A39 runs every regression test through `scripts/run_test_isolated.sh`. The wrapper removes outer GitHub release/tag version variables before invoking the test. Tests that verify release/tag behavior inject their own explicit environment. This prevents a `release.published` job from changing the semantics of historical development-fallback tests while leaving the real release build context untouched.
