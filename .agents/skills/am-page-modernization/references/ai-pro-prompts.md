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
1. Run am-bridge stage1 for the target page.
2. Review the stage1 package and review JSON.
3. Confirm or correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage classification, and backend trace chain.
4. If the stage1 judgment is weak, write corrections into the review JSON and continue with that correction layer.
5. Run stage2 and lock the conversion plan.
6. Run stage3 and generate the starter bundle.
7. Summarize what was locked, what still needs PM confirmation, and what the next implementation step should be.

Quality bar:
- Do not treat all datasets as peers.
- Distinguish main result dataset vs search/code/view-state datasets.
- Do not claim backend trace completion unless controller/service/DAO/SQL evidence is present or explicitly overridden in review JSON.
- Follow the project harness instead of answering in one shot.
- If registered tools are unavailable, use the direct execution path selected during bootstrap.
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
