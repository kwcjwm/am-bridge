# AI Pro Bootstrap Prompts

These prompts are for the human operator to paste into AI Pro after cloning this repository into the target environment.

## Prompt 1: Discover The AI Pro Environment

```text
You are preparing this repository for AI Pro + GLM-4.7.

First, inspect the local AI Pro environment and discover:
- where global prompts or slash commands are stored
- where project prompts or workflow definitions are stored
- where tool registrations are stored
- whether Python is available

Use these repository files as the source of truth:
- integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md
- integrations/ai-pro/bootstrap/bootstrap-manifest.json
- integrations/ai-pro/global/harness-global.md
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/tools/tool-contract.md

Do not make assumptions silently.
Report the paths and formats you discovered before editing anything.
```

## Prompt 2: Install The Global Harness

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

Install the global harness for AI Pro using:
- integrations/ai-pro/global/harness-global.md

Preferred result:
- /harness becomes available

If AI Pro does not support slash commands, create the nearest equivalent global prompt and report the exact alias you chose.
After installation, verify that the global harness can inspect workspace harness files.
```

## Prompt 3: Activate The Project Harness

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

Activate the AM project harness for this repository.

Use these files:
- AGENTS.md
- .agents/skills/am-page-modernization/SKILL.md
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/project/operator-prompts.md

Keep the PM/PL contract intact:
- human operator = PM
- GLM-4.7 = PL
- am-bridge = deterministic tool layer

If AI Pro cannot use the Codex-style project files directly, register the portable workflow prompt from integrations/ai-pro/project/.
```

## Prompt 4: Register am-bridge Tools

```text
Follow integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md.

Register am-bridge as callable deterministic tools for AI Pro.

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

## Prompt 5: Point The Config To The Real Legacy Project

```text
Update am-bridge.config.json for the real target project.

I will provide:
- sourceRoots
- backendRoots

Do not leave sample paths in place if real paths are available.
After the update, summarize the configured roots.
```

## Prompt 6: Validate The Whole Stack

```text
Validate the AI Pro bootstrap for this repository.

1. Run /harness or the installed equivalent.
2. Confirm the project harness is discoverable.
3. Run stage1 on a known page.
4. Confirm the tool returns JSON.
5. Confirm the stage1 result includes key page decisions.

If the sample form.xml is used, expect:
- primaryDatasetId = ds_scorechk
- mainGridComponentId = Grid0
- backend trace to sampleDAO.ScoreChk

Report:
- global harness status
- project harness status
- tool status
- config status
- validation result
- next operator action
```

## Prompt 7: All-In-One Bootstrap

```text
Bootstrap this repository for AI Pro + GLM-4.7 end to end.

Use these sources:
- integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md
- integrations/ai-pro/bootstrap/bootstrap-manifest.json
- integrations/ai-pro/global/harness-global.md
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/tools/tool-contract.md
- scripts/ai_pro_stage_runner.py

Tasks:
1. Discover the local AI Pro config locations and formats.
2. Install the global harness.
3. Activate the project harness.
4. Register the am-bridge tools.
5. Tell me what values are still needed for am-bridge.config.json.
6. Validate the installed setup as far as possible.

Do not claim success unless each step was actually completed or explicitly blocked.
```
