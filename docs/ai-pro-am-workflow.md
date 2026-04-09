# AI Pro AM Workflow

This workflow is meant for the exported internal workspace, not for the external Codex support repository root.
Start with `bootstrap-initial-prompt.md` first, then bootstrap AI Pro, then run page AM work.
If `prompts/amprompt.md` exists in the internal bundle, use it only as supplemental detail guidance after the core harness is loaded.

## Roles

- Human operator: `PM`
- AI Pro with `GLM-4.7`: `PL`
- `am-bridge`: deterministic AM toolset under the PL

## Why This Structure Exists

`am-bridge` is not the final decision-maker.
It extracts repeatable evidence.
AI Pro reviews that evidence, corrects weak judgment, and pushes the work to the next stage.

This is important for legacy AM because:

- a main result grid dataset is often more important than search/code/view-state datasets
- backend routes may be partially hidden behind wrappers
- one-shot conversion is less reliable than staged correction

## Stage Flow

1. `stage1`
   Build the page conversion package, detailed legacy analysis report, and review JSON.
2. `AI review`
   Correct dominant dataset, main grid, primary transaction, and backend trace when needed.
3. `stage2`
   Lock the conversion plan, file ownership, Vue page config JSON, and PM test checklist.
4. `stage3`
   Generate starter code, handoff prompts, and copy the Vue config and PM checklist into the starter bundle.

## Recommended Operator Prompt

```text
Use the am-page-modernization skill.
Target page: C:\path\to\aaa.xml

I am the PM and you are the PL.
Use am-bridge as your deterministic toolset.

Run stage1 first.
Review the package and review JSON before proceeding.
Correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage, and backendTraces when needed.
Then run stage2, inspect the PM checklist, and run stage3.
At the end, report:
- locked decisions
- remaining uncertainties
- next implementation step
```

If you want the exact shortest operator sequence, use `deploy/internal-ai/operator-script.md`.

## Review Discipline

If stage1 is wrong, do not just mention the correction in prose.
Write the correction into the review JSON so later stages inherit the fixed judgment.

Typical corrections:

- `primaryDatasetId`
- `mainGridComponentId`
- `primaryTransactionIds`
- per-dataset `primaryUsage`
- backend trace fields such as `controllerMethod`, `daoClass`, `sqlMapId`, `querySummary`

## Expected Outcome

When the PM gives `aaa.xml`, AI Pro should be able to:

- analyze the page and related backend chain
- distinguish main business datasets from secondary datasets
- lock a page-level modernization plan
- emit a PM-facing checklist for test and signoff review
- emit starter Vue and Spring Boot skeletons
- preserve uncertainty as review artifacts instead of hiding it
