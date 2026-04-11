# Stage 1 - Conversion Package

## Contents

- [Executive Summary](#executive-summary)
- [Key Decisions](#key-decisions)
- [Main User Flows (4)](#main-user-flows-4)
- [Backend Trace Summary (2)](#backend-trace-summary-2)
- [Risks / Open Questions (2)](#risks-open-questions-2)
- [Artifact Index](#artifact-index)
- [Review Guidance](#review-guidance)

## Executive Summary

- Page: `form` / `New Form`
- Interaction pattern: `grid-page`
- Primary business result: dataset `ds_scorechk` / grid `Grid0`
- Primary transaction: `TX-BUTTON0ONCLICK-1`
- Related screens: `2` detected, `1` unresolved

## Key Decisions

- `ds_scorechk` remains the main result dataset unless review overrides change it.
- `grid-page` interaction pattern should be preserved before UI redesign.
- Treat popup/subview targets as separate screens, not inline fragments of the current page.
- Use `review.json` for corrections; do not carry technical fixes only in chat.

## Main User Flows (4)

| Flow | Trigger | Transaction | Navigation | Summary |
| --- | --- | --- | --- | --- |
| User action | 성적조회 | TX-BUTTON0ONCLICK-1 | none | calls TX-BUTTON0ONCLICK-1; controls Combo0 |
| Initial load | form | none | none | manual review required |
| User action | 과목 담당교수 | none | subview | subview -> scurl; controls Div0 |
| User action | 장학금대상 | none | popup | popup -> DefApp::scholarship.xml |

## Backend Trace Summary (2)

| Transaction | Route | Controller | SQL Map | Tables |
| --- | --- | --- | --- | --- |
| TX-TESTNAMESELECT-1 | http://127.0.0.1:8080/miplatform/testNameList.do | EgovSampleController.selectTestList | sampleDAO.testNameList | score_jew |
| TX-BUTTON0ONCLICK-1 | http://127.0.0.1:8080/miplatform/testScoreChk.do | EgovSampleController.selectScoreList | sampleDAO.ScoreChk | score_jew, student_jew |

## Risks / Open Questions (2)

- Related screen target scurl could not be resolved automatically. Confirm whether it should be treated as a separate page.
- TX-FNCMTR-1 uses a dynamic or wrapper URL. Confirm the final endpoint contract manually.

## Artifact Index

- package-json: [package-json](form-package.json)
- review-json: [review-json](../../../reviews/DefApp/Win32/form-review.json)
- page-spec: [page-spec](../../../target/DefApp/Win32/form-spec.md)
- page report hub: [page report hub](../../../reports/DefApp/Win32/form/README.md)
- stage1 report pack: [stage1 report pack](../../../reports/DefApp/Win32/form/stage1/README.md)
- Registry directory: [../../../reports/DefApp/Win32/form/stage1/registries](../../../reports/DefApp/Win32/form/stage1/registries)
- Registry: [datasets.csv](../../../reports/DefApp/Win32/form/stage1/registries/datasets.csv)
- Registry: [dataset-columns.csv](../../../reports/DefApp/Win32/form/stage1/registries/dataset-columns.csv)
- Registry: [components.csv](../../../reports/DefApp/Win32/form/stage1/registries/components.csv)
- Registry: [bindings.csv](../../../reports/DefApp/Win32/form/stage1/registries/bindings.csv)
- Registry: [functions.csv](../../../reports/DefApp/Win32/form/stage1/registries/functions.csv)
- Registry: [events.csv](../../../reports/DefApp/Win32/form/stage1/registries/events.csv)
- Registry: [transactions.csv](../../../reports/DefApp/Win32/form/stage1/registries/transactions.csv)
- Registry: [backend-traces.csv](../../../reports/DefApp/Win32/form/stage1/registries/backend-traces.csv)
- Registry: [navigation.csv](../../../reports/DefApp/Win32/form/stage1/registries/navigation.csv)
- Registry: [validation-rules.csv](../../../reports/DefApp/Win32/form/stage1/registries/validation-rules.csv)
- Registry: [state-rules.csv](../../../reports/DefApp/Win32/form/stage1/registries/state-rules.csv)
- Registry: [messages.csv](../../../reports/DefApp/Win32/form/stage1/registries/messages.csv)
- Registry: [grid-columns.csv](../../../reports/DefApp/Win32/form/stage1/registries/grid-columns.csv)

## Review Guidance

- Validate the primary dataset and dominant grid before downstream generation.
- Resolve unresolved related screens and dynamic wrapper transactions before treating stage 1 as stable.
- Keep technical corrections in `review.json` so the next run can reuse them.
