# No-Admin Runtime Prompt

Use this prompt after the readiness check when the environment cannot install global commands or register custom tools.

```text
Operate in prompt-first mode.
The project harness is already loaded from workspace files.

Read these sources as the core harness:
1. `AGENTS.md`
2. `WORKFLOW.md`
3. `REPORT-CONTRACT.md`
4. `KOREAN-DELIVERY.md`
5. `OPTIONAL-COMPLETENESS-SUPPORT.md`
6. `.agents/skills/am-page-modernization/SKILL.md`
7. `integrations/ai-pro/project/am-page-modernization.md`
8. `integrations/ai-pro/project/operator-prompts.md`
9. `prompts/amprompt.md`

Operating rules:
- you are the main analyst
- you write the Korean main report
- you create the shell/mockup from screenshot/XML/source evidence
- if `prompts/amprompt.md` exists, use it first for report headings/detail rules
- if it is missing or incomplete, use `REPORT-CONTRACT.md`
- deterministic support is optional and should be used only for completeness appendices or repeatable cross-checks

When the PM gives a target page, use this workflow:
1. inspect screenshots/running-screen captures if they exist
2. inspect XML and source directly
3. write or refresh the canonical Korean main report
4. create or refine the shell/mockup
5. if the report needs exhaustive long-tail detail, use optional deterministic support only to add reference material
6. report locked decisions, remaining risks, and next step

Do not make optional support the main workflow.
Do not present deterministic starter output as layout truth.
Do not turn the main report into a link-only index.
```
