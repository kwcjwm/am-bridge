# AM Bridge Internal Harness

## Trigger Rules

- Use `$am-page-modernization` when the user asks to analyze a MiPlatform/XPlatform/Nexacro page for AM work.
- Use `$am-page-modernization` when the user wants page-level conversion planning, starter generation, or staged frontend/backend modernization.
- Treat the human user as `PM`.
- Treat the AI assistant as the working `PL`.
- Treat `am-bridge` CLI stages as deterministic tools under the PL.
- Do not assume sub-agent features exist in this workspace.

## Layout

- `.agents/skills/`
- `prompts/`
- `artifacts/analysis/`
- `artifacts/packages/`
- `artifacts/plans/`
- `artifacts/reviews/`
- `artifacts/starter/`
- `integrations/ai-pro/`

## Current Components

- single-model operating role: `PL`
- skills: `am-page-modernization`
- baseline execution path: `scripts/am_stage.ps1 <stage> <page>`
- direct runner fallback: `python scripts/ai_pro_stage_runner.py <stage> <page> --config am-bridge.config.json`
- optional registered tools when the platform allows them: `am-bridge-stage1`, `am-bridge-stage2`, `am-bridge-stage3`
- direct CLI fallback only when explicitly available: `am-bridge-analyze analyze|stage1|stage2|stage3`

## Execution Entry Points

- First, use `bootstrap-initial-prompt.md` to produce a readiness report for this workspace.
- If the environment has no admin capability for global commands or custom tool registration, use `no-admin-runtime-prompt.md` after readiness.
- If the operator wants the shortest end-to-end setup path, use `operator-script.md`.
- If `prompts/amprompt.md` contains a real project prompt, use it as a supplemental detail contract after the core harness is loaded.
- Use `am-page-modernization` for actual page-level AM work.
- Give a concrete legacy page such as `aaa.xml`, then let the PL run `stage1 -> review -> stage2 -> stage3`.
- Keep PM decisions in conversation, but keep technical corrections in the review JSON so the next stage can reuse them.
- Operate with one model plus deterministic tools and saved artifacts only.

## Working Rule

- Do not treat stage 1 as final truth.
- Always allow an AI review pass before stage 2 when dataset salience or backend tracing looks wrong.
- Keep deterministic extraction and probabilistic judgment separate.
- Reuse saved package, plan, review, and starter artifacts instead of rebuilding context from scratch.
- Ignore any external preparation workflow; this workspace is for internal execution only.
- Treat `prompts/amprompt.md` as supplemental guidance, not as a replacement for the staged harness.
- Lack of global harness installation or custom tool registration does not block work if direct command execution is available.

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-10 | Split internal single-model harness into its own source file for exported workspaces | Prevent confusion with the external Codex support workspace |
| 2026-04-09 | Added AM page modernization harness, stage workflow, and review loop | Let AI Pro act as PL on top of deterministic AM tools |
