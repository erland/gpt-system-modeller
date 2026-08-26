# Status

- Current plan: Plan A+ – Custom GPT distribution and release automation
- Plan A completion marker: A1–A30 / A30
- Completed: A1–A37 / A30 + A31 + A32 + A33 + A34 + A35 + A36 + A37
- Current version: 0.1.0-dev.37
- Milestone: **Plan A complete; PR/main verification and release.published publishing implemented**
- Next: publish a GitHub Release to verify the hosted release job and uploaded release assets.

## A36 result

GitHub tag `vX.Y.Z` is authoritative for release distributions. The same resolved version is injected into Chat and Custom GPT package metadata and filenames. `VERSION` remains the development fallback.

## Source of truth

Canonical model/runtime sources remain unchanged. Release version authority is contextual: GitHub tag for tagged releases, `VERSION` otherwise.

## Repository cleanup after A36
A conservative cleanup removed superseded duplicate/generated artifacts while preserving active regression fixtures. The A23 duplicate example project and stored golden reference ZIP are no longer required; tests now validate the maintained reference project and deterministic packaging directly.


## A37 result

Pull requests run the full regression suite, pushes to `main` and manual runs additionally build/validate both distributions, and `release.published` builds and attaches Chat, Custom GPT and the build manifest to the GitHub Release. Only the release job receives `contents: write`.
