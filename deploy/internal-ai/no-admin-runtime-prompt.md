# No-Admin Runtime Prompt

Use this prompt when the internal AI environment cannot install a global command and cannot register custom tools.

Paste the prompt below after the readiness check has completed.

```text
In this environment, assume these admin features are unavailable:
- global `/harness` installation
- custom tool registration

Operate in prompt-first mode with direct command execution.
Do not treat missing admin features as a project failure.
The project harness is already loaded from workspace files.

Use these sources as the core harness:
1. `AGENTS.md`
2. `.agents/skills/am-page-modernization/SKILL.md`
3. `integrations/ai-pro/project/am-page-modernization.md`
4. `integrations/ai-pro/project/operator-prompts.md`

If `prompts/amprompt.md` exists, use it only as supplemental guidance for:
- detailed analysis report quality
- Vue conversion config completeness

It must not:
- replace the staged workflow
- replace `review.json` as the correction layer
- override explicit PM decisions

Choose the first usable runtime path from this list:
1. `scripts/am_stage.ps1`
2. `python scripts/ai_pro_stage_runner.py ...`
3. `am-bridge-analyze ...`

Report the chosen runtime path once, then continue using it.
Do not keep repeating that `/harness` or tool registration is unavailable.

Before real page work, confirm:
1. the workspace harness files are loaded
2. the selected direct execution path is available
3. `prompts/amprompt.md` presence or absence

When the PM gives a target page, execute this workflow:
1. run stage1
2. inspect package artifacts, analysis report, and `review.json`
3. correct `review.json` when dominant dataset, main grid, transactions, dataset usage, or backend traces are weak or wrong
4. run stage2
5. inspect the PM checklist and Vue config
6. run stage3 only when stage2 is acceptable
7. report locked decisions, remaining risks, and next step

Important:
- treat project harness readiness as the primary success condition
- treat direct execution availability as the runtime success condition
- treat global command and custom tool registration only as optional convenience features
- never claim runtime success without evidence
```
