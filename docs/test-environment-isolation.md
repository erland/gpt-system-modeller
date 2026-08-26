# Test environment isolation (A39)

## Purpose

GitHub Actions injects release- and ref-specific environment variables into a job. Some System Modeller regression tests intentionally verify the local-development fallback where `VERSION` is the source of the generated distribution version. Those tests must not change meaning merely because the suite happens to run inside a `release.published` job.

A39 therefore isolates every Python regression test from the outer GitHub version context. `scripts/test.sh` invokes each test through `scripts/run_test_isolated.sh`, which removes:

- `GITHUB_EVENT_NAME`
- `GITHUB_EVENT_RELEASE_TAG_NAME`
- `GITHUB_REF_TYPE`
- `GITHUB_REF_NAME`
- `GITHUB_REF`
- `SYSTEM_MODELLER_RELEASE_VERSION`

Tests that verify release/tag behavior (A36-A38 and later) inject their own explicit environment values. This makes the test suite deterministic across pull requests, pushes to `main`, manual workflow runs and published releases.

The production build is **not** isolated. The release job still receives the real GitHub release context and `scripts/versioning.py` therefore continues to use the published `vX.Y.Z` tag as the authoritative release version.
