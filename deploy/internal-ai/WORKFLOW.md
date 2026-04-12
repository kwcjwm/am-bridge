# Workflow

## Goal

Do AM well.
The internal AI is the primary worker.
This workspace exists to constrain output quality and delivery format, not to force deterministic execution.

## Default Flow

1. Gather inputs
   - page XML
   - matching main page image using the default rule `<page>.xml` -> `<page>.jpg`
   - related source
   - screenshots or running-screen captures
   - PM notes
   - if the matching main page image is missing, ask the PM/operator to provide it first
2. Recover the shell first when layout fidelity matters.
   - treat the matching `<page>.jpg` file as the primary visual source for the page shell
3. Analyze behavior, data flow, backend flow, and boundary decisions from XML and source.
4. Write the canonical Korean main report in the required format.
5. Create or refine the mockup/page shell.
6. If the report looks good but exhaustive long-tail details are missing, use optional deterministic support to fill numbered `Detailed Inventory` appendices only.
7. If implementation is requested, create the converted page or implementation plan from the reviewed report and shell.

## Optional Deterministic Support

Use deterministic support only when one of these is true:

- the report needs a complete inventory table
- the page has too many datasets/components/transactions to trust memory alone
- backend trace candidates need a repeatable appendix
- the PM explicitly asks for a machine-generated cross-check

Do not use deterministic support by default for:

- shell generation
- dominant dataset judgment
- business interpretation
- final report narrative

## Output Locations

- `inputs/source/`
- `inputs/screenshots/`
- `inputs/notes/`
- `artifacts/visual/`
- `artifacts/reports/`
- `artifacts/decisions/`
- `artifacts/implementation/`
