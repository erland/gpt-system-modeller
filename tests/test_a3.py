#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/modeling-principles.md"


def main() -> int:
    if not DOC.is_file():
        print("FAIL: docs/modeling-principles.md missing")
        return 1
    text = DOC.read_text(encoding="utf-8")
    required = {
        "four abstraction levels": all(x in text for x in ("Conceptual", "Logical", "Runtime", "Implementation")),
        "system boundary": "## 4. System" in text and "## 5. ExternalSystem" in text,
        "structural distinctions": all(x in text for x in ("## 6. Subsystem", "## 7. Component", "## 8. Service", "## 9. Module", "## 10. Responsibility")),
        "use case rules": "## 11. UseCase" in text and "Endpoint = UseCase" in text,
        "information rules": "## 13. InformationObject" in text and "Table = InformationObject" in text,
        "runtime rules": all(x in text for x in ("## 17. RuntimeUnit", "## 18. DeploymentNode", "## 19. Environment")),
        "source abstraction": "## 20. Hur källkod ska abstraheras" in text and "Observed clusters" in text,
        "view rules": "## 26. Regler för arkitekturvyer" in text,
        "anti-patterns": "## 27. Antimönster" in text,
        "decision rule": "högre abstraktionsnivån" in text,
    }
    failed = [name for name, ok in required.items() if not ok]
    if failed:
        for name in failed:
            print(f"FAIL: missing/invalid A3 requirement: {name}")
        return 1
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version.startswith("0.1.0-dev."):
        print(f"FAIL: expected Plan A development version, got {version!r}")
        return 1
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "modeling-principles.md" not in readme:
        print("FAIL: README does not link modeling-principles.md")
        return 1
    print("A3 modeling-principles tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
