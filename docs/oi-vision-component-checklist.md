# OI / Vision 공통 항목 체크리스트

## 목적

이 문서는 일반 업무 화면 기준으로 작성된 F/E 전환 항목에서, OI 또는 Vision 시스템에 공통적으로 자주 들어가는 항목 중 누락되기 쉬운 것들을 별도로 점검하기 위한 체크리스트다.

결론부터 말하면, 기존 문서에는 기본적인 `Grid / Form / dataset / transaction / 이벤트`는 들어 있었지만 아래 영역은 보강이 필요했다.

- 실시간 데이터 수신
- 알람 / 이벤트 스트림
- 설비 상태 보드
- 차트 세분화
- 이미지 / 비전 뷰어
- ROI / overlay / annotation
- 판정 / 리뷰 워크플로
- 제어 명령 / 위험 액션

## OI 시스템에서 흔한 기본 화면 요소

- 설비 상태 카드
- 라인 / 설비 현황 보드
- 생산량 / 목표 / 달성률 KPI 카드
- Andon / 신호등 상태 표시
- 알람 배너
- 알람 / 이벤트 콘솔
- 실시간 trend chart
- stop / idle / run 비율 차트
- 공정 진행 타임라인
- 작업지시 / lot 진행 표
- recipe / parameter 패널
- start / stop / reset / retry 명령 버튼
- 인터락 / 권한 상태 표시
- 설비 연결 상태 / heartbeat 표시

## Vision 시스템에서 흔한 기본 화면 요소

- 이미지 뷰어
- 멀티 카메라 뷰
- 썸네일 갤러리
- 실시간 프레임 표시
- 이미지 compare 뷰
- zoom / pan / rotate
- ROI 박스 / 폴리곤
- defect marker overlay
- annotation toolbar
- histogram
- confidence / score panel
- OK / NG / Review 결과 패널
- defect class 분포 차트
- image history / review queue
- operator relabel / confirm 액션

## 지금까지 문서에서 빠져 있었거나 약했던 항목

### 1. 실시간 통신

누락 이유:

- 일반 업무 화면은 조회 버튼 기반일 수 있지만, OI / Vision은 주기 조회나 push가 핵심인 경우가 많다.

추가로 봐야 할 것:

- polling 주기
- websocket / push 여부
- 화면 진입 / 이탈 시 구독 시작 / 종료
- reconnect 전략
- stale data 표시 방식

### 2. 상태색과 severity

누락 이유:

- OI / Vision은 색 자체가 의미를 갖는 경우가 많다.

추가로 봐야 할 것:

- run / idle / down / alarm 색상표
- OK / NG / review 색상표
- severity 레벨
- blinking / acknowledge 상태

### 3. 차트 종류 세분화

누락 이유:

- 기존 문서에는 차트를 하나의 큰 항목으로만 봤다.

추가로 봐야 할 것:

- trend
- histogram
- heatmap
- pareto
- SPC / control chart
- gauge
- sparkline

### 4. 이미지 / 좌표계 / overlay

누락 이유:

- Vision은 일반 이미지 표시가 아니라, 좌표와 오버레이가 핵심이다.

추가로 봐야 할 것:

- 원본 이미지 크기
- 표시 배율
- 좌표 변환
- ROI / bbox / polygon
- marker / label 배치
- hover / select interaction

### 5. 판정 / 리뷰 워크플로

누락 이유:

- Vision 시스템은 조회 화면이 아니라 판정 검토 화면인 경우가 많다.

추가로 봐야 할 것:

- OK / NG / Review
- defect class
- confidence
- operator confirm
- relabel
- reject reason

### 6. 설비 명령과 위험 액션

누락 이유:

- OI는 단순 조회보다 제어 기능이 섞여 있는 경우가 많다.

추가로 봐야 할 것:

- start / stop / reset
- recipe change
- lot track in / out
- 장비 명령 실행 권한
- 이중 확인
- 감사 로그

## 컴포넌트 관점 보강 목록

### 반드시 체크할 컴포넌트

- Tree
- TreeGrid
- Splitter
- Accordion
- StatusBar
- Toolbar
- KPI Card
- Alarm Banner
- Event Console
- Timeline
- Gantt 유사 진행 뷰
- Gauge
- Heatmap
- Histogram
- Pareto Chart
- SPC Chart
- Image Canvas
- Overlay Layer
- ROI Editor
- Thumbnail Filmstrip
- Mini Map
- Compare Slider
- Video / Stream Viewer

### 프로젝트에 따라 자주 나오는 컴포넌트

- Floor Map
- Equipment Topology View
- Batch Queue Panel
- Review Queue Grid
- Defect Map
- Parameter Diff Panel
- Recipe Version Compare
- Log Console
- Terminal / Command Result Viewer

## 분석기 관점 보강 목록

기존 분석기에 더해 별도 분석기로 두는 편이 나은 것:

- 실시간 데이터 분석기
- 차트 분석기
- 이미지 / 비전 분석기
- 알람 / 이벤트 스트림 분석기
- 설비 / 제어 명령 분석기
- Vision 판정 / 리뷰 분석기

## 권장 추가 산출물

- `realtime-subscription-map`
- `chart-spec`
- `alarm-event-map`
- `image-vision-spec`
- `command-action-map`
- `review-workflow-spec`

## 최종 판단

지금까지 작성한 문서는 일반 업무 화면 전환 관점에서는 괜찮다.
하지만 OI / Vision 시스템까지 커버하려면, 위 항목들을 별도 체크리스트와 분석기 수준으로 격상해서 다뤄야 한다.
특히 아래 4개는 빠지면 안 된다.

- 실시간성
- 알람 / 상태색
- 이미지 / overlay / ROI
- 제어 명령 / 판정 리뷰

