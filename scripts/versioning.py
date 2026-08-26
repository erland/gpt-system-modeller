#!/usr/bin/env python3
"""Resolve System Modeller repository and distribution versions.

A36 policy:
- A GitHub release/tag named vX.Y.Z is authoritative for release builds.
- SYSTEM_MODELLER_RELEASE_VERSION may explicitly provide X.Y.Z or vX.Y.Z.
- Outside a tag/release build, VERSION remains the fallback source.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(?:v)?(?P<version>0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True)
class VersionInfo:
    repository_version: str
    distribution_version: str
    release_version: str
    source: str
    tag: str | None = None


def normalize_release(value: str) -> str:
    value = value.strip()
    match = SEMVER.fullmatch(value)
    if not match:
        raise ValueError(f"release version/tag must match vX.Y.Z or X.Y.Z, got {value!r}")
    return value[1:] if value.startswith("v") else value


def repository_version(root: Path = ROOT) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def github_tag(env: dict[str, str] | None = None) -> str | None:
    env = env or os.environ
    if env.get("GITHUB_REF_TYPE") == "tag" and env.get("GITHUB_REF_NAME"):
        return env["GITHUB_REF_NAME"].strip()
    ref = env.get("GITHUB_REF", "")
    if ref.startswith("refs/tags/"):
        return ref[len("refs/tags/"):].strip()
    return None


def resolve(root: Path = ROOT, env: dict[str, str] | None = None, explicit: str | None = None) -> VersionInfo:
    env = env or os.environ
    repo = repository_version(root)

    requested = explicit or env.get("SYSTEM_MODELLER_RELEASE_VERSION")
    if requested:
        release = normalize_release(requested)
        return VersionInfo(repo, release, release, "explicit", f"v{release}")

    tag = github_tag(env)
    if tag:
        release = normalize_release(tag)
        return VersionInfo(repo, release, release, "github_tag", tag)

    # Preserve the pre-A36 local-development behavior: generated package
    # contents carry VERSION, while release-shaped filenames use its base.
    release = repo.split("-dev.", 1)[0]
    return VersionInfo(repo, repo, release, "VERSION", None)
