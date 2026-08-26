# Versionering och release-taggar – A36

## Princip

Vid ett GitHub-taggbygge är taggen `vX.Y.Z` den auktoritativa releaseversionen. Användaren behöver därför inte ändra `VERSION` inför en release.

Prioritetsordningen är:

1. explicit `--release-version` / `SYSTEM_MODELLER_RELEASE_VERSION`,
2. GitHub-taggen (`GITHUB_REF_TYPE=tag` + `GITHUB_REF_NAME`, eller `GITHUB_REF=refs/tags/...`),
3. repositoryfilen `VERSION` som fallback vid lokal utveckling, PR och vanlig branch-build.

Endast SemVer-taggar av formen `vX.Y.Z` eller `X.Y.Z` accepteras för releaseoverride.

## Vad taggen styr

För taggen `v0.2.0` ska samma build generera:

- `system-modeller-chat-v0.2.0.zip`
- `system-modeller-custom-gpt-v0.2.0.zip`
- Chat-distributionens inbäddade `VERSION` = `0.2.0`
- Custom GPT `instructions.md` = version `0.2.0`
- Custom GPT `manifest.yaml` = version `0.2.0`
- `build-manifest.yaml` med `release_version: 0.2.0`, `distribution_version: 0.2.0` och `version_source: github_tag`.

Repositoryts `VERSION` behålls som utvecklingsmetadata och kan exempelvis vara `0.1.0-dev.36` även när en historisk eller framtida release byggs från en explicit tagg.

## Lokal utveckling

Utan tagg/override bevaras tidigare beteende:

- paketnamnet använder basversionen före `-dev.`
- innehållets versionsmetadata använder det fulla `VERSION`-värdet.

Detta gör att utvecklingsbyggen fortfarande kan särskiljas från riktiga taggreleaser.

## Lokal simulering av en release

```bash
SYSTEM_MODELLER_RELEASE_VERSION=0.2.0 python scripts/ci_build.py --output-dir dist
```

eller:

```bash
python scripts/ci_build.py --release-version v0.2.0 --output-dir dist
```

## GitHub Actions

Workflowen triggas både på `main`, pull requests, `workflow_dispatch` och taggar `v*.*.*`. Vid taggbygge exporteras den validerade taggversionen som `SYSTEM_MODELLER_RELEASE_VERSION` innan tester och builders körs.
