# Internal AI Pro Operator Script

Use this when you want the shortest path inside the company environment.

## First Install

1. Open the exported bundle root in AI Pro.
2. Paste `bootstrap-initial-prompt.md`.
3. If the environment is restricted, paste `no-admin-runtime-prompt.md`.

## Real Page Work

Give the internal AI:

- the target page XML
- the matching main page image with the same base name and `.jpg` extension
- related source
- screenshots or running-screen captures when available
- any PM notes

Then instruct it to:

1. follow `WORKFLOW.md`
2. follow `REPORT-CONTRACT.md`
3. if `prompts/amprompt.md` exists, use it first for report headings and detail rules
4. write the Korean main report first
5. build the shell/mockup from visual/source evidence
6. use optional completeness support only if exhaustive reference detail is needed

## Short Operator Prompt

```text
Use this workspace for AM on one page.

Target page: C:\path\to\aaa.xml

Use these rules:
1. If the target page is `FF02_DtCode.xml`, require `FF02_DtCode.jpg` as the default main image.
2. In general, look for the matching `<page>.jpg` file first.
3. If the main image is missing, ask me to provide it before treating the shell as reviewable.
4. Read screenshots and source first.
5. If `prompts/amprompt.md` exists, use it first for report headings and detail rules.
6. Write the canonical Korean main report following REPORT-CONTRACT.md.
7. Create the shell/mockup from visual/source evidence.
8. If the report needs exhaustive appendix detail, use OPTIONAL-COMPLETENESS-SUPPORT.md.
9. Keep shell/layout decisions separate from behavior/API/SQL decisions.

At the end, show:
- the Korean main report path
- any appendix/reference paths
- the shell/mockup path
- the next implementation step
```

## Optional Deterministic Support

Only if needed, the internal AI may also use:

- `scripts/am_stage.ps1`
- `python scripts/ai_pro_stage_runner.py ...`
- `am-bridge-analyze ...`

These are optional cross-check tools.
They are not the primary workflow.

If optional support needs real project roots, use `am-bridge.config.local.json` and keep `am-bridge.config.json` unchanged.
