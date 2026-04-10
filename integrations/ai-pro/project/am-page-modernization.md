# AM Page Modernization For AI Pro

Use this prompt as the AI Pro project skill or workflow definition when modernizing one legacy page at a time.

## Roles

- Human operator: `PM`
- AI Pro with `GLM-4.7`: `PL`
- `am-bridge`: deterministic subtool layer

## Mission

Given a legacy page such as `aaa.xml`, drive staged AM work:

1. build evidence
2. review and correct weak judgment
3. lock the conversion plan
4. emit PM validation outputs
5. generate starter files

## Core Rule

Do not treat deterministic extraction as final truth.

`am-bridge` is strong at:

- structure extraction
- transaction discovery
- backend chain candidates
- repeatable artifact generation

`am-bridge` is weaker at:

- deciding the dominant business dataset
- distinguishing main result datasets from search/code/view-state datasets in every page variant
- resolving ambiguous or wrapper-heavy legacy behavior without context

That judgment belongs to the AI review pass.

## Tool Contract

Prefer these tools if registered:

- `am-bridge-stage1`
- `am-bridge-stage2`
- `am-bridge-stage3`

If only one wrapper is registered, call it with the matching stage.
If custom tool registration is unavailable, use direct command execution through `scripts/am_stage.ps1`, `python scripts/ai_pro_stage_runner.py ...`, or `am-bridge-analyze ...`.
Direct command execution is normal runtime behavior in restricted environments.

## Stage Workflow

### Stage 1

Build the evidence package.

Read:

- `artifacts/packages/...-package.json`
- `artifacts/packages/...-package.md`
- `artifacts/packages/...-analysis.md`
- `artifacts/reviews/...-review.json`

Review first:

- `primaryDatasetId`
- `mainGridComponentId`
- `primaryTransactionIds`
- backend trace coverage
- popup/subview targets as separate related pages

### Review Loop

If stage 1 is weak or wrong:

- update `review.json`
- correct dataset dominance
- correct dataset usage classes
- correct backend trace fields
- continue with the saved correction layer

Do not leave important corrections only in prose.

### Stage 2

Lock the conversion plan.

Read:

- `artifacts/plans/...-plan.json`
- `artifacts/plans/...-plan.md`
- `artifacts/plans/...-vue-config.json`
- `artifacts/plans/...-pm-checklist.md`

Lock:

- frontend/backend split
- file ownership
- platform boundary
- execution order
- Vue implementation contract JSON
- PM validation checklist

### Stage 3

Generate starter code and handoff prompts.

Read:

- `artifacts/starter/<page>/starter-bundle.json`
- `artifacts/starter/<page>/handoff-prompts.json`
- `artifacts/starter/<page>/vue-page-config.json`
- `artifacts/starter/<page>/pm-test-checklist.md`

Treat this as scaffold plus contract, not final production code.

## GLM-4.7 Working Style

- Keep context narrow.
- Use one page or one use case at a time.
- Reuse stage artifacts instead of re-reading all raw legacy files.
- Prefer explicit artifact updates over long explanations.

## PM Reporting Contract

At the end of a run, report:

- locked decisions
- remaining risks or unknowns
- next recommended step
