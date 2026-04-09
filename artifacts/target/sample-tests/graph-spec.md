# 페이지 전환 명세

## 기본 정보

- 페이지 ID: graph
- 페이지명: Base::graph
- 페이지 유형: main
- 레거시 원본 파일: samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\graph.xml
- 업무 도메인: unknown
- 주요 유스케이스: search

## 공통 플랫폼 연계

- 메뉴 키: 플랫폼 확인 필요
- 권한 키: 플랫폼 확인 필요
- 인증 연계: 확인 필요
- 결재: 없음
- 메일: 없음
- 공통 기능 사용: 없음
- 컴포넌트별 의존성: 없음

## 레거시 분석 요약

- 주요 dataset: ds_subteacher
- 주요 transaction: TX-FNCMTR-1("svc::" + strController), TX-FORMONLOADCOMPLETED-1(http://127.0.0.1:8080/miplatform/subteacher.do)
- 주요 함수: fnSetVoInfo, fnCmTr, form_OnLoadCompleted
- 팝업 / 서브화면: 없음
- 연계 controller / service / SQL: 후속 backend trace 설계 필요

## Vue 페이지 설계 초안

- Vue 페이지명: GraphPage
- 라우트: /graph
- 상태 관리 방식: 페이지 로컬 reactive state
- 주요 컴포넌트: Static0, Grid0
- 입력 / 조회 / 저장 흐름: 초기 로드: form_OnLoadCompleted / 주요 호출 2건

## UI 규칙 요약

- 스타일: 총 5건 / 대표 토큰: align-center, bg-btntext, border-flat, font-tahoma-14, text-window
- 상태 규칙: 총 3건 / 대상: Grid0.Enable, Grid0.TabStop, Grid0.Visible
- 검증 규칙: 총 0건 / 유형: 없음
- 메시지: 총 1건 / 유형: label

## API 전략

- 기존 API 재사용: "svc::" + strController, http://127.0.0.1:8080/miplatform/subteacher.do
- 기존 API 보정: 응답/파라미터 구조 검토 필요
- 신규 API 필요: 기존 transaction만으로 부족한 경우에만 추가
- 공통 플랫폼 API 연계: 없음

## 검토 체크리스트

- 권한 맵핑 누락 여부: 권한 키 확인 필요
- 결재 연계 필요 여부: 없음
- 공통 기능 중복 구현 여부: 추가 확인 필요
- 팝업/서브화면 누락 여부: 팝업/서브화면 없음 또는 확인 필요
- UI 규칙 누락 여부: UI 규칙 요약 존재