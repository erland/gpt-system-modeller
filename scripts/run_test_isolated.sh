#!/usr/bin/env bash
set -euo pipefail

# A39: Unit/regression tests must not inherit GitHub event version context.
# Individual tests that verify tag/release behavior inject their own explicit
# environment values. This prevents a hosted release job from changing the
# assumptions of older fallback-version tests.
if [[ $# -lt 1 ]]; then
  echo "usage: $0 <python-test> [args...]" >&2
  exit 2
fi

exec env \
  -u GITHUB_EVENT_NAME \
  -u GITHUB_EVENT_RELEASE_TAG_NAME \
  -u GITHUB_REF_TYPE \
  -u GITHUB_REF_NAME \
  -u GITHUB_REF \
  -u SYSTEM_MODELLER_RELEASE_VERSION \
  python3 "$@"
