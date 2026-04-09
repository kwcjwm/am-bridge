# 페이지 전환 명세

## 기본 정보

- 페이지 ID: form
- 페이지명: New Form
- 페이지 유형: main
- 레거시 원본 파일: samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\form.xml
- 업무 도메인: unknown
- 주요 유스케이스: review, search

## 공통 플랫폼 연계

- 메뉴 키: 플랫폼 확인 필요
- 권한 키: 플랫폼 확인 필요
- 인증 연계: 확인 필요
- 결재: 없음
- 메일: 없음
- 공통 기능 사용: 없음
- 컴포넌트별 의존성: 없음

## 레거시 분석 요약

- 주요 dataset: ds_scorechk, ds_testCategory, ds_screen
- 주요 transaction: TX-TESTNAMESELECT-1(http://127.0.0.1:8080/miplatform/testNameList.do), TX-FNCMTR-1("svc::" + strController), TX-BUTTON0ONCLICK-1(http://127.0.0.1:8080/miplatform/testScoreChk.do)
- 주요 함수: fnSetVoInfo, testNameSelect, fnCmTr, Button0_OnClick, form_OnLoadCompleted, Button1_OnClick, Button2_OnClick
- 팝업 / 서브화면: subview:scurl, popup:DefApp::scholarship.xml
- 연계 controller / service / SQL: 후속 backend trace 설계 필요

## Vue 페이지 설계 초안

- Vue 페이지명: FormPage
- 라우트: /form
- 상태 관리 방식: 페이지 로컬 reactive state
- 주요 컴포넌트: Grid0, Static5, Button0, Combo0, Static4, Button1, Div0, Button2
- 입력 / 조회 / 저장 흐름: 초기 로드: form_OnLoadCompleted / 사용자 액션: Button0_OnClick, Button1_OnClick, Button2_OnClick / 주요 호출 3건

## UI 규칙 요약

- 스타일: 총 7건 / 대표 토큰: align-center, bg-aliceblue, bg-azure, border-none, font-tahoma-11 외 1건
- 상태 규칙: 총 3건 / 대상: Grid0.Enable, Grid0.TabStop, Grid0.Visible
- 검증 규칙: 총 1건 / 유형: custom
- 메시지: 총 7건 / 유형: action-label, alert, component-text, label

## API 전략

- 기존 API 재사용: http://127.0.0.1:8080/miplatform/testNameList.do, "svc::" + strController, http://127.0.0.1:8080/miplatform/testScoreChk.do
- 기존 API 보정: 응답/파라미터 구조 검토 필요
- 신규 API 필요: 기존 transaction만으로 부족한 경우에만 추가
- 공통 플랫폼 API 연계: 없음

## 검토 체크리스트

- 권한 맵핑 누락 여부: 권한 키 확인 필요
- 결재 연계 필요 여부: 없음
- 공통 기능 중복 구현 여부: 추가 확인 필요
- 팝업/서브화면 누락 여부: navigation 포함
- UI 규칙 누락 여부: UI 규칙 요약 존재