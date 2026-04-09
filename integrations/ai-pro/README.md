# AI Pro Deployment Kit

This directory is the carry-in package for `AI Pro + GLM-4.7`.

The deployment model has three layers:

1. Global harness
   Enable `/harness` or an equivalent global command in AI Pro.
2. Project harness
   Teach AI Pro how this AM project is supposed to work.
3. Tool wiring
   Expose `am-bridge` as deterministic tools that the model can call.

## 1. Global Harness

Use [global/harness-global.md](C:/workspace/am-bridge/integrations/ai-pro/global/harness-global.md) as the source for the global `/harness` behavior.

AI Pro needs one of these capabilities:

- a global slash command registry
- a global prompt library
- a global system-prompt slot that can be bound to a command alias

Recommended mapping:

- command: `/harness`
- source file: `integrations/ai-pro/global/harness-global.md`

## 2. Project Harness

Use these files for the project-level AM workflow:

- [AGENTS.md](C:/workspace/am-bridge/AGENTS.md)
- [.agents/skills/am-page-modernization/SKILL.md](C:/workspace/am-bridge/.agents/skills/am-page-modernization/SKILL.md)
- [project/am-page-modernization.md](C:/workspace/am-bridge/integrations/ai-pro/project/am-page-modernization.md)
- [project/operator-prompts.md](C:/workspace/am-bridge/integrations/ai-pro/project/operator-prompts.md)

If AI Pro can read workspace files directly, keep `AGENTS.md` and `.agents/` in the workspace and point AI Pro at them.

If AI Pro cannot read Codex skill format directly, use the portable prompt files under `integrations/ai-pro/project/`.

## 3. Tool Wiring

Expose `am-bridge` through [scripts/ai_pro_stage_runner.py](C:/workspace/am-bridge/scripts/ai_pro_stage_runner.py).

Recommended tool registrations:

- `am-bridge-stage1`
- `am-bridge-stage2`
- `am-bridge-stage3`

Use [tools/tool-registry.example.json](C:/workspace/am-bridge/integrations/ai-pro/tools/tool-registry.example.json) as the registration template.

The runner returns JSON so GLM-4.7 can consume artifact paths and key decisions without parsing human-oriented console output.

## Deployment Order

1. Install the global harness prompt.
2. Install or expose the project harness files.
3. Register the `am-bridge` stage tools.
4. Point `am-bridge.config.json` to the real legacy source roots and backend roots.
5. Run `/harness`.
6. Run the AM page workflow prompt against `aaa.xml`.

## GLM-4.7 Operating Rules

For this project, GLM-4.7 should:

- work one page at a time
- prefer stage artifacts over raw legacy dumps
- correct weak analysis in `review.json`
- treat `am-bridge` as evidence extraction, not as final judgment
- keep PM decisions in conversation and technical corrections in artifacts

## Export

Use [scripts/export_ai_pro_bundle.py](C:/workspace/am-bridge/scripts/export_ai_pro_bundle.py) to build a ready-to-copy bundle for another environment.

## Bootstrap With GLM-4.7

If the repo is cloned into another machine and GLM-4.7 should perform the setup work there, start here:

- [bootstrap/glm-bootstrap-playbook.md](C:/workspace/am-bridge/integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md)
- [bootstrap/bootstrap-prompts.md](C:/workspace/am-bridge/integrations/ai-pro/bootstrap/bootstrap-prompts.md)
- [bootstrap/bootstrap-manifest.json](C:/workspace/am-bridge/integrations/ai-pro/bootstrap/bootstrap-manifest.json)

Those files tell GLM-4.7 how to:

1. install the global harness
2. activate the project harness
3. register `am-bridge` tools
4. verify the whole stack
