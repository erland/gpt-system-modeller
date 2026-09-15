# End-to-end report regression

B10 verifies that the complete standard architecture-report path behaves consistently across three representative system sizes: `small`, `medium` and `dense`.

The cases are declared in `evals/report-regression/cases.yaml`. `scripts/evaluate_report_regression.py` generates deterministic temporary system projects from those declarations and evaluates the same runtime components used by normal reporting.

The regression checks that:

- all canonical report sections from the standard profile are rendered in stable order,
- B7-supported diagrams either stay whole or are split deterministically,
- every rendered split part remains within the profile's preferred element and relationship budgets,
- the detail parts together retain all canonical facts represented by the original materialized view,
- the medium and dense cases actually exercise automatic diagram splitting,
- B8 produces exactly one sequence diagram per Interaction and keeps every Interaction isolated,
- the generated result is deterministic across repeated runs.

The three levels are intentionally synthetic rather than domain-specific golden projects. This makes density and expected split behavior explicit and keeps the regression stable while still exercising the complete report composition pipeline.

B10 validates report composition and semantic coverage. It does not introduce alternative report structures or user-selectable detail levels; that groundwork belongs to B11.
