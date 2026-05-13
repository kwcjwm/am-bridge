# 2단계 구현 WORKFLOW

## 목표

2단계는 1단계 분석/설계와 1.5단계 QA가 승인된 뒤, 간이 Vue shell을 `CUBE 공통 플랫폼 + Vue3 + Spring Boot` 기준의 구현 산출물로 강화하는 단계다.

이 단계는 단순히 화면을 예쁘게 고치는 단계가 아니다.

핵심은 다음 네 가지다.

1. 1단계 보고서/CSV/스크린샷/소스를 구현 입력으로 통합한다.
2. MiPlatform F/E에 몰려 있던 책임을 Vue, CUBE, Spring Controller, Service, Mapper로 다시 나눈다.
3. Vue가 호출할 API/controller 계약을 설계하고 구현한다.
4. 단위 테스트, 간단 API 셀프 테스트, FE/BE 피드백 루프까지 2단계 안에서 돌린다.

## 기본 원칙

### 1. 1단계 Vue shell은 최종 코드가 아니다

1단계 Vue shell은 화면 구조와 의사소통을 위한 껍데기다.

2단계에서는 이 shell을 다음 근거로 강화한다.

- 1단계 메인 보고서
- 1단계 상세 CSV 산출물
- 1.5단계 QA 결과
- 레거시 MiPlatform F/E 소스
- 관련 B/E 소스
- 스크린샷
- CUBE 컴포넌트/스타일/API/i18n 참조

### 2. CUBE가 있으면 CUBE를 쓴다

메뉴, 권한, 공통 레이아웃, 공통 버튼, 그리드, 팝업, 메시지, 공통 코드, API wrapper, 다국어, 스타일 토큰 등은 기본적으로 CUBE 책임으로 본다.

로컬 구현은 페이지 고유 업무 동작에 한정한다.

### 3. MiPlatform F/E 책임을 그대로 Vue로 옮기지 않는다

MiPlatform 화면에는 다음 책임이 F/E에 과도하게 들어 있는 경우가 많다.

- dataset orchestration
- transaction parameter assembly
- validation
- 버튼 활성/비활성 제어
- popup 처리
- message 처리
- common code 조회
- backend routing hint
- 비즈니스 분기

2단계에서는 이 책임을 아래로 재분배한다.

- CUBE 플랫폼
- Vue page
- Spring Controller/API
- Spring Service/domain
- Mapper/query
- PM/아키텍트 결정 필요 항목

### 4. 2단계에서 셀프 테스트까지 한다

3단계 검증은 별도지만, 2단계 구현자는 최소한 다음을 자체 수행해야 한다.

- FE 단위/컴포넌트 테스트 또는 최소 빌드/타입 검증
- BE 단위 테스트 또는 controller/service 단위 검증
- API 셀프 테스트
- FE payload와 BE DTO 간 계약 mismatch 확인
- i18n key resolve 확인
- CUBE 공통 기능 중복 구현 여부 확인

## Step 0. 2단계 착수 게이트

### 목적

2단계 구현을 시작할 수 있는 상태인지 확인한다.

### 입력

- 1단계 메인 보고서
- 1단계 CSV 산출물
- 1단계 Vue shell
- 1단계 test checklist
- 1.5단계 QA 결과
- 레거시 F/E 소스
- 관련 B/E 소스
- 스크린샷
- CUBE 참조 문서/소스

### 확인 항목

- 1.5단계 QA에 blocking 이슈가 없는가
- 화면 목적과 대표 업무 흐름이 명확한가
- 주요 dataset, transaction, event가 식별되어 있는가
- 주요 controller/service/mapper 후보가 식별되어 있는가
- 스크린샷과 shell의 기준 관계가 명확한가
- CUBE 공통 사용 전제가 정리되어 있는가
- 기존 테스트 실행 방식이 확인되어 있는가

### 산출물

- `phase2-intake-summary.md`
- `phase2-blockers.md`

### 사용 역할

- `implementation-readiness-reviewer`

## Step 1. 분석 산출물 통합 인덱스 작성

### 목적

보고서, CSV, shell, 스크린샷, 소스가 따로 놀지 않도록 구현용 입력 인덱스를 만든다.

### 작업

- 보고서 섹션별 구현 근거를 정리한다.
- CSV 파일별 사용 목적을 정리한다.
- 스크린샷 기준 영역과 Vue shell 영역을 매핑한다.
- 레거시 F/E 파일과 관련 이벤트/transaction을 매핑한다.
- 관련 B/E 파일과 controller/service/mapper 후보를 매핑한다.
- 1.5 QA 지적 사항을 구현 체크 항목으로 변환한다.

### CSV 활용 기준

CSV는 보조 산출물이 아니라 구현의 입력이다.

예:

- components CSV -> CUBE 컴포넌트 매핑
- datasets CSV -> Vue state, DTO, API response 설계
- transactions CSV -> API/controller 계약
- events CSV -> Vue event handler와 service 호출 흐름
- validations/messages CSV -> validation, i18n, error 처리
- backend candidates CSV -> controller/service/mapper 설계

### 산출물

- `phase2-evidence-index.md`
- `analysis-artifact-usage-map.csv`
- `qa-to-implementation-action-map.csv`

### 사용 역할

- `analysis-artifact-integrator`
- `phase2-artifact-producer`

## Step 2. CUBE 플랫폼 참조 잠금

### 목적

로컬 구현을 시작하기 전에 CUBE가 담당할 기능을 먼저 잠근다.

### 분석 대상

- CUBE layout/frame
- 메뉴/route 연계
- 권한/auth 처리
- 공통 grid/table
- 공통 form component
- 공통 button/action area
- popup/modal
- common code lookup
- API client wrapper
- error/message handler
- loading/empty/success state
- i18n utility
- design token/style convention

### 규칙

CUBE가 제공하는 것은 CUBE를 사용한다.

페이지 로컬 구현은 업무 화면 고유 로직에 한정한다.

### 산출물

- `cube-platform-usage-map.md`
- `cube-local-implementation-boundary.md`
- `cube-gap-list.md`

### 사용 역할

- `cube-platform-adapter`

## Step 2.1. CUBE 공통 컴포넌트 구현 반영 하네스

### 목적

CUBE 공통 컴포넌트를 "사용 예정"으로만 표시하지 않고, 실제 Vue 코드에 어떻게 반영할지 확정한다.

### 참조 문서

- `cube-component-implementation-harness.md`

### 작업

- components CSV와 Phase 1 Vue shell의 placeholder를 연결한다.
- 각 placeholder에 대응하는 CUBE component 후보를 찾는다.
- CUBE component의 props, events, slots, v-model 사용 방식을 확인한다.
- datasets CSV와 API response를 CUBE grid/form binding 구조에 맞춘다.
- validations/messages CSV를 CUBE validation/message/i18n 방식에 연결한다.
- CUBE에 없는 기능은 local 구현으로 바로 만들지 않고 platform gap으로 기록한다.

### 실제 코드 반영 기준

- template의 임시 div/table/input/button을 CUBE component로 치환한다.
- page state 이름과 shape를 CUBE component binding에 맞춘다.
- CUBE component가 요구하는 data shape와 API response가 다르면 page-local mapper를 둔다.
- 공통 동작은 CUBE component props 또는 composable로 연결하고, 내부 로직을 복제하지 않는다.
- hard-coded label/message는 i18n key로 교체한다.

### 산출물

- `cube-component-mapping.csv`
- `cube-component-implementation-notes.md`
- Vue component 반영 사항

### 사용 역할

- `cube-component-implementer`
- `cube-platform-adapter`

## Step 2.2. CUBE 메뉴/배치 레이아웃 구현 반영 하네스

### 목적

화면을 CUBE 메뉴, route, page frame, action area, permission 구조에 실제로 연결한다.

### 참조 문서

- `cube-menu-layout-implementation-harness.md`

### 작업

- menu key, permission key, route path, route name, page title i18n key를 정한다.
- CUBE page frame 안에 화면을 배치한다.
- search/filter, main grid/list, detail/form, action area의 배치 구조를 정한다.
- 조회/저장/삭제/닫기 등 action을 CUBE action area에 배치한다.
- 권한, loading, edit mode, row selection에 따른 button visible/enabled 상태를 연결한다.

### 실제 코드 반영 기준

- route/menu 등록은 대상 프로젝트의 기존 CUBE 방식으로 추가한다.
- page title, breadcrumb, permission hook은 CUBE frame에서 제공하는 방식을 사용한다.
- 버튼 영역은 로컬 floating button이 아니라 CUBE action area에 연결한다.
- 스크린샷과 다르더라도 CUBE 표준 layout이 있으면 CUBE를 우선한다. 단, 업무상 핵심 영역의 우선순위는 유지한다.

### 산출물

- `cube-menu-route-map.md`
- `action-permission-state-map.csv`
- `layout-implementation-notes.md`
- route/page/layout 코드 반영 사항

### 사용 역할

- `menu-layout-implementer`
- `cube-platform-adapter`

## Step 2.3. CUBE 컴포넌트 스타일 구현 반영 하네스

### 목적

CUBE style guide, design token, component variant를 실제 Vue 구현에 반영한다.

### 참조 문서

- `cube-style-implementation-harness.md`

### 작업

- 기존 CUBE 화면 중 유사 레이아웃을 찾는다.
- search area, grid/list, detail/form, action area별 style/token을 매핑한다.
- CUBE component variant와 density 기준을 정한다.
- 다국어 적용 후 label/button/grid header overflow 가능성을 확인한다.
- page-local CSS가 필요한 경우 이유와 범위를 기록한다.

### 실제 코드 반영 기준

- 색상, 간격, typography는 CUBE token/class/component variant를 우선 사용한다.
- page-local style은 scoped 범위로 제한한다.
- CUBE component 내부 selector override는 금지한다.
- screenshot pixel fit을 위해 임의 margin을 누적하지 않는다.
- grid height, form column, action area spacing은 responsive constraint로 잡는다.

### 산출물

- `cube-style-reference-map.md`
- `style-token-mapping.csv`
- `style-implementation-notes.md`
- style 코드 반영 사항

### 사용 역할

- `component-style-implementer`
- `visual-alignment-reviewer`

## Step 3. MiPlatform F/E와 B/E R&R 재정의

### 목적

MiPlatform 시대의 F/E-heavy 구조를 target 구조에 맞게 다시 나눈다.

### 분류 값

각 동작과 데이터 책임은 아래 중 하나로 분류한다.

- `CUBE_PLATFORM`
- `VUE_PAGE`
- `SPRING_CONTROLLER`
- `SPRING_SERVICE`
- `QUERY_MAPPER`
- `COMMON_API`
- `DEPRECATED`
- `UNRESOLVED`

### 기본 분배 기준

| MiPlatform 항목 | Target 책임 |
| --- | --- |
| 메뉴, 권한, 공통 frame | CUBE_PLATFORM |
| 공통 popup/message | CUBE_PLATFORM |
| 공통 코드 조회 | CUBE_PLATFORM 또는 COMMON_API |
| dataset field binding | VUE_PAGE |
| transaction 호출 시점 | VUE_PAGE |
| transaction URL/API 경계 | SPRING_CONTROLLER |
| UI 검색 조건 조립 | VUE_PAGE |
| 업무 기본값/권위 있는 파라미터 보정 | SPRING_SERVICE |
| 즉시 UI validation | VUE_PAGE |
| 저장 전 최종 validation | SPRING_SERVICE |
| SQL 분기/조회/저장 | SPRING_SERVICE + QUERY_MAPPER |
| grid style/layout | CUBE_PLATFORM + VUE_PAGE |
| 다국어 text | CUBE i18n |

### 산출물

- `rnr-matrix.md`
- `legacy-to-target-responsibility.csv`
- `unresolved-rnr-decisions.md`

### 사용 역할

- `frontend-legacy-analyzer`
- `backend-legacy-analyzer`
- `rnr-architect`
- `phase2-artifact-producer`

## Step 4. API와 Controller 계약 설계

### 목적

Vue가 호출할 Spring Boot API 구조를 먼저 잠근다.

### 입력

- 보고서의 transaction/API 분석
- transactions CSV
- datasets CSV
- backend candidates CSV
- R&R matrix
- CUBE API convention
- 기존 Spring Boot 프로젝트 구조

### API별 설계 항목

- endpoint path
- HTTP method
- request DTO
- response DTO
- paging/sorting/filtering rule
- error response rule
- permission requirement
- controller method
- service method
- mapper/query candidate
- legacy transaction ID
- Vue caller
- 단위/API 테스트 시나리오

### 설계 규칙

MiPlatform transaction 이름을 그대로 REST API 이름으로 옮기지 않는다.

target 프로젝트의 Spring Boot/CUBE naming convention에 맞추되, legacy transaction ID는 추적 가능하게 남긴다.

### 산출물

- `api-contract.md`
- `api-contract.csv`
- `dto-mapping.md`
- `controller-service-mapper-map.md`
- `api-test-scenario.md`

### 사용 역할

- `backend-api-architect`
- `frontend-api-consumer`
- `test-strategy-planner`
- `phase2-artifact-producer`

## Step 5. 테스트 전략 잠금

### 목적

구현 전에 2단계 셀프 검증 범위를 정한다.

### 테스트 범위

#### FE

- Vue component render 가능 여부
- 주요 event handler 동작
- validation 동작
- API client 호출 payload shape
- i18n key 사용 여부
- shell placeholder 제거 여부

#### BE

- controller request/response binding
- service 단위 validation/business rule
- mapper/query 호출 경계
- error response format
- DTO field mapping

#### API 셀프 테스트

- 대표 조회 API happy path
- 빈 결과
- validation fail
- 저장/수정/삭제가 있으면 최소 성공/실패 케이스
- 권한/공통 header가 필요하면 header 누락 또는 mock 조건

### 산출물

- `phase2-test-strategy.md`
- `unit-test-targets.md`
- `api-self-test-plan.md`

### 사용 역할

- `test-strategy-planner`

## Step 6. Vue Shell 강화 계획

### 목적

1단계 shell을 실제 Vue 구현 계획으로 변환한다.

### 작업

- shell 영역을 CUBE layout/component에 매핑한다.
- `cube-component-mapping.csv`를 기준으로 placeholder 치환 순서를 정한다.
- `cube-menu-route-map.md`를 기준으로 route/menu/page frame 반영 위치를 정한다.
- `style-token-mapping.csv`를 기준으로 CUBE style/token 적용 방식을 정한다.
- placeholder control을 CUBE component로 치환 계획한다.
- grid column, form field, button 영역을 CSV와 보고서 기준으로 재정의한다.
- screenshot 기준으로 시각적 우선순위를 확인한다.
- Vue state 구조를 정의한다.
- API client 호출 위치와 payload를 정의한다.
- loading/empty/error/success 상태를 정의한다.
- i18n key를 정의한다.
- unresolved behavior는 코드로 추측하지 않고 명시한다.

### 산출물

- `vue-shell-hardening-plan.md`
- `component-mapping.csv`
- `state-and-event-map.md`
- `i18n-key-plan.csv`
- `screenshot-to-shell-alignment.md`

### 사용 역할

- `frontend-implementation-architect`
- `cube-platform-adapter`
- `i18n-implementer`
- `phase2-artifact-producer`

## Step 7. 구현 Slice 계획

### 목적

전체 화면을 무작위로 구현하지 않도록 세로 slice 단위로 구현 순서를 정한다.

### 권장 순서

1. CUBE page frame, route, menu 연결
2. 검색/필터 영역
3. 대표 조회 API와 main grid/list
4. row selection과 detail binding
5. 등록/수정/삭제/저장 흐름
6. validation과 message
7. popup/common code 연계
8. permission/button state
9. i18n replacement
10. screenshot 기준 visual alignment
11. 테스트와 FE/BE 피드백 루프

### 산출물

- `implementation-slice-plan.md`
- `slice-test-map.md`

### 사용 역할

- `implementation-planner`

## Step 8. Backend 구현

### 목적

Vue가 호출할 Spring Boot API를 구현하거나 기존 구조에 맞게 연결한다.

### 작업

- controller method 작성 또는 수정
- request/response DTO 작성 또는 수정
- service method 연결
- mapper/query 연결
- authoritative validation 구현
- CUBE/common error response pattern 적용
- legacy transaction/controller/service/mapper traceability 기록

### 산출물

- controller/service/DTO/mapper 변경
- `backend-implementation-notes.md`
- `legacy-api-traceability.md`

### 사용 역할

- `backend-implementer`
- `backend-contract-reviewer`

## Step 9. Frontend 구현

### 목적

CUBE 기반 Vue3 페이지를 구현한다.

### 작업

- CUBE layout/style 적용
- CUBE form/grid/button/popup/message component 사용
- CUBE menu/route/page frame/action area 연결
- CUBE style token, component variant, density 기준 반영
- page state 구성
- API client 호출 연결
- event handler 구현
- UI-level validation 구현
- i18n key 적용
- shell-only mock data 제거
- Vue에 남기면 안 되는 비즈니스 책임 제거

### 산출물

- Vue page/component 변경
- API client 변경
- i18n locale 변경
- `frontend-implementation-notes.md`

### 사용 역할

- `frontend-implementer`
- `i18n-implementer`

## Step 10. 단위 테스트 작성과 실행

### 목적

2단계 구현자가 스스로 최소 단위 검증을 수행한다.

### FE 테스트

프로젝트에 테스트 환경이 있으면 기존 방식에 맞춰 작성한다.

예:

- component render test
- event handler test
- validation function test
- API client payload mapping test
- i18n key presence test

테스트 환경이 없으면 최소한 다음을 수행하고 기록한다.

- type check
- lint
- build
- 주요 handler 수동 점검 결과

### BE 테스트

프로젝트에 테스트 환경이 있으면 기존 방식에 맞춰 작성한다.

예:

- controller binding test
- service validation test
- DTO mapping test
- error response test

테스트 환경이 없으면 최소한 다음을 수행하고 기록한다.

- compile
- targeted test command
- API self-test로 controller binding 확인

### 산출물

- 테스트 코드 변경
- `unit-test-result.md`
- 실패/보류 테스트 목록

### 사용 역할

- `unit-test-writer`

## Step 11. API 셀프 테스트

### 목적

FE/BE 통합 검증 전에 API가 단독으로 최소 동작하는지 확인한다.

### 테스트 방식

프로젝트 상황에 맞게 아래 중 가능한 방식을 사용한다.

- existing API test framework
- Spring Boot test
- HTTP client file
- curl script
- Postman collection
- local mock/stub

### API별 최소 케이스

- happy path
- empty result
- validation fail
- error response format
- permission/header 조건
- 저장성 API가 있으면 success/fail 최소 케이스

### 결과 기록

각 API마다 다음을 기록한다.

- endpoint
- request sample
- expected response
- actual response
- pass/fail
- mismatch owner
- 재실행 여부

### 산출물

- `api-self-test-result.md`
- request/response sample
- API mismatch list

### 사용 역할

- `api-self-test-runner`

## Step 12. FE/BE 셀프 피드백 루프

### 목적

Vue 구현과 Spring Boot 구현 사이의 payload/DTO/상태 mismatch를 2단계 안에서 줄인다.

### 루프 단위

아래 단위로 반복한다.

1. API contract 확인
2. FE payload 생성 확인
3. BE request DTO binding 확인
4. BE response DTO 확인
5. FE grid/detail binding 확인
6. error/loading/empty/success 상태 확인
7. mismatch owner 결정
8. 수정 후 재실행

### 반복 제한

기본 2회 반복한다.

2회 이후에도 남는 문제는 `phase2-open-issues.md`에 기록하고 Phase 3 또는 PM/아키텍트 결정으로 넘긴다.

### mismatch 분류

- `FE_PAYLOAD`
- `BE_DTO`
- `API_CONTRACT`
- `SERVICE_RULE`
- `QUERY_RESULT`
- `CUBE_WRAPPER`
- `I18N`
- `UNRESOLVED`

### 산출물

- `fe-be-feedback-loop.md`
- `contract-mismatch-log.csv`
- `phase2-open-issues.md`

### 사용 역할

- `fe-be-feedback-loop-coordinator`
- `integration-reviewer`

## Step 13. 스크린샷 기준 UI 정렬 점검

### 목적

구현된 Vue 화면이 1단계 shell과 원본 스크린샷의 의도를 유지하는지 확인한다.

### 확인 항목

- 주요 영역 배치
- grid/form/button 우선순위
- CUBE style 적용 여부
- 텍스트 overflow
- 버튼/필드 비활성 상태
- popup 진입점
- loading/empty/error 표시
- 다국어 적용 후 레이아웃 깨짐 여부

### 산출물

- `visual-alignment-check.md`
- screenshot diff 또는 수동 점검 결과

### 사용 역할

- `visual-alignment-reviewer`

## Step 14. 2단계 Self-QA

### 목적

3단계 검증으로 넘기기 전에 2단계 산출물이 최소 품질을 만족하는지 자체 점검한다.

### 확인 항목

- 1단계 보고서 요구사항이 구현에 반영되었는가
- 1.5 QA 지적 사항이 해결 또는 보류 처리되었는가
- CSV 산출물이 구현 입력으로 사용되었는가
- CUBE 공통 기능을 중복 구현하지 않았는가
- R&R matrix가 코드와 일치하는가
- API contract가 FE/BE 코드와 일치하는가
- 단위 테스트 결과가 기록되었는가
- API 셀프 테스트 결과가 기록되었는가
- FE/BE 피드백 루프 결과가 기록되었는가
- i18n hard-coded text가 남아 있지 않은가
- Phase 3에서 검증할 항목이 명확한가

### 산출물

- `phase2-self-qa.md`
- 갱신된 `test-checklist.md`
- `phase3-handoff-notes.md`

### 사용 역할

- `implementation-reviewer`

## Step 15. 3단계 검증 인계

### 목적

3단계 검증자가 다시 분석을 시작하지 않도록 구현 결과와 검증 포인트를 전달한다.

### 인계 항목

- 변경 파일 목록
- 구현 요약
- CUBE 사용 요약
- R&R matrix
- API contract
- 테스트 명령과 결과
- API 셀프 테스트 결과
- FE/BE 피드백 루프 결과
- 미해결 이슈
- Phase 3 우선 검증 항목

### 산출물

- `phase3-handoff-notes.md`
