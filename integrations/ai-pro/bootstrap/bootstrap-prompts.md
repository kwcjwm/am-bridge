# AI Pro Bootstrap Prompts

These prompts are for the human operator to paste into AI Pro after opening the exported internal workspace in the target environment.

## Prompt 0: Internal Workspace Readiness Check

Use `bootstrap-initial-prompt.md` as the first message in the internal AI workspace.
Do not start with the prompts below until the readiness report is complete.

## Prompt 1: Discover The AI Pro Environment

```text
You are preparing the exported internal AM workspace for AI Pro + GLM-4.7.

First, inspect the local AI Pro environment and discover:
- whether this workspace is the exported internal bundle root
- whether workspace files can be read directly
- whether direct command execution is possible
- whether Python is available
- whether global prompts or slash commands are supported
- whether tool registrations are supported

Use these workspace files as the source of truth:
- integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md
- integrations/ai-pro/bootstrap/bootstrap-manifest.json
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/tools/tool-contract.md

Do not make assumptions silently.
Report the capabilities you discovered before editing anything.
```

## Prompt 2: Activate The Project Harness

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

Activate the AM project harness for this workspace.

Use these files:
- AGENTS.md
- bootstrap-initial-prompt.md
- no-admin-runtime-prompt.md
- .agents/skills/am-page-modernization/SKILL.md
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/project/operator-prompts.md

Keep the PM/PL contract intact:
- human operator = PM
- GLM-4.7 = PL
- am-bridge = deterministic tool layer

If AI Pro cannot use the Codex-style project files directly, register the portable workflow prompt from integrations/ai-pro/project/.
```

## Prompt 3: Select A Runnable Execution Path

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

Choose the default runtime path for this workspace.

Check these candidates in order:
1. scripts/am_stage.ps1
2. python scripts/ai_pro_stage_runner.py ...
3. registered am-bridge-stage1, am-bridge-stage2, am-bridge-stage3
4. am-bridge-analyze ...

Pick the first path that is actually available and does not depend on blocked admin features.
Do not claim success without evidence.
Report the selected path and the blocked alternatives.
```

## Prompt 4: Optional Global Harness

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

If the platform allows global command or global prompt installation, install the global harness using:
- integrations/ai-pro/global/harness-global.md

Preferred result:
- /harness becomes available

If AI Pro does not support slash commands but does support saved prompts, create the nearest equivalent and report the exact alias you chose.
After installation, verify that the global harness can inspect workspace harness files.
```

If global command installation is blocked by server policy, skip this prompt.

## Prompt 5: Optional Tool Registration

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

If the platform allows custom tool registration, register am-bridge as callable deterministic tools for AI Pro.

Use:
- scripts/ai_pro_stage_runner.py
- integrations/ai-pro/tools/tool-contract.md
- integrations/ai-pro/tools/tool-registry.example.json
- integrations/ai-pro/tools/tool-registry.single-tool.example.json

Prefer three fixed tools if the environment supports them:
- am-bridge-stage1
- am-bridge-stage2
- am-bridge-stage3

If the environment only supports one parameterized tool, register one am-bridge-stage tool instead.
After registration, show the resolved commands or config entries you created.
```

If custom tool registration is blocked by server policy, skip this prompt and keep the direct execution path from Prompt 3.

## Prompt 6: Point The Config To The Real Legacy Project

```text
Update am-bridge.config.json for the real target project.

I will provide:
- sourceRoots
- backendRoots

Do not leave sample paths in place if real paths are available.
After the update, summarize the configured roots.
```

If you want to prove the bundle first with the bundled public sample, do Prompt 7 before this step.

## Prompt 7: Validate The Whole Stack

```text
Validate the AI Pro bootstrap for this workspace.

1. Confirm the project harness is discoverable from workspace files.
2. Confirm the selected runtime path still works.
3. Run stage1 on the bundled sample page or another known page exposed by the configured sourceRoots.
4. Confirm key stage1 decisions are present.
5. Run stage2 and confirm a Vue page config JSON and PM checklist are emitted if stage1 succeeded.

If the bundled sample form.xml is used, expect:
- primaryDatasetId = ds_scorechk
- mainGridComponentId = Grid0
- backend trace to sampleDAO.ScoreChk

Report:
- project harness status
- selected runtime path
- global harness status
- tool status
- config status
- validation result
- next operator action
```

## Prompt 8: All-In-One Bootstrap

```text
Bootstrap this exported internal workspace for AI Pro + GLM-4.7 end to end.

Use these sources:
- integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md
- integrations/ai-pro/bootstrap/bootstrap-manifest.json
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/tools/tool-contract.md
- scripts/ai_pro_stage_runner.py

Tasks:
1. Discover the local AI Pro capability set.
2. Activate the project harness.
3. Select a runnable deterministic execution path.
4. Optionally install the global harness if the platform allows it.
5. Optionally register am-bridge tools if the platform allows it.
6. Tell me what values are still needed for am-bridge.config.json.
7. Validate the installed setup as far as possible.

Do not claim success unless each step was actually completed or explicitly blocked.
```
