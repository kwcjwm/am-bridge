# PM Test Checklist - form

## Scope

- Legacy page: C:\workspace\am-bridge\samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\form.xml
- Page name: New Form
- Page type: main
- Target route: /form
- Vue page: FormPage
- Interaction pattern: grid-page
- Primary dataset: ds_scorechk
- Secondary datasets: ds_testCategory
- Main grid: Grid0
- Primary transactions: TX-BUTTON0ONCLICK-1

## PM Smoke Checks

- [ ] The page opens without blocking errors and shows the intended business title/context.
- [ ] The dominant business area is centered on dataset `ds_scorechk` and grid/component `Grid0`.
- [ ] Search, result, and reference/code datasets are clearly separated in the rendered screen behavior.
- [ ] Search controls are present and usable: Button0, Combo0, Button1, Button2.

## Data Retrieval Checks

- [ ] `TX-BUTTON0ONCLICK-1` calls `http://127.0.0.1:8080/miplatform/testScoreChk.do` via `EgovSampleController.selectScoreList` and refreshes `ds_scorechk`.

## Functional Scenario Checks

- [ ] `Button0_OnClick` behaves as expected. Transactions: TX-BUTTON0ONCLICK-1. Reads: no read dataset captured. Writes: no write dataset captured. Controls: Combo0.
- [ ] `Button1_OnClick` behaves as expected. Transactions: no direct transaction captured. Reads: ds_screen. Writes: no write dataset captured. Controls: Div0.

## Backend And Integration Spot Checks

- [ ] `TX-BUTTON0ONCLICK-1` keeps the intended backend chain `EgovSampleController.selectScoreList -> EgovSampleServiceImpl.ScoreChk -> SampleDAO.ScoreChk` and preserves SQL behavior `sampleDAO.ScoreChk`.

## Related Screen Checks

- [ ] Clarify unresolved related target `scurl` before merging it into any current-page implementation.
- [ ] `Button2_OnClick` opens `scholarship` from legacy target `DefApp::scholarship.xml` as a separate related screen with the expected handoff.

## Negative And Regression Checks

- [ ] Empty-result and no-data cases behave safely and keep the page usable.
- [ ] Validation and business error messages match the original user flow expectations.
- [ ] Backend failure or timeout cases do not leave the page in an inconsistent state.
- [ ] Shared platform functions were not reimplemented locally without approval.

## Open Questions To Resolve

- [ ] Related screen target scurl could not be resolved automatically. Confirm whether it should be treated as a separate page.
- [ ] TX-FNCMTR-1 uses a dynamic or wrapper URL. Confirm the final endpoint contract manually.

## Signoff Guidance

- [ ] Lock PM signoff only after stage2 artifacts, Vue config, and this checklist are internally consistent.
- [ ] If a checklist item fails because the analysis looks wrong, update review.json and rerun the relevant stage.