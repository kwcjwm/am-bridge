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

Execution policy:
1. Run stage1.
2. Review the package and review.json.
3. Correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage, and backend traces if needed.
4. Run stage2.
5. Run stage3.
6. Report locked decisions, remaining risks, and next implementation step.
```

## 3. Review-Only Pass

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

Use the existing stage1 artifacts.
Focus only on the review loop.
If the dominant dataset or backend trace is wrong, fix review.json and summarize the correction.
```

## 4. Stage 3 Starter Generation Only

```text
Use the AM page modernization workflow for this workspace.
Target page: C:\path\to\aaa.xml

Assume stage1 review and stage2 planning are already approved.
Run stage3 and summarize the generated starter bundle with the next implementation task split.
```
