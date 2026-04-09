# Detailed Legacy Analysis Report

## Page Identity

- pageId: form
- pageName: New Form
- pageType: main
- sourceFile: C:\workspace\am-bridge\samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\form.xml
- interactionPattern: grid-page

## Page Boundary

- primaryDatasetId: ds_scorechk
- mainGridComponentId: Grid0
- primaryTransactionIds: TX-BUTTON0ONCLICK-1

## Frontend Integrated Analysis

### Datasets

#### ds_scorechk
- role: response
- primaryUsage: main-grid
- boundComponents: Grid0
- columns: stuno, stuname, avgscore, rank, denseRank
- salienceScore: 171

#### ds_testCategory
- role: code
- primaryUsage: code-lookup
- boundComponents: Combo0
- columns: testCategory, testname
- salienceScore: 25

#### ds_screen
- role: view-state
- primaryUsage: view-state
- boundComponents: none
- columns: caption, id, level
- salienceScore: 0

### Components

#### Grid0
- componentType: Grid
- layoutGroup: data-panel
- events: none

#### Static5
- componentType: Static
- layoutGroup: content-panel
- events: none

#### Button0
- componentType: Button
- layoutGroup: search-panel
- events: OnClick

#### Combo0
- componentType: Combo
- layoutGroup: search-panel
- events: none

#### Static4
- componentType: Static
- layoutGroup: content-panel
- events: none

#### Button1
- componentType: Button
- layoutGroup: search-panel
- events: OnClick

#### Div0
- componentType: Div
- layoutGroup: container-panel
- events: none

#### Button2
- componentType: Button
- layoutGroup: search-panel
- events: OnClick

### User Actions

#### Button0_OnClick
- transactions: TX-BUTTON0ONCLICK-1
- controls: Combo0
- readsDatasets: none
- writesDatasets: none

#### form_OnLoadCompleted
- transactions: none
- controls: none
- readsDatasets: none
- writesDatasets: none

#### Button1_OnClick
- transactions: none
- controls: Div0
- readsDatasets: ds_screen
- writesDatasets: none

#### Button2_OnClick
- transactions: none
- controls: none
- readsDatasets: none
- writesDatasets: none

## Backend Integrated Analysis

### TX-TESTNAMESELECT-1
- legacyUrl: http://127.0.0.1:8080/miplatform/testNameList.do
- controller: EgovSampleController.selectTestList
- service: EgovSampleServiceImpl.testNameList
- dao: SampleDAO.testNameList
- sqlMapId: sampleDAO.testNameList
- tables: score_jew
- responseFields: testCategory, testname
- querySummary: SELECT distinct testCategory, testname FROM score_jew WHERE 1=1 ORDER BY testCategory ASC

### TX-BUTTON0ONCLICK-1
- legacyUrl: http://127.0.0.1:8080/miplatform/testScoreChk.do
- controller: EgovSampleController.selectScoreList
- service: EgovSampleServiceImpl.ScoreChk
- dao: SampleDAO.ScoreChk
- sqlMapId: sampleDAO.ScoreChk
- tables: score_jew, student_jew
- responseFields: avgscore, denseRank, rank, stuname, stuno
- querySummary: select A.stuno as stuno,B.STUNAME as stuname, To_char(round(avg(score),0)) as avgscore, To_char(Rank() over(order by avg(score) DESC)) as rank, To_char(DENSE_RANK() OVER(order by avg(score) DESC,(select score from sco...

## Related Screens

### scurl
- relation: subview
- triggerFunction: Button1_OnClick
- resolutionStatus: unresolved
- resolvedPath: unknown
- relatedPageId: unknown
- relatedPageName: unknown
- relatedPageType: unknown

### DefApp::scholarship.xml
- relation: popup
- triggerFunction: Button2_OnClick
- resolutionStatus: resolved
- resolvedPath: C:\workspace\am-bridge\samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\scholarship.xml
- relatedPageId: scholarship
- relatedPageName: New Form
- relatedPageType: main

## Handoff Notes

- Treat popup or subview targets as separate screens, not as inline sections of the current page.
- Use stage 2 Vue config JSON as the implementation contract for frontend generation.
- Keep ambiguous wrapper transactions in open questions until review.json resolves them.