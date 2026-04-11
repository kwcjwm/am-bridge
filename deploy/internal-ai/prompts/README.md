# Custom Prompt Assets

Place operator-supplied prompt assets here when you want them carried into the internal AI workspace.

Recommended file:

- `amprompt.md`

Role of `amprompt.md`:

- supplemental prompt for high-detail analysis reporting
- supplemental prompt for customer-facing UI shell quality and section naming
- supplemental prompt for richer Vue conversion config generation
- reference material after the core internal harness has been loaded

Do not use it to replace the core staged harness rules.
The internal AI should still follow:

- `AGENTS.md`
- `bootstrap-initial-prompt.md`
- `.agents/skills/am-page-modernization/SKILL.md`

Use `amprompt.md` only as an additional quality and detail contract.
