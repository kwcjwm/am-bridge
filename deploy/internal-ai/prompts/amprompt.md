# AM Prompt

Replace this file with your validated prompt-engineered AM prompt.

Recommended use:

- detailed Korean report heading guidance
- detailed section/subsection rules
- stronger table/ASCII/report formatting guidance
- richer PM-facing explanation structure

Do not use this file to override the AI-first harness rules.

When this file contains real content, the internal AI should read it only after:

1. `AGENTS.md`
2. `bootstrap-initial-prompt.md` when bootstrapping
3. `.agents/skills/am-page-modernization/SKILL.md`

Then it should use `amprompt.md` as the preferred report heading/detail contract.
If the prompt is incomplete, fill gaps with `REPORT-CONTRACT.md`.
