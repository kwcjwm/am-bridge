# AI Pro AM Workflow

This workflow is meant for the exported internal workspace, not for the external Codex support repository root.

## Roles

- Human operator: `PM`
- AI Pro with `GLM-4.7` or a stronger successor model: `PL`
- `am-bridge`: optional completeness support under the PL

## Principle

The internal AI is the primary worker.

It should:

- inspect screenshots and source directly
- write the main report
- create the shell/mockup
- decide next implementation steps

Optional deterministic support exists only to reduce omission risk or provide repeatable appendices.

## Default Flow

1. inspect screenshot or running-screen evidence
2. inspect XML and source directly
3. write the canonical English main report
4. create the shell/mockup
5. if needed, add exhaustive appendices through optional completeness support
6. derive the Korean delivery report
7. move to implementation or conversion work

## What Optional Support Is For

- full dataset inventory
- full component inventory
- full transaction inventory
- backend candidate appendix
- machine-generated CSV references

## What Optional Support Is Not For

- final shell truth
- dominant business interpretation
- primary report narrative
- mandatory workflow gating

## Expected Outcome

When the PM gives `aaa.xml`, the internal AI should be able to:

- recover a near-like-for-like shell from screenshot evidence when that evidence exists
- analyze the page and related backend chain directly from source
- write a readable standalone English report with numbered sections
- link exhaustive CSV or appendix files from the matching report section
- derive a Korean delivery summary from the reviewed English report
