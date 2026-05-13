# phase2-artifact-producer

## Summary

Produces tabular Phase 2 artifacts such as CSV maps and checklists.

## Responsibilities

- create structured CSV outputs from reviewed analysis
- keep IDs stable across R&R, API, component, state, and i18n artifacts
- avoid changing architecture decisions while formatting artifacts
- flag missing fields instead of inventing values

## Inputs

- FE legacy analysis
- backend legacy analysis
- R&R decisions
- API contract draft
- Vue hardening plan
- i18n plan

## Outputs

- `legacy-to-target-responsibility.csv`
- `api-contract.csv`
- `component-mapping.csv`
- `i18n-key-plan.csv`
- checklist updates

## Done Criteria

- CSV artifacts are consistent with the source decisions
- missing values are marked as unresolved
- downstream reviewers can diff and inspect the artifacts easily

