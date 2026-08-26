# A35 – Release readiness for v0.1.0

A35 distinguishes **local release readiness** from **GitHub-hosted workflow verification**.

## Local release check

Run:

```bash
python scripts/release_check.py --output-dir release-dist
```

The check:

1. builds Chat and Custom GPT distributions twice,
2. requires byte-identical repeated builds,
3. validates Custom GPT integrity and parity with Chat,
4. checks artifact names and version metadata from `VERSION`,
5. verifies SHA-256 values in `build-manifest.yaml`,
6. checks both ZIP files for forbidden development/runtime junk,
7. materializes the verified release artifacts,
8. writes `release-readiness.yaml`.

A local result of `READY` means that the repository content is suitable for a v0.1.0 release candidate.

## GitHub Actions runtime verification

Local execution cannot prove that GitHub-hosted runners, repository event configuration or artifact upload behave correctly. After the repository is pushed, run the `Test and build distributions` workflow once (a push to `main`, pull request, or manual `workflow_dispatch` is sufficient).

The GitHub run is considered successful when:

- the `Test, build and validate` job is green,
- the Chat artifact is uploaded,
- the Custom GPT artifact is uploaded,
- the build manifest artifact is uploaded,
- no parity or regression step fails.

This is the only A35 item that may require the repository owner to perform an external action.

## Release version

A35 intentionally keeps the repository on a development version (`0.1.0-dev.35`). The generated distribution filenames use the release base `0.1.0`. Change `VERSION` to `0.1.0` only when actually preparing/publishing the release commit/tag.
