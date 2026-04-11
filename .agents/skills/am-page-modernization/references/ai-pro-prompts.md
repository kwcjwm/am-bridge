# AI Pro Prompt Playbook

## One-Time Harness Check

Use this only when the AI Pro environment actually supports a global harness command.
If not, use the bundle `bootstrap-initial-prompt.md` and `no-admin-runtime-prompt.md` flow instead.

Use this when you want AI Pro to inspect the project harness before real AM work:

```text
/harness
Read the AM harness for this project.
Treat me as PM and yourself as the working PL.
Use am-bridge stage tools as deterministic subtools and use the am-page-modernization workflow for real page work.
Report the stage workflow you will follow for page-level AM.
```

## End-to-End Page Modernization

Use this when you want AI Pro to drive one page from analysis through starter generation:

```text
Use the am-page-modernization skill.
Target page: <absolute-path-to-aaa.xml>

Role:
- I am the PM.
- You are the PL.

Execution policy:
1. Decide whether this page needs `UI Shell First`.
2. If early customer layout agreement matters, create a shell blueprint with clearly marked placeholder actions.
3. Run am-bridge stage1 for the target page.
4. Review the stage1 package and review JSON.
5. Confirm or correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage classification, and backend trace chain.
6. If the stage1 judgment is weak, write corrections into the review JSON and continue with that correction layer.
7. Run stage2 and lock the conversion plan.
8. Run stage3 and generate the starter bundle.
9. Summarize what was locked, what still needs PM confirmation, and what the next implementation step should be.

Quality bar:
- Do not treat all datasets as peers.
- Distinguish main result dataset vs search/code/view-state datasets.
- Do not claim backend trace completion unless controller/service/DAO/SQL evidence is present or explicitly overridden in review JSON.
- Follow the project harness instead of answering in one shot.
- If registered tools are unavailable, use the direct execution path selected during bootstrap.
```

## UI Shell First Prompt

Use this when the PM wants a customer-facing shell before behavior is finalized:

```text
Use the am-page-modernization skill.
Target page: <absolute-path-to-aaa.xml>

I am the PM and you are the PL.
Create a customer-facing UI shell first.

Requirements:
1. Lock the page frame, search block, result grid block, detail block, tabs, popup anchors, and major button placement.
2. Keep shared platform assumptions explicit.
3. Use placeholder actions such as `console.log`, `alert`, or `연결 예정` where real behavior is not locked yet.
4. Do not pretend API, save flow, validation, or backend bindings are complete.
5. Produce a shell blueprint the PM can use for structure signoff before stage1/stage2 behavior locking.
```

## Stage-Specific Review Prompt

Use this when stage1 already exists and you want AI Pro to focus on the correction loop:

```text
Use the am-page-modernization skill.
Target page: <absolute-path-to-aaa.xml>

Use the existing stage1 package and review JSON.
Review whether the dominant business dataset, main grid, and primary transaction are correct.
If backend trace coverage is incomplete or wrong, correct the backendTraces block in review JSON.
Then rerun stage2 with the corrected review layer and summarize only the decisions that matter for PM approval.
```
