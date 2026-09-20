# Claude Project distribution

C3 introduces a deterministic Claude Project projection of the same canonical System Modeller sources.

The package contains:

- `project-instructions.md`
- selected canonical Knowledge files
- `project/runtime-contract.json`
- `manifest.yaml`
- `README.md`
- `VERSION`

Claude Project does not claim local execution of System Modeller's Python scripts. The runtime contract therefore marks local script execution as unavailable and requires canonical mutation to stop whenever reliable validation cannot be performed.

The builder is `scripts/package_claude.py`; validation is `scripts/validate_claude.py`.
