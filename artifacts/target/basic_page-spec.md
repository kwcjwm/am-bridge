# Page Conversion Spec

## 기본 정보

- 페이지 ID: MainForm
- 레거시 화면 파일: tests\fixtures\basic_page.xml
- 업무 도메인: resource-equipment
- 주요 use case: review, search

## 공통 플랫폼 연계

- 메뉴: MENU:MainForm
- 권한: 후보 필요
- 인증: 확인 필요
- 결재: 필요
- 메일: 없음
- 공통 레이아웃 / 공통 컴포넌트: approval

## 레거시 분석

- 주요 dataset: ds_search, ds_result, ds_code
- 주요 transaction: TX-FNLOADCODES-1(/api/common/codes), TX-FNSEARCH-1(/api/equipment/status)
- 연계 controller / service / SQL: 후속 backend trace 단계 필요
- 팝업 / 서브화면: popup:DefApp::approval.xml

## 타깃 페이지 설계

- Vue 페이지명: MainFormPage
- 라우트: /main-form
- 상태 관리 방식: 페이지 로컬 reactive state
- 주요 컴포넌트: ComboStatus, ButtonSearch, ButtonApproval, Grid0
- 입력 / 조회 / 저장 흐름: 초기 로드: form_OnLoadCompleted / 사용자 액션: ComboStatus_OnChanged, fnSearch, fnOpenApproval / 주요 호출 수: 2

## API 전략

- 기존 API 재사용: /api/common/codes, /api/equipment/status
- 기존 API 보정: 응답/파라미터 표준화 여부 검토
- 신규 API 필요: 기존 transaction으로 부족한 경우에만 추가
- 공통 플랫폼 API 연계: approval

## 검토 포인트

- 권한 매핑 누락 여부: 권한 키 후보 필요
- 결재 연계 필요 여부: 필요
- 공통 기능 중복 구현 여부: 공통 기능 호출만 유지
- 레거시 기능 누락 여부: navigation 포함
