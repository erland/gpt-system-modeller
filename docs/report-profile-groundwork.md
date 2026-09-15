# Report profile groundwork

B11 introduces a stable internal registry for architecture report profiles without exposing profile selection to users.

## Catalog

`metamodel/report-profiles/catalog.yaml` is the registry for report-profile identities and lifecycle state.

The B11 catalog contains three profile identities:

- `overview` — `planned`, not implemented,
- `standard` — `stable`, implemented and the default,
- `detailed` — `planned`, not implemented.

The catalog itself and every profile entry remain `user_selectable: false` in B11.

## Runtime behavior

`scripts/report_profile.py` resolves the default profile through the catalog. Existing calls to `report_profile.load()` therefore continue to load `standard.yaml` and preserve the current report behavior.

A caller may use `report_profile.load(profile="standard")` explicitly. Selecting `overview` or `detailed` fails deterministically with a `planned but not implemented` error. Unknown profile IDs also fail rather than silently falling back to `standard`.

An explicit file path remains supported for validation and tests. A caller may not combine an explicit path and a named profile.

## Stability boundary

B11 does not create alternate report content, alternate section sets or user-visible profile controls. The canonical `standard` profile remains the only implemented profile and the only source used by report generation, diagram composition and the PDF presentation contract.

Future profiles may vary section inclusion, narrative depth and presentation policy. The catalog also reserves future dimensions such as audience and purpose, but these are metadata groundwork only.

## Invariants

- `standard` is the only implemented profile.
- `standard` is the default profile.
- `overview` and `detailed` are explicit planned identities, not aliases for `standard`.
- No profile is user-selectable in B11.
- Missing, unknown or unimplemented profile choices fail explicitly.
- The existing standard report output remains governed by `metamodel/report-profiles/standard.yaml`.
