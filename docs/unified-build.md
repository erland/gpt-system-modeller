# Unified build and validation

From Plan C C5, `scripts/ci_build.py` is the common deterministic build path for System Modeller.

For release version `X.Y.Z` it produces:

- `system-modeller-project-vX.Y.Z.zip`
- `system-modeller-chat-vX.Y.Z.zip`
- `system-modeller-custom-gpt-vX.Y.Z.zip`
- `system-modeller-claude-vX.Y.Z.zip`
- `system-modeller-opencode-vX.Y.Z.zip`
- `runtime-parity.yaml`
- `SHA256SUMS.txt`
- `build-manifest.yaml`

The project ZIP is a deterministic source package and excludes Git metadata, virtual environments, caches and generated distribution directories.

The common build runs the existing Chat/Custom GPT parity validator plus the Claude and OpenCode validators before writing the final manifest.

`runtime-parity.yaml` is rendered directly from `gpt-project.yaml`. `SHA256SUMS.txt` covers the project package, all four runtime ZIPs and the parity report. `build-manifest.yaml` records the same artifacts together with their hashes, sizes and validation summaries.

The older runtime-specific builders remain supported compatibility entry points. CI and release publication are migrated to the complete artifact set in C6.
