# AM Bridge Internal AI Workspace

This directory is the source for the internal single-model AM workspace.

Use the exported bundle as the workspace root inside the company environment.
Do not point the internal AI at the root of the external support repository.

The internal bundle is now `AI-first` and `docs-first`.

What the internal AI should do by default:

- read screenshots and running-screen captures
- read XML and source directly
- write the canonical Korean main report
- create the first shell/mockup
- use CSV and appendices only as supporting detail

What optional deterministic support may do:

- help enumerate exhaustive dataset/component/transaction lists
- surface backend candidate traces
- provide machine-generated reference material when the AI-written report needs a completeness appendix

What optional deterministic support should not do by default:

- decide the final page layout
- decide the dominant business interpretation
- generate the primary shell/mokcup truth
- become the mandatory workflow engine

Start with:

1. `bootstrap-initial-prompt.md`
2. `WORKFLOW.md`
3. `REPORT-CONTRACT.md`
4. `operator-script.md`

If you already have a strong operator-authored prompt such as `amprompt.md`, place it under `deploy/internal-ai/prompts/`.
It will be exported into bundle-root `prompts/amprompt.md`.
