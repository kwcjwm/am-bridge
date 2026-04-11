# Stage 2 - Conversion Plan

## Contents

- [Target Architecture Summary](#target-architecture-summary)
- [Locked Assumptions](#locked-assumptions)
- [Implementation Scope](#implementation-scope)
- [File Blueprint Summary](#file-blueprint-summary)
- [Execution Sequence](#execution-sequence)
- [Verification Strategy](#verification-strategy)
- [Manual Decisions Pending (2)](#manual-decisions-pending-2)
- [Related Screens (2)](#related-screens-2)
- [Evidence Registry Links](#evidence-registry-links)

## Target Architecture Summary

- Package: `form-package`
- Target route: `/form`
- Vue page name: `FormPage`
- Interaction pattern: `grid-page`
- Frontend files: `3` / backend files: `7`

## Locked Assumptions

- Primary dataset remains `ds_scorechk` unless review overrides change it.
- Primary transactions locked for this page: `TX-BUTTON0ONCLICK-1`.
- Popup/subview targets stay separated from the current page implementation.
- Shared platform behaviors are not reimplemented locally without explicit approval.

## Implementation Scope

| Layer | Count | Representative Files |
| --- | --- | --- |
| Frontend | 3 | frontend/src/pages/form/FormPage.vue, frontend/src/composables/useFormPage.ts, frontend/src/api/form.ts |
| Backend | 7 | backend/src/main/java/com/example/am/form/web/FormPageController.java, backend/src/main/java/com/example/am/form/service/FormPageService.java, backend/src/main/java/com/example/am/form/service/impl/FormPageServiceImpl.java |

## File Blueprint Summary

| Path | Purpose | Summary |
| --- | --- | --- |
| frontend/src/pages/form/FormPage.vue | entry page | Vue 3 page shell that preserves the legacy interaction flow and platform boundaries. |
| frontend/src/composables/useFormPage.ts | page orchestration | Local state, initial load, primary action handlers, and realtime cleanup. |
| frontend/src/api/form.ts | api bridge | Typed API client for the primary page use case and platform-aware headers. |
| backend/src/main/java/com/example/am/form/web/FormPageController.java | spring controller | Spring Boot controller that replaces MiPlatform endpoint contracts with REST-style endpoints. |
| backend/src/main/java/com/example/am/form/service/FormPageService.java | service interface | Application service boundary for page use cases. |
| backend/src/main/java/com/example/am/form/service/impl/FormPageServiceImpl.java | service implementation | Service implementation that adapts legacy DAO/query semantics into Spring Boot service logic. |
| backend/src/main/java/com/example/am/form/dto/FormPageSearchCondition.java | request dto | Request DTO inferred from the search-form dataset. |
| backend/src/main/java/com/example/am/form/dto/FormPageRow.java | response dto | Response DTO inferred from the primary result dataset. |
| backend/src/main/java/com/example/am/form/mapper/FormPageMapper.java | mybatis mapper | Mapper interface for primary page queries and inferred lookup datasets. |
| backend/src/main/resources/mapper/FormPageMapper.xml | query placeholder | Optional MyBatis mapper/XML placeholder when the legacy SQL must be preserved first. |

## Execution Sequence

1. Stage 1: run package analysis and write review overrides if the primary dataset or backend trace is wrong.
1. Stage 2: lock the primary dataset, primary transaction, platform boundaries, and file blueprint ownership.
1. Stage 2 deliverable: emit a Vue page config JSON that downstream generation can consume directly.
1. Stage 2 deliverable: emit a PM-facing test checklist so the page can be validated before signoff.
1. Stage 3: generate starter files and let AI Pro fill business logic using the starter bundle plus review overrides.
1. Verification: compare the generated page flow against the original datasets, transactions, and popup/subview flows.

## Verification Strategy

- Primary dataset matches the dominant result grid or primary business response.
- Search/code/view-state datasets are not treated as equal peers to the primary result dataset.
- Each primary transaction has a resolved or manually corrected backend route chain.
- Popup/subview targets are treated as separate related screens, not merged silently into the current page.
- No shared platform function is reimplemented locally without explicit approval.

## Manual Decisions Pending (2)

- Related screen target scurl could not be resolved automatically. Confirm whether it should be treated as a separate page.
- TX-FNCMTR-1 uses a dynamic or wrapper URL. Confirm the final endpoint contract manually.

## Related Screens (2)

| Type | Target | Resolved Page | Status |
| --- | --- | --- | --- |
| subview | scurl | unresolved | unresolved |
| popup | DefApp::scholarship.xml | scholarship | resolved |

## Evidence Registry Links

- plan-json: [plan-json](form-plan.json)
- vue-config-json: [vue-config-json](form-vue-config.json)
- pm-checklist: [pm-checklist](form-pm-checklist.md)
- review-json: [review-json](../../../reviews/DefApp/Win32/form-review.json)
- page report hub: [page report hub](../../../reports/DefApp/Win32/form/README.md)
- stage2 report pack: [stage2 report pack](../../../reports/DefApp/Win32/form/stage2/README.md)
- Prompt pack: [../../../reports/DefApp/Win32/form/stage2/ai-prompts.md](../../../reports/DefApp/Win32/form/stage2/ai-prompts.md)
- Registry directory: [../../../reports/DefApp/Win32/form/stage2/registries](../../../reports/DefApp/Win32/form/stage2/registries)
- Registry: [file-blueprints.csv](../../../reports/DefApp/Win32/form/stage2/registries/file-blueprints.csv)
- Registry: [verification-checks.csv](../../../reports/DefApp/Win32/form/stage2/registries/verification-checks.csv)
- Registry: [related-screens.csv](../../../reports/DefApp/Win32/form/stage2/registries/related-screens.csv)
- Registry: [execution-steps.csv](../../../reports/DefApp/Win32/form/stage2/registries/execution-steps.csv)
