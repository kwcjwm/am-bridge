# 2단계 Sub-Agent Usage Guide

## 기본 원칙

이 문서는 2단계 구현 workflow의 각 step에서 사용할 역할 하네스를 정의한다.

실제 runtime에 sub-agent 기능이 있으면 병렬 가능한 역할만 분리 실행한다.

single-model runtime이면 같은 역할 문서를 순서대로 읽고, 해당 역할 관점으로 집중 수행한다.

CUBE 공통 컴포넌트, 메뉴/레이아웃, 스타일 반영 규칙은 별도 reference 문서로 늘리지 않고 각 구현 역할 문서에 둔다.

QA 체크리스트는 구현 역할 문서가 아니라 `visual-alignment-reviewer`와 `implementation-reviewer`가 소유한다.

## Step별 역할 매핑

| Workflow Step | 사용 역할 |
| --- | --- |
| Step 0. 2단계 착수 게이트 | `implementation-readiness-reviewer` |
| Step 1. 분석 산출물 통합 인덱스 | `analysis-artifact-integrator`, `phase2-artifact-producer` |
| Step 2. CUBE 플랫폼 참조 잠금 | `cube-platform-adapter` |
| Step 2.1. CUBE 공통 컴포넌트 구현 반영 | `cube-component-implementer`, `cube-platform-adapter` |
| Step 2.2. CUBE 메뉴/배치 레이아웃 구현 반영 | `menu-layout-implementer`, `cube-platform-adapter` |
| Step 2.3. CUBE 컴포넌트 스타일 구현 반영 | `component-style-implementer`, `visual-alignment-reviewer` |
| Step 3. MiPlatform FE/BE R&R 재정의 | `frontend-legacy-analyzer`, `backend-legacy-analyzer`, `rnr-architect`, `phase2-artifact-producer` |
| Step 4. API와 Controller 계약 설계 | `backend-api-architect`, `frontend-api-consumer`, `test-strategy-planner`, `phase2-artifact-producer` |
| Step 5. 테스트 전략 잠금 | `test-strategy-planner` |
| Step 6. Vue Shell 강화 계획 | `frontend-implementation-architect`, `cube-platform-adapter`, `i18n-implementer`, `phase2-artifact-producer` |
| Step 7. 구현 Slice 계획 | `implementation-planner` |
| Step 8. Backend 구현 | `backend-implementer`, `backend-contract-reviewer` |
| Step 9. Frontend 구현 | `frontend-implementer`, `i18n-implementer` |
| Step 10. 단위 테스트 작성과 실행 | `unit-test-writer` |
| Step 11. API 셀프 테스트 | `api-self-test-runner` |
| Step 12. FE/BE 셀프 피드백 루프 | `fe-be-feedback-loop-coordinator`, `integration-reviewer` |
| Step 13. 스크린샷 기준 UI 정렬 점검 | `visual-alignment-reviewer` |
| Step 14. 2단계 Self-QA | `implementation-reviewer` |
| Step 15. 3단계 검증 인계 | `implementation-reviewer`, `phase2-artifact-producer` |

## 역할별 책임

### analysis-artifact-integrator

- 보고서, CSV, shell, 스크린샷, 소스, QA 결과를 구현 입력으로 연결한다.
- 구현자가 어떤 산출물을 어디에 써야 하는지 인덱스를 만든다.
- 보고서와 CSV가 코드 구현에서 누락되지 않도록 추적한다.

### implementation-readiness-reviewer

- 2단계 착수 가능 여부를 판단한다.
- blocking gap과 non-blocking gap을 분리한다.

### cube-platform-adapter

- CUBE 공통 컴포넌트/스타일/API/i18n 사용 지점을 매핑한다.
- 로컬 중복 구현을 막는다.

### cube-component-implementer

- Phase 1 shell placeholder를 CUBE component로 치환하는 구체 구현 방식을 정한다.
- props, events, slots, v-model, validation, i18n 연결을 실제 Vue 코드에 반영한다.
- CUBE component가 요구하는 data shape와 API response 간 mapper 필요 여부를 판단한다.

### menu-layout-implementer

- CUBE menu, route, page frame, breadcrumb, action area, permission hook을 실제 page에 연결한다.
- 화면 배치 구조를 CUBE layout 기준으로 구현한다.
- 버튼 visible/enabled 상태를 권한, loading, edit mode, row selection과 연결한다.

### component-style-implementer

- CUBE style token, component variant, density, spacing, typography를 실제 Vue template/style에 반영한다.
- local CSS가 필요한 경우 범위와 이유를 제한한다.
- 다국어 적용 후 overflow와 화면 깨짐을 점검한다.

### frontend-legacy-analyzer

- MiPlatform F/E source에서 dataset, event, transaction, validation, popup, message를 분석한다.
- Vue로 옮기면 안 되는 FE-heavy 업무 책임을 표시한다.

### backend-legacy-analyzer

- 기존 controller/service/mapper/query 후보를 추적한다.
- transaction과 backend 후보 간 연결을 찾는다.

### rnr-architect

- 최종 R&R matrix를 확정한다.
- CUBE, Vue, Spring Controller, Service, Mapper 책임을 나눈다.

### backend-api-architect

- Vue가 호출할 Spring Boot API/controller 계약을 설계한다.
- request/response DTO와 service/mapper 연결을 정의한다.

### frontend-api-consumer

- API 계약이 Vue state와 화면 binding에 맞는지 검토한다.
- payload/response mismatch를 조기에 찾는다.

### test-strategy-planner

- 단위 테스트, API 셀프 테스트, FE/BE 루프의 최소 범위를 정한다.
- API contract마다 테스트 시나리오를 붙인다.

### frontend-implementation-architect

- Phase 1 Vue shell을 구현 가능한 Vue 구조로 재설계한다.
- CUBE component mapping, state/event map, i18n key plan을 만든다.

### implementation-planner

- 구현 slice 순서를 정한다.
- FE/BE 작업 순서와 테스트 순서를 맞춘다.

### frontend-implementer

- CUBE 기반 Vue 구현을 담당한다.
- page state, API 호출, event handler, UI validation, i18n 적용을 수행한다.

### backend-implementer

- Spring Boot controller/service/DTO/mapper 구현을 담당한다.
- authoritative validation과 common error response를 반영한다.

### backend-contract-reviewer

- backend 구현이 API contract와 맞는지 검토한다.
- controller/service/DTO drift를 찾는다.

### unit-test-writer

- FE/BE 단위 테스트 또는 최소 빌드/타입/컴파일 검증을 수행한다.
- 테스트 환경이 없으면 대체 셀프 체크를 명시한다.

### api-self-test-runner

- API를 단독으로 호출해 happy path, empty, validation fail, error response를 확인한다.
- request/response sample과 실제 결과를 기록한다.

### fe-be-feedback-loop-coordinator

- FE payload와 BE DTO/response 사이 mismatch를 추적한다.
- 수정 후 재실행 루프를 관리한다.

### integration-reviewer

- FE/BE 계약 정합성과 CUBE wrapper 사용 결과를 검토한다.

### visual-alignment-reviewer

- 스크린샷, Phase 1 shell, 구현 Vue 화면 사이 시각적 정렬을 점검한다.

### implementation-reviewer

- 2단계 self-QA와 3단계 인계 품질을 검토한다.

### phase2-artifact-producer

- CSV, 표, checklist, handoff 문서 등 구조화 산출물을 만든다.
- 판단을 새로 하지 않고 확정된 분석/설계 결과를 표준 형태로 정리한다.

## 병렬 실행 가능 항목

다음은 병렬 실행해도 된다.

- `frontend-legacy-analyzer`와 `backend-legacy-analyzer`
- `cube-platform-adapter`와 `analysis-artifact-integrator`
- `i18n-implementer`의 key 후보 정리와 `frontend-implementation-architect`의 component mapping 초안
- 테스트 전략 초안 작성과 API contract review

## 병렬 실행 금지 항목

다음은 순서를 지켜야 한다.

- R&R matrix 확정 전 API contract 최종화 금지
- API contract 확정 전 deep Vue API wiring 금지
- backend DTO shape 확정 전 FE/BE 루프 결과 확정 금지
- reviewer가 지적한 같은 파일 범위를 implementer가 동시에 수정 금지

## 산출물 소유권

- R&R 최종 판단: `rnr-architect`
- CUBE 공통 컴포넌트 반영: `cube-component-implementer`
- CUBE 메뉴/레이아웃 반영: `menu-layout-implementer`
- CUBE 스타일 반영: `component-style-implementer`
- API/controller 계약: `backend-api-architect`
- Vue shell 강화 계획: `frontend-implementation-architect`
- 단위 테스트 결과: `unit-test-writer`
- API 셀프 테스트 결과: `api-self-test-runner`
- FE/BE 피드백 루프 결과: `fe-be-feedback-loop-coordinator`
- 최종 self-QA: `implementation-reviewer`
