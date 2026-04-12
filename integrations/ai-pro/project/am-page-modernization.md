# AM Page Modernization For AI Pro

Use this as the project-level AM workflow definition inside AI Pro.

## Roles

- Human operator: `PM`
- Internal AI: `PL`
- `am-bridge`: optional completeness support only

## Core Principle

The internal AI is the primary worker.

It should:

- inspect screenshots and source directly
- write the Korean main report
- create the shell/mockup
- decide the next implementation move

It may use `am-bridge` only when exhaustive inventories or repeatable cross-checks are needed.

## Default Flow

1. inspect screenshot/running-screen evidence
2. inspect XML and source directly
3. if `prompts/amprompt.md` exists, use it first for report headings and detail rules
4. write the canonical Korean main report
5. create the shell/mockup
6. add optional completeness appendices only when needed, and link them from the matching numbered section of the report

## Hard Rules

- do not make deterministic output the default truth
- do not treat starter generation as the shell source of truth
- do not replace the main report with a link-only index
- do not create English-first output by default
- do not use optional support unless it materially improves completeness or repeatability

## Good Uses Of Optional Support

- full dataset list
- full component list
- full transaction list
- backend candidate appendix

## Bad Uses Of Optional Support

- final layout judgment
- primary shell generation
- dominant business interpretation
- final report narrative
