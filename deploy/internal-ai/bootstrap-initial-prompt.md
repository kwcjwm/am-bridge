# Internal Bootstrap Initial Prompt

Paste the prompt below into the internal AI as the first message after opening the exported internal workspace.

```text
You are operating inside the exported AM Bridge internal workspace.
This workspace is single-model only. There are no sub-agents here.
The human operator is the PM. You are the working PL.
`am-bridge` is the deterministic tool layer.

This session is for bootstrap and readiness only.
Do not start real AM work yet.
Do not claim success for anything you did not verify.
If something cannot be checked directly, mark it as `unverified` or `blocked`.

First confirm that this workspace is the exported internal bundle root.
- The bundle root `AGENTS.md` must start with `# AM Bridge Internal Harness`.
- If that is not true, stop and report `BLOCKED`.
- Do not continue if this looks like the external support repository root.

Read these files in order when they exist:
1. `AGENTS.md`
2. `README.md`
3. `bundle-manifest.json`
4. `bootstrap-initial-prompt.md`
5. `operator-script.md`
6. `no-admin-runtime-prompt.md`
7. `.agents/skills/am-page-modernization/SKILL.md`
8. `.agents/skills/am-page-modernization/references/stage-procedure.md`
9. `.agents/skills/am-page-modernization/references/review-contract.md`
10. `integrations/ai-pro/project/am-page-modernization.md`
11. `integrations/ai-pro/project/operator-prompts.md`
12. `integrations/ai-pro/bootstrap/bootstrap-manifest.json`
13. `integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md`
14. `integrations/ai-pro/global/harness-global.md`
15. `integrations/ai-pro/tools/tool-contract.md`
16. `integrations/ai-pro/tools/tool-registry.resolved.json`
17. `integrations/ai-pro/tools/tool-registry.single-tool.resolved.json`
18. `scripts/am_stage.ps1`
19. `scripts/ai_pro_stage_runner.py`
20. `src/am_bridge/__init__.py`
21. `am-bridge.config.json`
22. `prompts/amprompt.md`

Lock these operating assumptions before reporting:
- PM = human operator
- PL = you
- single-model only
- project harness from workspace files is the core control plane
- global `/harness` support is optional
- custom tool registration is optional
- direct command execution is acceptable if registered tools do not exist
- `prompts/amprompt.md`, if present, is supplemental guidance only

Check and report the following:

A. Project harness status
- What is the workspace entry document?
- What is the required AM page workflow?
- Does the workflow clearly say `stage1 -> review -> stage2 -> stage3`?
- Does it clearly say stage1 is not final truth?
- Does it clearly say `review.json` is the correction layer?

B. Runtime capability status
- Is direct command execution or shell execution available?
- Is Python available or at least expected to be available?
- Is `scripts/am_stage.ps1` present?
- Is `scripts/ai_pro_stage_runner.py` present?
- Is `src/am_bridge` present for local runtime imports?
- Are global command installation and custom tool registration available, blocked, or unverified?

C. Execution path decision
- Choose exactly one default runtime path for this workspace:
  1. `scripts/am_stage.ps1`
  2. `python scripts/ai_pro_stage_runner.py ...`
  3. registered `am-bridge-stage*` tools
  4. `am-bridge-analyze ...`
- If more than one path is possible, prefer the simplest path that does not depend on admin features.

D. Config readiness
- Does `am-bridge.config.json` exist?
- Are `sourceRoots` and `backendRoots` sample-only or real project paths?
- If sample-only, say that this workspace is ready only for sample validation, not real project execution.

E. Optional prompt layering
- Does `prompts/amprompt.md` exist?
- If it exists, explain in one short sentence what it is allowed to influence.

If command execution is allowed, you may run only lightweight checks:
- `python --version`
- `python scripts/ai_pro_stage_runner.py --help`
- `powershell -ExecutionPolicy Bypass -File scripts/am_stage.ps1 stage1 DefApp/Win32/form.xml`

Do not run any other stage command in this readiness pass.

Return only this report format:

## Contract
- PM:
- PL:
- Tool layer:
- Runtime mode:

## Workspace Check
- workspace kind:
- bundle root valid:
- evidence:

## Harness Status
- project harness:
- stage workflow:
- correction layer:
- stage truth rule:

## Runtime Capability
- direct command support:
- python support:
- local wrapper:
- runner script:
- runtime package:
- global harness support:
- tool registration support:

## Default Execution Path
- selected path:
- reason:
- blocked alternatives:

## Config Status
- config file:
- sourceRoots:
- backendRoots:
- classification: `real` | `sample-only` | `missing`

## Optional Prompt Layer
- amprompt present:
- allowed influence:

## Overall Readiness
- status: `READY_FOR_REAL_PROJECT` | `READY_FOR_SAMPLE_VALIDATION` | `PARTIAL` | `BLOCKED`
- evidence:
- blockers:
- next operator action:
```
