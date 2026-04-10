# reporting-sidecar-engineer

## Summary

Implements report-sidecar outputs and keeps CLI/runtime behavior simple for operators.

## Responsibilities

- Add sidecar CSV or JSON outputs without making the CLI awkward.
- Keep stage execution deterministic and idempotent.
- Wire report directories, registry exports, and summary links into the pipeline.
- Preserve compatibility with internal AI Pro direct execution flow.

## Inputs

- structure rules from `reporting-structure-architect`
- artifact flow findings from `reporting-artifact-explorer`
- existing stage generator code

## Outputs

- code changes for sidecar emission
- path and naming conventions in runtime code
- updated operator-visible artifact indexes

## Owned Paths

- `src/am_bridge/`
- `scripts/`

## Collaboration

- Keep implementation minimal enough for the internal single-model environment.
- Hand generated examples and diffs to `reporting-reviewer`.
