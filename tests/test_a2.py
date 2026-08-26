#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "docs/mvp-scope.md"


def main() -> int:
    if not SCOPE.is_file():
        print("FAIL: docs/mvp-scope.md missing")
        return 1
    text = SCOPE.read_text(encoding="utf-8")
    required = {
        "system understanding goal": "Systemförståelse" in text or "systemförståelse" in text,
        "UML relationship": "Förhållande till UML" in text,
        "C4 relationship": "Förhållande till C4" in text,
        "deployment in scope": "Deployment View" in text and "RuntimeUnit" in text,
        "use cases in scope": "UseCase" in text,
        "information in scope": "InformationObject" in text,
        "evidence in scope": "Evidence" in text,
        "declared/observed/inferred": all(x in text for x in ("declared", "observed", "inferred")),
        "definition of done": "Definition of Done" in text,
        "architecture description": "arkitekturbeskrivning" in text.lower(),
    }
    failed = [name for name, ok in required.items() if not ok]
    if failed:
        for name in failed:
            print(f"FAIL: missing/invalid A2 requirement: {name}")
        return 1
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version.startswith("0.1.0-dev."):
        print(f"FAIL: expected Plan A development version, got {version!r}")
        return 1
    # A2 remains a regression test after later steps; do not require STATUS to stay at A2.
    print("A2 scope tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
