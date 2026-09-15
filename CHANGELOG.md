# Changelog

## 0.1.0-dev.50 – Plan B complete

- B1–B4: hardened Chat runtime for simpler models with explicit operation order, deterministic context summary and small-model regression gates.
- B5–B10: added canonical report profile, diagram budgets, deterministic large-view splitting, scenario-specific sequence diagrams, PDF presentation contract and small/medium/dense end-to-end report regression.
- B11: introduced an internal report-profile catalog with `standard` as the only implemented/default profile and `overview`/`detailed` reserved as planned, non-user-selectable variants.
- B12: aligned Chat and Custom GPT distributions with the Plan B reporting/runtime sources, retained six Custom GPT Knowledge files and expanded the parity contract.
- Pull-request CI now builds and validates both distribution ZIPs in addition to the full regression suite, and uploads Chat, Custom GPT and build manifest artifacts.
- Added final distribution/release-readiness regression and documentation. Plan B is complete; publication remains a separate tag/GitHub Release action.

## Historical changelog

The complete pre-Plan-B history is preserved in Git history through `0.1.0-dev.39`. This development branch intentionally consolidates the active changelog around the Plan B completion entry; no runtime or release behavior depends on historical changelog text.
