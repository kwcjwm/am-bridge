---
name: am-page-modernization
description: AI PL workflow for page-based AM modernization using am-bridge. Use when the PM gives a MiPlatform/XPlatform/Nexacro page such as `aaa.xml` and wants staged work: (1) stage 1 page+backend analysis package, (2) AI review and correction of dataset salience or backend trace, (3) stage 2 conversion plan, (4) stage 3 starter generation for Vue/Spring Boot, or any general AM execution that should follow the project harness instead of a one-shot answer.
---

# AM Page Modernization

Use this skill when acting as the working PL for AM tasks.
The human user is the PM. `am-bridge` CLI is the deterministic toolset. Your job is to orchestrate the steps, review weak spots, and move the work forward in stages.

## Core Rule

Do not treat the deterministic analyzer as final truth.

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

## Stage Workflow

### Stage 1: Build Evidence Package

Run:

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

Run:

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

Run:

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

## Operating Style For GLM-4.7

GLM-4.7 works better when you keep context narrow and structured.

- Prefer stage artifacts over dumping raw legacy code every time.
- Reuse saved package/plan/review files between steps.
- When correcting analysis, edit the review JSON rather than re-explaining the whole page in prose.
- Advance one page or one use case at a time.

## PM / PL Contract

- The PM gives scope, priority, deadlines, and approval.
- The AI PL runs the stage tools, performs review judgments, and proposes the next move.
- When unsure, save the uncertainty into artifacts instead of hiding it.

## Reference Loading

Read these only when needed:

- `references/stage-procedure.md`
- `references/review-contract.md`
- `references/ai-pro-prompts.md`
