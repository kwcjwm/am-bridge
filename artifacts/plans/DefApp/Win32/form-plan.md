# Stage 2 - Conversion Plan

- packageId: form-package
- pageId: form
- route: /form
- vuePageName: FormPage
- interactionPattern: grid-page

## Frontend Files

- frontend/src/pages/form/FormPage.vue: Vue 3 page shell that preserves the legacy interaction flow and platform boundaries.
- frontend/src/composables/useFormPage.ts: Local state, initial load, primary action handlers, and realtime cleanup.
- frontend/src/api/form.ts: Typed API client for the primary page use case and platform-aware headers.

## Backend Files

- backend/src/main/java/com/example/am/form/web/FormPageController.java: Spring Boot controller that replaces MiPlatform endpoint contracts with REST-style endpoints.
- backend/src/main/java/com/example/am/form/service/FormPageService.java: Application service boundary for page use cases.
- backend/src/main/java/com/example/am/form/service/impl/FormPageServiceImpl.java: Service implementation that adapts legacy DAO/query semantics into Spring Boot service logic.
- backend/src/main/java/com/example/am/form/dto/FormPageSearchCondition.java: Request DTO inferred from the search-form dataset.
- backend/src/main/java/com/example/am/form/dto/FormPageRow.java: Response DTO inferred from the primary result dataset.
- backend/src/main/resources/mapper/FormPageMapper.xml: Optional MyBatis mapper/XML placeholder when the legacy SQL must be preserved first.

## Execution Steps

- Stage 1: run package analysis and write review overrides if the primary dataset or backend trace is wrong.
- Stage 2: lock the primary dataset, primary transaction, platform boundaries, and file blueprint ownership.
- Stage 3: generate starter files and let AI Pro fill business logic using the starter bundle plus review overrides.
- Verification: compare the generated page flow against the original datasets, transactions, and popup/subview flows.

## Verification Checks

- Primary dataset matches the dominant result grid or primary business response.
- Search/code/view-state datasets are not treated as equal peers to the primary result dataset.
- Each primary transaction has a resolved or manually corrected backend route chain.
- No shared platform function is reimplemented locally without explicit approval.

## AI Prompts

### review

```text
Review page form. Confirm whether primaryDatasetId=ds_scorechk really represents the dominant business result. Distinguish result/search/code/view-state datasets, correct backend traces if needed, and write corrections into the review JSON before stage 2.
```

### frontend

```text
Using the stage 1 package and stage 2 plan for form, implement the frontend files (frontend/src/pages/form/FormPage.vue, frontend/src/composables/useFormPage.ts, frontend/src/api/form.ts). Preserve the interaction pattern grid-page, treat ds_scorechk as the main business result, and keep platform features out of local reimplementation.
```

### backend

```text
Using the stage 1 package and stage 2 plan for form, implement the backend files (backend/src/main/java/com/example/am/form/web/FormPageController.java, backend/src/main/java/com/example/am/form/service/FormPageService.java, backend/src/main/java/com/example/am/form/service/impl/FormPageServiceImpl.java, backend/src/main/java/com/example/am/form/dto/FormPageSearchCondition.java, backend/src/main/java/com/example/am/form/dto/FormPageRow.java, backend/src/main/resources/mapper/FormPageMapper.xml). Map the legacy route http://127.0.0.1:8080/miplatform/testScoreChk.do through EgovSampleController.selectScoreList. Preserve business behavior, but expose cleaner Spring Boot request/response DTOs.
```

## Package Hints

- Treat ds_scorechk as the primary business dataset unless review overrides say otherwise.
- Primary dataset reasons: largest-grid:Grid0, transaction-output:TX-BUTTON0ONCLICK-1, wide-schema:5, default-records:1
- Resolved backend chain begins at EgovSampleController.selectScoreList.