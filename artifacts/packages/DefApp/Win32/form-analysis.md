# Detailed Legacy Analysis Report

## Contents

- [Executive Summary](#executive-summary)
- [Screen Story](#screen-story)
- [Primary Data Model (3)](#primary-data-model-3)
- [Action And Event Flow (4)](#action-and-event-flow-4)
- [Backend Trace Summary (2)](#backend-trace-summary-2)
- [Related Screens (2)](#related-screens-2)
- [Migration Implications](#migration-implications)
- [Evidence Registry Links](#evidence-registry-links)

## Executive Summary

- This page behaves as a `grid-page` centered on `ds_scorechk`.
- Main visible result area is `Grid0` and primary transaction is `TX-BUTTON0ONCLICK-1`.
- Backend traces resolved: `2` / unresolved related screens: `1`.
- Source file: `C:\workspace\am-bridge\samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\form.xml`.

## Screen Story

- The page opens as `main` and centers the user on `Grid0` backed by `ds_scorechk`.
- Initial event is `form_OnLoadCompleted` and should be reviewed for preload or lookup behavior.
- Primary visible actions detected: 성적조회, form, 과목 담당교수, 장학금대상.
- Related navigation count: `2`.

## Primary Data Model (3)

| Dataset | Role | Usage | Columns | Bound Components | Salience |
| --- | --- | --- | --- | --- | --- |
| ds_scorechk [PRIMARY] | response | main-grid | 5 | Grid0 | 171 |
| ds_testCategory | code | code-lookup | 2 | Combo0 | 25 |
| ds_screen | view-state | view-state | 3 | none | 0 |

## Action And Event Flow (4)

| Handler | Trigger | Transactions | Reads | Writes | Summary |
| --- | --- | --- | --- | --- | --- |
| Button0_OnClick | 성적조회 | TX-BUTTON0ONCLICK-1 | none | none | Combo0 |
| form_OnLoadCompleted | form | none | none | none | no direct UI control |
| Button1_OnClick | 과목 담당교수 | none | ds_screen | none | subview -> scurl |
| Button2_OnClick | 장학금대상 | none | none | none | popup -> DefApp::scholarship.xml |

## Backend Trace Summary (2)

| Transaction | Controller | Service | DAO | SQL Map | Tables |
| --- | --- | --- | --- | --- | --- |
| TX-TESTNAMESELECT-1 | EgovSampleController.selectTestList | EgovSampleServiceImpl.testNameList | SampleDAO.testNameList | sampleDAO.testNameList | score_jew |
| TX-BUTTON0ONCLICK-1 | EgovSampleController.selectScoreList | EgovSampleServiceImpl.ScoreChk | SampleDAO.ScoreChk | sampleDAO.ScoreChk | score_jew, student_jew |

## Related Screens (2)

| Type | Target | Trigger | Status | Resolved Page |
| --- | --- | --- | --- | --- |
| subview | scurl | Button1_OnClick | unresolved | unresolved |
| popup | DefApp::scholarship.xml | Button2_OnClick | resolved | scholarship |

## Migration Implications

- Treat ds_scorechk as the primary business dataset unless review overrides say otherwise.
- Primary dataset reasons: largest-grid:Grid0, transaction-output:TX-BUTTON0ONCLICK-1, wide-schema:5, default-records:1
- Resolved backend chain begins at EgovSampleController.selectScoreList.
- Treat popup/subview navigation targets as related screens. Do not merge them into the current page implementation by default.
- Treat stage 1 output as evidence plus candidate judgment, not as immutable truth.
- Run AI review before stage 2 whenever the page has a dominant grid, dynamic transaction wrappers, or ambiguous backend traces.
- review-note: If the dominant result dataset is wrong, update primaryDatasetId and dataset.primaryUsage before stage 2.
- review-note: If AI found a better backend chain, override the affected backendTraces entry and rerun stage 1 or continue into stage 2 with that review file.

## Evidence Registry Links

- package-json: [package-json](form-package.json)
- review-json: [review-json](../../../reviews/DefApp/Win32/form-review.json)
- page-spec: [page-spec](../../../target/DefApp/Win32/form-spec.md)
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
