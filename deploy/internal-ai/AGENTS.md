# AM Bridge Internal Harness

## Trigger Rules

- Use `$am-page-modernization` when the PM wants AM work for a legacy page.
- Treat the human user as `PM`.
- Treat the internal AI as the working `PL`.
- The internal AI is the primary analyst, report writer, and mockup/shell author.
- Deterministic tools are optional support only.
- Do not assume sub-agent features exist in this workspace.

## Layout

- `.agents/skills/`
- `prompts/`
- `inputs/`
- `artifacts/`
- `samples/`
- optional deterministic support:
  - `scripts/`
  - `src/am_bridge/`
  - `am-bridge.config.json`

## Core Documents

- `WORKFLOW.md`
- `REPORT-CONTRACT.md`
- `KOREAN-DELIVERY.md`
- `OPTIONAL-COMPLETENESS-SUPPORT.md`
- `operator-script.md`
- `bootstrap-initial-prompt.md`
- `no-admin-runtime-prompt.md`

## Working Rule

- Start from screenshot, running-screen, XML, and source evidence first.
- If the target page XML is `FF02_DtCode.xml`, the default main page image is `FF02_DtCode.jpg`.
- In general, treat `<page>.xml` -> `<page>.jpg` as the default main page image naming rule.
- If the main page image is missing, ask the PM/operator to provide it before treating the shell as reviewable.
- Build the shell or mockup from visual/source evidence, not from deterministic starter output.
- Use optional deterministic support only when it helps fill exhaustive inventories or candidate traces.
- Do not let optional support decide final layout, dominant dataset judgment, or report narrative by itself.
- English main reports are canonical.
- Korean reports are derived delivery documents.
- Keep shell decisions and behavior/contract decisions separate.
- Do not treat stage-based outputs as mandatory workflow.
- Avoid stage3 starter generation unless the PM explicitly asks for legacy deterministic scaffolding.

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-12 | Reframed the internal harness around AI-led analysis, reporting, and shell creation with optional completeness support only | Keep the internal AI in charge and prevent weak deterministic outputs from becoming default truth |
| 2026-04-12 | Added bundle update metadata, update playbook, and local config override guidance | Let internal AI decide whether future extracted bundles need fresh reinstall or partial update |
| 2026-04-11 | Added `UI Shell First` lane alongside staged behavior / contract lock flow | Let internal AI produce early customer-facing layout agreements without pretending behavior is already fixed |
| 2026-04-10 | Split internal single-model harness into its own source file for exported workspaces | Prevent confusion with the external Codex support workspace |
| 2026-04-09 | Added AM page modernization harness, stage workflow, and review loop | Let AI Pro act as PL on top of deterministic AM tools |
