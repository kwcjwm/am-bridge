# AI Pro Deployment Kit

This directory contains the internal deployment assets for `AI Pro + GLM-4.7`.

The repository root is an external Codex support workspace.
The company-side AI should not open the root of this repository directly.
Instead, export the internal bundle and open the exported bundle root as its workspace.

The deployment model has three layers:

1. Global harness
   Enable `/harness` or an equivalent global command in AI Pro.
2. Project harness
   Teach AI Pro how this AM project is supposed to work.
3. Tool wiring
   Expose `am-bridge` as deterministic tools that the model can call.

## 1. Global Harness

Use `integrations/ai-pro/global/harness-global.md` as the source for the global `/harness` behavior.

AI Pro needs one of these capabilities:

- a global slash command registry
- a global prompt library
- a global system-prompt slot that can be bound to a command alias

Recommended mapping:

- command: `/harness`
- source file: `integrations/ai-pro/global/harness-global.md`

## 2. Project Harness

Use these files for the project-level AM workflow:

- `AGENTS.md`
- `bootstrap-initial-prompt.md`
- `operator-script.md`
- `prompts/amprompt.md` when a custom detailed AM prompt is provided
- `.agents/skills/am-page-modernization/SKILL.md`
- `integrations/ai-pro/project/am-page-modernization.md`
- `integrations/ai-pro/project/operator-prompts.md`

If AI Pro can read workspace files directly, point it at the exported bundle root, not this repository root.
The first user message inside the company-side workspace should be the contents of `bootstrap-initial-prompt.md`.
For the shortest operator path, follow `operator-script.md`.
If `prompts/amprompt.md` exists, treat it as supplemental detail guidance after the core harness is active.

If AI Pro cannot read Codex skill format directly, use the portable prompt files under `integrations/ai-pro/project/`.

## 3. Tool Wiring

Expose `am-bridge` through `scripts/ai_pro_stage_runner.py`.

Recommended tool registrations:

- `am-bridge-stage1`
- `am-bridge-stage2`
- `am-bridge-stage3`

Use `integrations/ai-pro/tools/tool-registry.example.json` as the registration template.

The runner returns JSON so GLM-4.7 can consume artifact paths and key decisions without parsing human-oriented console output.
It also produces:

- stage 1 detailed analysis report
- stage 2 Vue page config JSON
- stage 2 PM-facing test checklist
- stage 3 starter bundle plus copied Vue config
- stage 3 copied PM checklist

## Deployment Order

1. Open the exported bundle root, not the source repository root.
2. Install the global harness prompt.
3. Paste `bootstrap-initial-prompt.md` and review the readiness report.
4. Install or expose the project harness files.
5. Register the `am-bridge` stage tools.
6. Run `/harness`.
7. Run the bundled sample validation or another known page.
8. Only after validation, point `am-bridge.config.json` to the real legacy source roots and backend roots.

## GLM-4.7 Operating Rules

For this project, GLM-4.7 should:

- work one page at a time
- prefer stage artifacts over raw legacy dumps
- correct weak analysis in `review.json`
- treat `am-bridge` as evidence extraction, not as final judgment
- keep PM decisions in conversation and technical corrections in artifacts

## Export

Use `scripts/export_ai_pro_bundle.py` to build a ready-to-copy bundle for another environment.
The exported bundle is the only workspace that should be opened in the internal company AI environment.

## Bootstrap With GLM-4.7

If the exported internal bundle is copied into another machine and GLM-4.7 should perform the setup work there, start here:

- `integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md`
- `integrations/ai-pro/bootstrap/bootstrap-prompts.md`
- `integrations/ai-pro/bootstrap/bootstrap-manifest.json`

Those files tell GLM-4.7 how to:

1. install the global harness
2. activate the project harness
3. register `am-bridge` tools
4. verify the whole stack
