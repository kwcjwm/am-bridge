---
name: am-page-modernization
description: AI PL workflow for page-based AM modernization using am-bridge. Use when the PM gives a MiPlatform/XPlatform/Nexacro page such as `aaa.xml` and wants either (a) an early customer-facing UI shell for structure signoff or (b) staged behavior locking work: stage 1 page+backend analysis package, AI review, stage 2 conversion plan, and stage 3 starter generation for Vue/Spring Boot.
---

# AM Page Modernization

Use this skill when acting as the working PL for AM tasks.
The human user is the PM. `am-bridge` CLI is the deterministic toolset. Your job is to orchestrate the steps, review weak spots, and move the work forward in stages.

## Core Rule

Do not treat the deterministic analyzer as final truth.
Do not treat a `UI Shell` as completed functionality.

In AI Pro environments, use the simplest real runtime that the platform allows.

Prefer direct execution first in restricted environments:

- `scripts/am_stage.ps1 <stage> <page-xml>`
- `python scripts/ai_pro_stage_runner.py <stage> <page-xml> --config am-bridge.config.json`

Use registered runner-backed tools when the platform actually supports them:

- `am-bridge-stage1`
- `am-bridge-stage2`
- `am-bridge-stage3`
- fallback: `am-bridge-stage`

Use direct CLI commands such as `am-bridge-analyze stage1 <page-xml>` only when that shell interface is the actual available runtime.

The analyzer is good at:

- extracting structure
- finding transaction candidates
- tracing controller/service/DAO/SQL candidates
- generating repeatable artifacts

The analyzer is weak at:

- deciding which dataset is truly primary
- distinguishing dominant result datasets from search/code/view-state datasets in every legacy variant
- resolving ambiguous backend chains in dynamic wrapper-heavy pages

That judgment belongs to the AI review pass.

## Operating Lanes

### Lane A: UI Shell First

Use this lane when the PM primarily wants to avoid early customer questions such as:

- why a button moved
- why a section is missing
- where a popup entry went

In this lane:

- lock the page frame, component placement, tabs, search area, result grid, detail area, and popup anchors first
- allow placeholder actions such as `console.log`, `alert`, or `연결 예정`
- clearly mark that behavior, API, save flow, validation, and backend bindings are not final yet

Recommended artifacts:

- `templates/analysis/page-triage.yaml`
- `templates/target/ui-shell-blueprint.yaml`

### Lane B: Behavior / Contract Lock

Use this lane when the PM needs actual modernization decisions to be locked.

This is the existing staged flow:

- stage 1 analysis package
- AI review via `review.json`
- stage 2 plan and Vue config lock
- stage 3 starter generation

## Stage Workflow

### Stage 1: Build Evidence Package

If the selected runtime path is `scripts/am_stage.ps1`, run:

```powershell
scripts/am_stage.ps1 stage1 <page-xml>
```

If the selected runtime path is the Python runner, run:

```powershell
python scripts/ai_pro_stage_runner.py stage1 <page-xml> --config am-bridge.config.json
```

If runner-backed AI Pro tools are registered, call `am-bridge-stage1`.
If neither of the above is available, run the direct CLI:

```powershell
am-bridge-analyze stage1 <page-xml>
```

Read:

- `artifacts/packages/...-package.json`
- `artifacts/packages/...-package.md`
- `artifacts/packages/...-analysis.md`
- `artifacts/reviews/...-review.json`

Check first:

- `primaryDatasetId`
- `mainGridComponentId`
- `primaryTransactionIds`
- backend trace coverage
- related popup/subview screens as separate pages

If the dominant business dataset is wrong, edit the review JSON before stage 2.

### Stage 1.5: AI Review Loop

Use the package report and your own judgment to correct:

- primary dataset
- dataset usage classification
- primary transaction
- interaction pattern
- backend trace chain

Write corrections into the review JSON.
This is mandatory when the page has a strong main grid or obvious analyzer mistakes.

### Stage 2: Lock Conversion Plan

If the selected runtime path is `scripts/am_stage.ps1`, run:

```powershell
scripts/am_stage.ps1 stage2 <page-xml>
```

If the selected runtime path is the Python runner, run:

```powershell
python scripts/ai_pro_stage_runner.py stage2 <page-xml> --config am-bridge.config.json
```

If runner-backed AI Pro tools are registered, call `am-bridge-stage2`.
If neither of the above is available, run the direct CLI:

```powershell
am-bridge-analyze stage2 <page-xml>
```

Read:

- `artifacts/plans/...-plan.json`
- `artifacts/plans/...-plan.md`
- `artifacts/plans/...-vue-config.json`
- `artifacts/plans/...-pm-checklist.md`

Use this stage to lock:

- file ownership
- frontend/backend split
- platform boundary
- execution order
- Vue implementation contract JSON
- PM validation checklist

### Stage 3: Generate Starter Bundle

If the selected runtime path is `scripts/am_stage.ps1`, run:

```powershell
scripts/am_stage.ps1 stage3 <page-xml>
```

If the selected runtime path is the Python runner, run:

```powershell
python scripts/ai_pro_stage_runner.py stage3 <page-xml> --config am-bridge.config.json
```

If runner-backed AI Pro tools are registered, call `am-bridge-stage3`.
If neither of the above is available, run the direct CLI:

```powershell
am-bridge-analyze stage3 <page-xml>
```

Read:

- `artifacts/starter/<page>/starter-bundle.json`
- `artifacts/starter/<page>/handoff-prompts.json`
- `artifacts/starter/<page>/vue-page-config.json`
- `artifacts/starter/<page>/pm-test-checklist.md`
- generated starter files

Treat stage 3 as scaffold + contract, not as final production code.

## When To Start With A UI Shell

Start with `UI Shell First` before stage 1 when one or more of these are true:

- the PM expects early structure signoff
- customer feedback is likely to focus on layout, missing blocks, or moved buttons
- the page is visually dense but the behavior contract is not ready to lock yet

Do not skip stage 1, review, or stage 2 just because the shell already exists.

## Operating Style For GLM-4.7

GLM-4.7 works better when you keep context narrow and structured.

- Prefer stage artifacts over dumping raw legacy code every time.
- Reuse saved package/plan/review files between steps.
- When correcting analysis, edit the review JSON rather than re-explaining the whole page in prose.
- Advance one page or one use case at a time.
- Keep generated reports canonical in English. If PM-facing Korean output is needed, derive it from the reviewed English report pack instead of treating generator-authored Korean as the source of truth.
- By default, translate only the summary-level PM/operator docs and keep deeper section docs plus registries linked in English.

## PM / PL Contract

- The PM gives scope, priority, deadlines, and approval.
- The AI PL runs the stage tools, performs review judgments, and proposes the next move.
- When unsure, save the uncertainty into artifacts instead of hiding it.

## Reference Loading

Read these only when needed:

- `references/stage-procedure.md`
- `references/review-contract.md`
- `references/ai-pro-prompts.md`
