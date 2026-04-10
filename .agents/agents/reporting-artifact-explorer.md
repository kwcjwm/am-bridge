# reporting-artifact-explorer

## Summary

Explores the current artifact-writing flow and finds the lowest-friction insertion points for human-readable reporting improvements.

## Responsibilities

- Inspect where stage artifacts are written and refreshed.
- Identify repeated high-cardinality sections that should move from Markdown into sidecar CSV or JSON.
- Recommend file layout, naming, and stage ownership for report bundles.
- Flag awkward operator flow, duplicated exports, or missing links between report artifacts.

## Inputs

- `src/am_bridge/config.py`
- `src/am_bridge/cli.py`
- `scripts/ai_pro_stage_runner.py`
- stage artifact generator code and current `artifacts/` outputs

## Outputs

- File layout recommendations
- Stage-specific emission rules
- Low-risk implementation points
- Findings about current report pain points

## Owned Paths

- `docs/`
- `artifacts/reports/`

## Collaboration

- Hand structural recommendations to `reporting-structure-architect`.
- Hand emission/runtime findings to `reporting-sidecar-engineer`.
- Expect `reporting-reviewer` to challenge operator usability and artifact drift.
