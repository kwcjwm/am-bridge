# AI Pro Operator Prompts

## 0. Project Harness Readiness Check

Use `bootstrap-initial-prompt.md` as the first message in the exported internal workspace.

If the readiness result shows that global commands or custom tool registration are blocked, immediately switch to `no-admin-runtime-prompt.md`.

## 1. Optional Global Harness Check

```text
/harness
Read the workspace harness.
Tell me whether the AM page modernization workflow is ready, which tools are callable, and what I should run next.
```

If `/harness` cannot exist in this environment, skip this prompt and use the no-admin runtime flow.

## 2. End-To-End AM For One Page

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

I am the PM and you are the PL.
Use am-bridge as the deterministic tool layer.
If prompts/amprompt.md exists, use it as supplemental guidance for analysis report detail and Vue conversion config completeness, but do not override the staged workflow.
If registered tools are unavailable, use direct command execution through `scripts/am_stage.ps1`, `python scripts/ai_pro_stage_runner.py ...`, or `am-bridge-analyze ...`.
Treat direct command execution as normal operation, not as a degraded mode.

Execution policy:
1. Classify whether this page needs `UI Shell First`.
2. If early customer structure signoff matters, create a shell blueprint with clearly marked placeholder actions.
3. Run stage1.
4. Review the package, detailed analysis report, and review.json.
5. Correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage, and backend traces if needed.
6. Run stage2.
7. Inspect the PM checklist and make sure it matches the page's real business functions.
8. Run stage3.
9. Copy the PM checklist into the starter bundle.
10. Report locked decisions, remaining risks, and next implementation step.
```

## 2A. End-To-End AM With Custom AM Prompt

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

I am the PM and you are the PL.
Use am-bridge as the deterministic tool layer.

Read these in order:
1. AGENTS.md
2. .agents/skills/am-page-modernization/SKILL.md
3. prompts/amprompt.md

Execution policy:
1. Decide whether this page needs `UI Shell First`.
2. If yes, create a shell blueprint before behavior lock.
3. Run stage1.
4. Review the package, detailed analysis report, and review.json.
5. Use prompts/amprompt.md only to increase report detail, shell quality, and Vue conversion config quality.
6. Do not let prompts/amprompt.md replace review.json as the correction layer.
7. Run stage2.
8. Run stage3 if stage2 is acceptable.
9. Report what came from the core harness and what was additionally shaped by prompts/amprompt.md.
```

## 3. Review-Only Pass

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

Use the existing stage1 artifacts.
Focus only on the review loop.
If the dominant dataset or backend trace is wrong, fix review.json and summarize the correction.
Treat popup/subview targets as separate related screens.
Call out PM checklist items that would be wrong unless review.json is corrected.
```

## 4. Stage 3 Starter Generation Only

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

Assume stage1 review and stage2 planning are already approved.
Run stage3 and summarize the generated starter bundle, Vue config, and PM checklist with the next implementation task split.
```

## 5. UI Shell First Only

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

The PM wants customer-facing structure signoff first.

Produce a UI shell blueprint that fixes:
- search block placement
- result grid placement
- detail / form section placement
- main buttons
- popup or subview entry points

Use placeholder actions such as `console.log`, `alert`, or `연결 예정` when real behavior is not locked yet.
Do not claim API, save, validation, or backend behavior is already finalized.
Summarize which parts are structure-only and which still need stage1/stage2 behavior locking.
```

## 6. Korean Report Delivery From Canonical English Reports

```text
Use the generated English report pack as the source of truth for this page.
Target page: C:\path\to\aaa.xml

Read:
1. artifacts/reports/<page>/README.md
2. artifacts/reports/<page>/translate-to-korean.md
3. stage1/stage2 overview docs linked from the page hub
4. the primary narrative reports in `artifacts/packages/` and `artifacts/plans/`

Produce a Korean delivery version for PM/operator use.

Rules:
1. Keep dataset IDs, transaction IDs, endpoint IDs, and file paths in backticks.
2. Translate explanation text, not technical identifiers.
3. Default to summary-only Korean delivery, not a full Korean mirror of every section and CSV.
4. Keep deep links pointed at the English canonical docs unless a Korean counterpart is explicitly required.
5. Before writing files, list the exact Korean output files and confirm that none overwrite English originals.
6. Separate UI shell/layout decisions from behavior/API/SQL lock decisions.
7. Call out unresolved risks clearly.
8. Do not change the English originals unless explicitly asked.
```
