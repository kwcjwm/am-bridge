# AM Bridge Harness

## Trigger Rules

- Use `$am-page-modernization` when the user asks to analyze a MiPlatform/XPlatform/Nexacro page for AM work.
- Use `$am-page-modernization` when the user wants page-level conversion planning, starter generation, or staged frontend/backend modernization.
- Treat the human user as `PM`.
- Treat the AI assistant as the working `PL`.
- Treat `am-bridge` CLI stages as deterministic tools under the PL.

## Layout

- `.agents/agents/`
- `.agents/skills/`
- `artifacts/analysis/`
- `artifacts/packages/`
- `artifacts/plans/`
- `artifacts/reviews/`
- `artifacts/starter/`

## Current Components

- agents: `am-pl`
- skills: `am-page-modernization`
- tools: `am-bridge-analyze analyze|stage1|stage2|stage3`

## Execution Entry Points

- Use `/harness` to check or refresh the project harness itself.
- Use `am-page-modernization` for actual page-level AM work.
- Give a concrete legacy page such as `aaa.xml`, then let the PL run `stage1 -> review -> stage2 -> stage3`.
- Keep PM decisions in conversation, but keep technical corrections in the review JSON so the next stage can reuse them.

## Working Rule

- Do not treat stage 1 as final truth.
- Always allow an AI review pass before stage 2 when dataset salience or backend tracing looks wrong.
- Keep deterministic extraction and probabilistic judgment separate.

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-09 | Added AM page modernization harness, stage workflow, and review loop | Let AI Pro act as PL on top of deterministic AM tools |
