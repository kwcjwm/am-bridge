# 페이지 전환 명세

## 기본 정보

- 페이지 ID: VisionDashboard
- 페이지명: 비전 리뷰 대시보드
- 페이지 유형: main
- 레거시 원본 파일: tests\fixtures\oi_vision_page.xml
- 업무 도메인: quality
- 주요 유스케이스: control, monitor, review

## 공통 플랫폼 연계

- 메뉴 키: MENU:VisionDashboard
- 권한 키: 플랫폼 확인 필요
- 인증 연계: 확인 필요
- 결재: 필요
- 메일: 없음
- 공통 기능 사용: approval
- 컴포넌트별 의존성: ButtonJudgeOk[approval]

## 레거시 분석 요약

- 주요 dataset: ds_alarm, ds_chart, ds_reviewQueue
- 주요 transaction: TX-FNPOLLALARM-1(/api/alarm/stream), TX-FNLOADTREND-1(/api/vision/chart/trend), TX-FNLOADREVIEWQUEUE-1(/api/vision/review/queue)
- 주요 함수: form_OnLoadCompleted, form_OnClose, fnInitRealtime, fnDisposeRealtime, fnPollAlarm, fnOnAlarmMessage, fnOnReviewMessage, fnLoadTrend, fnLoadReviewQueue, fnAckAlarm, fnClearAlarm, fnStartEquipment, fnJudgeOk, fnJudgeNg, fnRealtimeCallback, fnCommandSuccess, fnCommandFailure, fnCallback
- 팝업 / 서브화면: 없음
- 연계 controller / service / SQL: 후속 backend trace 설계 필요

## Vue 페이지 설계 초안

- Vue 페이지명: VisionDashboardPage
- 라우트: /vision-dashboard
- 상태 관리 방식: 페이지 로컬 reactive state + 실시간 구독 상태 분리
- 주요 컴포넌트: ChartTrend, ImageViewerMain, GridAlarm, GridReview, ButtonAckAlarm, ButtonClearAlarm, ButtonStartEquipment, ButtonJudgeOk, ButtonJudgeNg
- 입력 / 조회 / 저장 흐름: 초기 로드: form_OnLoadCompleted, form_OnClose / 사용자 액션: fnAckAlarm, fnClearAlarm, fnStartEquipment, fnJudgeOk, fnJudgeNg / 주요 호출 3건 / 실시간 구독 3건

## UI 규칙 요약

- 스타일: 총 0건 / 대표 토큰: 없음
- 상태 규칙: 총 0건 / 대상: 없음
- 검증 규칙: 총 0건 / 유형: 없음
- 메시지: 총 9건 / 유형: action-label, alert, confirm

## API 전략

- 기존 API 재사용: /api/alarm/stream, /api/vision/chart/trend, /api/vision/review/queue
- 기존 API 보정: 응답/파라미터 구조 검토 필요
- 신규 API 필요: 기존 transaction만으로 부족한 경우에만 추가
- 공통 플랫폼 API 연계: approval

## OI / Vision 특화

- 실시간 구독: polling:/api/alarm/stream, mqtt:/topic/alarm, mqtt:/topic/vision/review
- 차트: ChartTrend(line/ds_chart)
- 이미지 / 비전 뷰: ImageViewerMain(image-review/ds_reviewQueue)
- 알람 스트림: ALARM:ds_alarm(realtime/fnAckAlarm)
- 제어 명령: 설비 시작(equipment.start)
- 리뷰 워크플로: REVIEW-0001(vision-review/ds_reviewQueue)

## 검토 체크리스트

- 권한 맵핑 누락 여부: 권한 키 확인 필요
- 결재 연계 필요 여부: 필요
- 공통 기능 중복 구현 여부: 공통 기능 재사용 우선
- 팝업/서브화면 누락 여부: 팝업/서브화면 없음 또는 확인 필요
- UI 규칙 누락 여부: UI 규칙 요약 존재