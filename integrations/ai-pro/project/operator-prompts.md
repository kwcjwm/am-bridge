# AI Pro Operator Prompts

## 1. Global Harness Check

```text
/harness
Read the workspace harness.
Tell me whether the AM page modernization workflow is ready, which tools are callable, and what I should run next.
```

## 2. End-To-End AM For One Page

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

I am the PM and you are the PL.
Use am-bridge as the deterministic tool layer.
If prompts/amprompt.md exists, use it as supplemental guidance for analysis report detail and Vue conversion config completeness, but do not override the staged workflow.

Execution policy:
1. Run stage1.
2. Review the package, detailed analysis report, and review.json.
3. Correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage, and backend traces if needed.
4. Run stage2.
5. Inspect the PM checklist and make sure it matches the page's real business functions.
6. Run stage3.
7. Copy the PM checklist into the starter bundle.
8. Report locked decisions, remaining risks, and next implementation step.
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
1. Run stage1.
2. Review the package, detailed analysis report, and review.json.
3. Use prompts/amprompt.md only to increase report detail and Vue conversion config quality.
4. Do not let prompts/amprompt.md replace review.json as the correction layer.
5. Run stage2.
6. Run stage3 if stage2 is acceptable.
7. Report what came from the core harness and what was additionally shaped by prompts/amprompt.md.
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
