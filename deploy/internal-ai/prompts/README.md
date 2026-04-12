# Custom Prompt Assets

Place operator-supplied prompt assets here when you want them carried into the internal AI workspace.

Recommended file:

- `amprompt.md`

Role of `amprompt.md`:

- preferred prompt for high-detail Korean report structure
- preferred prompt for section names, 세부항목, 표 형식, ASCII 규칙
- supplemental prompt for customer-facing UI shell quality and section naming
- reference material after the core internal harness has been loaded

Do not use it to replace the core AI-first harness rules.
The internal AI should still follow:

- `AGENTS.md`
- `bootstrap-initial-prompt.md`
- `.agents/skills/am-page-modernization/SKILL.md`

Use `amprompt.md` as the first report heading/detail contract.
If it is missing or incomplete, fall back to `REPORT-CONTRACT.md`.
