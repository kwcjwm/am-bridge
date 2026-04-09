# AM Prompt

Replace this file with your validated prompt-engineered AM prompt.

Recommended use:

- detailed analysis report guidance
- detailed Vue conversion config guidance
- richer PM-facing explanation structure

Do not use this file to override the staged execution contract.
The core execution order remains:

1. stage1
2. review
3. stage2
4. stage3

When this file contains real content, the internal AI should read it only after:

1. `AGENTS.md`
2. `bootstrap-initial-prompt.md` when bootstrapping
3. `.agents/skills/am-page-modernization/SKILL.md`

Then it may use `amprompt.md` as a supplemental detail contract for report quality and config completeness.
