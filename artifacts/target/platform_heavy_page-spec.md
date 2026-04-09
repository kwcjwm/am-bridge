# 페이지 전환 명세

## 기본 정보

- 페이지 ID: PlatformHeavyForm
- 페이지명: 플랫폼 연계 집중 화면
- 페이지 유형: main
- 레거시 원본 파일: tests\fixtures\platform_heavy_page.xml
- 업무 도메인: unknown
- 주요 유스케이스: 미정

## 공통 플랫폼 연계

- 메뉴 키: MENU:PlatformHeavyForm
- 권한 키: PAGE:PlatformHeavyForm
- 인증 연계: 공통 플랫폼 사용
- 결재: 필요
- 메일: 필요
- 공통 기능 사용: approval, auth, mail, permission
- 컴포넌트별 의존성: ButtonApproval[approval], ButtonAuth[auth], ButtonMail[mail], ButtonPermission[permission]

## 레거시 분석 요약

- 주요 dataset: 없음
- 주요 transaction: 없음
- 주요 함수: form_OnLoadCompleted, fnOpenApproval, fnSendMail, fnCheckPermission, fnAuthCheck
- 팝업 / 서브화면: 없음
- 연계 controller / service / SQL: 후속 backend trace 설계 필요

## Vue 페이지 설계 초안

- Vue 페이지명: PlatformHeavyFormPage
- 라우트: /platform-heavy-form
- 상태 관리 방식: 페이지 로컬 reactive state
- 주요 컴포넌트: ButtonApproval, ButtonMail, ButtonPermission, ButtonAuth
- 입력 / 조회 / 저장 흐름: 초기 로드: form_OnLoadCompleted / 사용자 액션: fnOpenApproval, fnSendMail, fnCheckPermission, fnAuthCheck

## UI 규칙 요약

- 스타일: 총 0건 / 대표 토큰: 없음
- 상태 규칙: 총 0건 / 대상: 없음
- 검증 규칙: 총 0건 / 유형: 없음
- 메시지: 총 4건 / 유형: action-label

## API 전략

- 기존 API 재사용: 없음
- 기존 API 보정: 없음
- 신규 API 필요: 확인 필요
- 공통 플랫폼 API 연계: 없음

## 검토 체크리스트

- 권한 맵핑 누락 여부: 권한 키 정보 존재
- 결재 연계 필요 여부: 필요
- 공통 기능 중복 구현 여부: 공통 기능 재사용 우선
- 팝업/서브화면 누락 여부: 팝업/서브화면 없음 또는 확인 필요
- UI 규칙 누락 여부: UI 규칙 요약 존재