# 페이지 전환 명세

## 기본 정보

- 페이지 ID: ValidationHeavyForm
- 페이지명: 검증 집중 화면
- 페이지 유형: main
- 레거시 원본 파일: tests\fixtures\validation_heavy_page.xml
- 업무 도메인: production-execution
- 주요 유스케이스: register

## 공통 플랫폼 연계

- 메뉴 키: 플랫폼 확인 필요
- 권한 키: 플랫폼 확인 필요
- 인증 연계: 확인 필요
- 결재: 없음
- 메일: 없음
- 공통 기능 사용: 없음
- 컴포넌트별 의존성: 없음

## 레거시 분석 요약

- 주요 dataset: ds_result
- 주요 transaction: TX-FNSAVE-1(/api/lot/save)
- 주요 함수: form_OnLoadCompleted, EditLotId_OnChanged, fnToggleDetail, fnSave, fnCallback
- 팝업 / 서브화면: 없음
- 연계 controller / service / SQL: 후속 backend trace 설계 필요

## Vue 페이지 설계 초안

- Vue 페이지명: ValidationHeavyFormPage
- 라우트: /validation-heavy-form
- 상태 관리 방식: 페이지 로컬 reactive state
- 주요 컴포넌트: StaticLotId, EditLotId, StaticQty, EditQty, EditRemark, StaticStatus, DivDetail, ButtonSave
- 입력 / 조회 / 저장 흐름: 초기 로드: form_OnLoadCompleted / 사용자 액션: EditLotId_OnChanged, fnSave / 주요 호출 1건

## UI 규칙 요약

- 스타일: 총 13건 / 대표 토큰: font-malgun-gothic-9-bold, input-required, text-222222, align-right, bg-007acc 외 6건
- 상태 규칙: 총 3건 / 대상: ButtonSave.Enable, DivDetail.Visible
- 검증 규칙: 총 3건 / 유형: length, number, required
- 메시지: 총 9건 / 유형: action-label, alert, confirm, label, status-text

## API 전략

- 기존 API 재사용: /api/lot/save
- 기존 API 보정: 응답/파라미터 구조 검토 필요
- 신규 API 필요: 기존 transaction만으로 부족한 경우에만 추가
- 공통 플랫폼 API 연계: 없음

## 검토 체크리스트

- 권한 맵핑 누락 여부: 권한 키 확인 필요
- 결재 연계 필요 여부: 없음
- 공통 기능 중복 구현 여부: 추가 확인 필요
- 팝업/서브화면 누락 여부: 팝업/서브화면 없음 또는 확인 필요
- UI 규칙 누락 여부: UI 규칙 요약 존재