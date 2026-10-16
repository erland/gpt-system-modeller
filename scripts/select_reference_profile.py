#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.project_model import select_reference_profile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features-json", required=True)
    args = ap.parse_args()

    features = json.loads(args.features_json)
    profile = select_reference_profile(features)
    print(json.dumps({
        "profile": profile,
        "reason": "Selected by canonical GPT Byggaren reference-profile rules."
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
