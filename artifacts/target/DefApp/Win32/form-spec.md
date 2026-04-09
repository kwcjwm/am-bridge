# 페이지 전환 명세

## 기본 정보

- 페이지 ID: form
- 페이지명: New Form
- 페이지 유형: main
- 레거시 원본 파일: C:\workspace\am-bridge\samples\ScoreRanking_Proj-master\src\main\resources\egovframework\conf\scoreranking\DefApp\Win32\form.xml
- 업무 도메인: production-execution
- 주요 유스케이스: review, search

## 기존 화면 구조(아스키 와이어프레임)

```text
+----------------------------------------------------------------------------------------------------------------------------+
|PAGE form (828x408)                                                                                                         |
|레거시 화면을 좌표 기준으로 축약한 ASCII 와이어프레임                                                                                            |
|----------------------------------------------------------------------------------------------------------------------------|
|                                                                                                                            |
| [ROW 01] 타이틀 / 안내 영역                                                                                                       |
|                                                                                                                            |
|                                +-----------------------------------------------------+                                    |
|                                |Static5                                              |                                    |
|                                |Static / 디와이정보기술 2019학년도 성적조회                        |                                    |
|                                |                                                     |                                    |
|                                +-----------------------------------------------------+                                    |
|                                                                                                                            |
| [ROW 02] 조회 조건 / 액션 영역                                                                                                     |
|                                                                                                                            |
|  +------------+ +----------------+ +------------+ +------------+ +------------+                                           |
|  |Static4     | |Combo0          | |Button0     | |Button1     | |Button2     |                                           |
|  |Static / 시험 | |Combo / ds_te...| |Button / ...| |Button / ...| |Button / ...|                                           |
|  |            | |selection input | |Button0_O...| |Button1_O...| |Button2_O...|                                           |
|  +------------+ +----------------+ +------------+ +------------+ +------------+                                           |
|                                                                                                                            |
| [ROW 03] 결과 목록 + 서브뷰 영역                                                                                                    |
|                                                                                                                            |
|  +---------------------------------------------------------------+ +--------------------------------------------------+   |
|  |Grid0                                                          | |Div0                                              |   |
|  |Grid / ds_scorechk                                             | |Div / container                                   |   |
|  |cols: stuno, stuname, avgscore 외 2건                            | |embedded view area                                |   |
|  |dataset: ds_scorechk                                           | |target: dynamic or popup-linked                   |   |
|  |                                                               | |                                                  |   |
|  +---------------------------------------------------------------+ +--------------------------------------------------+   |
|                                                                                                                            |
+----------------------------------------------------------------------------------------------------------------------------+
```

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

## 상세 분석

### Dataset

#### ds_scorechk
- 역할: response
- 컬럼: stuno(STRING) size=256, stuname(STRING) size=256, avgscore(STRING) size=256, rank(STRING) size=256, denseRank(STRING) size=256
- 기본 레코드 수: 1
- 사용 컨텍스트: component, script
- 연결 컴포넌트: Grid0
- 입력 transaction: 없음
- 출력 transaction: TX-BUTTON0ONCLICK-1
- 읽는 함수: 없음
- 쓰는 함수: 없음

#### ds_testCategory
- 역할: code
- 컬럼: testCategory(STRING) size=256, testname(STRING) size=256
- 기본 레코드 수: 0
- 사용 컨텍스트: component, script
- 연결 컴포넌트: Combo0
- 입력 transaction: 없음
- 출력 transaction: TX-TESTNAMESELECT-1
- 읽는 함수: 없음
- 쓰는 함수: 없음

#### ds_screen
- 역할: view-state
- 컬럼: caption(STRING) size=256, id(STRING) size=256, level(STRING) size=256
- 기본 레코드 수: 1
- 사용 컨텍스트: component, script
- 연결 컴포넌트: 없음
- 입력 transaction: 없음
- 출력 transaction: 없음
- 읽는 함수: Button1_OnClick
- 쓰는 함수: 없음

### Component

#### Grid0
- 유형: Grid
- 레이아웃 그룹: data-panel
- 부모 / 컨테이너: form / form
- 이벤트: 없음
- 바인딩: component-dataset:ds_scorechk, grid-cell:ds_scorechk:stuno, grid-cell:ds_scorechk:stuname, grid-cell:ds_scorechk:avgscore, grid-cell:ds_scorechk:rank, grid-cell:ds_scorechk:denseRank
- styleKey: 없음
- 플랫폼 의존: 없음
- 추정 역할: 목록 / 결과 표시

#### Static5
- 유형: Static
- 레이아웃 그룹: content-panel
- 부모 / 컨테이너: form / form
- 이벤트: 없음
- 바인딩: 없음
- styleKey: align-center
- 플랫폼 의존: 없음
- 추정 역할: 라벨 / 안내 문구

#### Button0
- 유형: Button
- 레이아웃 그룹: search-panel
- 부모 / 컨테이너: form / form
- 이벤트: OnClick->Button0_OnClick
- 바인딩: 없음
- styleKey: 없음
- 플랫폼 의존: 없음
- 추정 역할: 사용자 액션 버튼(성적조회)

#### Combo0
- 유형: Combo
- 레이아웃 그룹: search-panel
- 부모 / 컨테이너: form / form
- 이벤트: 없음
- 바인딩: inner-dataset:ds_testCategory, code-data:ds_testCategory:testCategory, display-data:ds_testCategory:testname
- styleKey: 없음
- 플랫폼 의존: 없음
- 추정 역할: 입력 / 조건 제어

#### Static4
- 유형: Static
- 레이아웃 그룹: content-panel
- 부모 / 컨테이너: form / form
- 이벤트: 없음
- 바인딩: 없음
- styleKey: align-center
- 플랫폼 의존: 없음
- 추정 역할: 라벨 / 안내 문구

#### Button1
- 유형: Button
- 레이아웃 그룹: search-panel
- 부모 / 컨테이너: form / form
- 이벤트: OnClick->Button1_OnClick
- 바인딩: 없음
- styleKey: 없음
- 플랫폼 의존: 없음
- 추정 역할: 사용자 액션 버튼(과목 담당교수)

#### Div0
- 유형: Div
- 레이아웃 그룹: container-panel
- 부모 / 컨테이너: form / form
- 이벤트: 없음
- 바인딩: 없음
- styleKey: 없음
- 플랫폼 의존: 없음
- 추정 역할: 서브뷰 / 컨테이너

#### Button2
- 유형: Button
- 레이아웃 그룹: search-panel
- 부모 / 컨테이너: form / form
- 이벤트: OnClick->Button2_OnClick
- 바인딩: 없음
- styleKey: 없음
- 플랫폼 의존: 없음
- 추정 역할: 사용자 액션 버튼(장학금대상)

### Transaction / API

#### TX-TESTNAMESELECT-1
- 서비스 ID: list
- URL: http://127.0.0.1:8080/miplatform/testNameList.do
- 입력 dataset: 없음
- 출력 dataset: ds_testCategory
- 파라미터 표현식: 없음
- callback: fnCallback
- wrapper: 없음
- 해석 메모: 직접 endpoint 호출

#### TX-FNCMTR-1
- 서비스 ID: svcid
- URL: "svc::" + strController
- 입력 dataset: "ds_voInfo, ", +, inputDs
- 출력 dataset: outputDs
- 파라미터 표현식: params
- callback: fnCallback
- wrapper: fnCmTr
- 해석 메모: 공통 wrapper를 거치는 호출이므로 FE client 규약과 BE endpoint 해석 규칙을 함께 확인해야 한다

#### TX-BUTTON0ONCLICK-1
- 서비스 ID: list
- URL: http://127.0.0.1:8080/miplatform/testScoreChk.do
- 입력 dataset: 없음
- 출력 dataset: ds_scorechk
- 파라미터 표현식: strParam
- callback: fnCallback
- wrapper: 없음
- 해석 메모: 직접 endpoint 호출이지만 파라미터 조립 로직을 FE에서 명시적으로 이관해야 한다

## 함수 호출 연계

### form_OnLoadCompleted
- 호출 주체: 없음
- 직접 연결 이벤트: form.OnLoadCompleted
- 직접 하위 함수: testNameSelect
- 직접 하위 transaction: 없음
- 직접 navigation: 없음

```text
[FUNC] form_OnLoadCompleted(obj)
  <- [EVENT] form.OnLoadCompleted
  -> [FUNC] testNameSelect(obj)
       downstreamTransactions = TX-TESTNAMESELECT-1
```

### Button0_OnClick
- 호출 주체: 없음
- 직접 연결 이벤트: Button0.OnClick
- 직접 하위 함수: 없음
- 직접 하위 transaction: TX-BUTTON0ONCLICK-1
- 직접 navigation: 없음

```text
[FUNC] Button0_OnClick(obj)
  <- [EVENT] Button0.OnClick
  -> [VALIDATION] Combo0 / custom
       condition = Combo0.Value==null
       failMessage = "어떤 시험입니까? 콤보박스에서 확인해주세요"
  -> [CONTROL] Combo0
  -> [TX] TX-BUTTON0ONCLICK-1 / http://127.0.0.1:8080/miplatform/testScoreChk.do
       output = ds_scorechk
       params = strParam
       callback = fnCallback
  -> [MSG] alert / "어떤 시험입니까? 콤보박스에서 확인해주세요"
```

### Button1_OnClick
- 호출 주체: 없음
- 직접 연결 이벤트: Button1.OnClick
- 직접 하위 함수: 없음
- 직접 하위 transaction: 없음
- 직접 navigation: subview:scurl

```text
[FUNC] Button1_OnClick(obj)
  <- [EVENT] Button1.OnClick
  -> [READ] ds_screen
  -> [CONTROL] Div0
  -> [NAV] subview / scurl
```

### Button2_OnClick
- 호출 주체: 없음
- 직접 연결 이벤트: Button2.OnClick
- 직접 하위 함수: 없음
- 직접 하위 transaction: 없음
- 직접 navigation: popup:DefApp::scholarship.xml

```text
[FUNC] Button2_OnClick(obj)
  <- [EVENT] Button2.OnClick
  -> [NAV] popup / DefApp::scholarship.xml
       params = "param="+Quote(param), 600, 300, AutoSize=false resize=false
```

### fnCmTr
- 호출 주체: 없음
- 직접 연결 이벤트: 없음
- 직접 하위 함수: fnSetVoInfo
- 직접 하위 transaction: TX-FNCMTR-1
- 직접 navigation: 없음

```text
[FUNC] fnCmTr(objFrm, svcid, strController, strVoClass, inputDs, outputDs, params, callbackFnc)
  -> [FUNC] fnSetVoInfo(objFrm, strVoClass)
  -> [TX] TX-FNCMTR-1 / "svc::" + strController
       input = "ds_voInfo, ", +, inputDs
       output = outputDs
       params = params
       wrapper = fnCmTr
       callback = fnCallback
```

### fnSetVoInfo
- 호출 주체: 함수 fnCmTr
- 직접 연결 이벤트: 없음
- 직접 하위 함수: 없음
- 직접 하위 transaction: 없음
- 직접 navigation: 없음

```text
[FUNC] fnSetVoInfo(objFrm, strVoClass)
  <- [FUNC] fnCmTr
  -> [WRITE] ds_voInfo
```

### testNameSelect
- 호출 주체: 함수 form_OnLoadCompleted
- 직접 연결 이벤트: 없음
- 직접 하위 함수: 없음
- 직접 하위 transaction: TX-TESTNAMESELECT-1
- 직접 navigation: 없음

```text
[FUNC] testNameSelect(obj)
  <- [FUNC] form_OnLoadCompleted
  -> [TX] TX-TESTNAMESELECT-1 / http://127.0.0.1:8080/miplatform/testNameList.do
       output = ds_testCategory
       callback = fnCallback
```

## 이벤트 / 시나리오 흐름

### EVT-0001
- 트리거: form / OnLoadCompleted
- 핸들러: form_OnLoadCompleted
- 이벤트 유형: lifecycle
- 효과: 없음
- 흐름 요약: 하위 함수 호출: testNameSelect

### EVT-0002
- 트리거: Button0 / OnClick
- 핸들러: Button0_OnClick
- 이벤트 유형: user-action
- 효과: TX-BUTTON0ONCLICK-1, message:alert
- 흐름 요약: transaction 호출: TX-BUTTON0ONCLICK-1 / 컴포넌트 제어: Combo0

### EVT-0003
- 트리거: Button1 / OnClick
- 핸들러: Button1_OnClick
- 이벤트 유형: user-action
- 효과: navigation:subview, message:alert
- 흐름 요약: 컴포넌트 제어: Div0

### EVT-0004
- 트리거: Button2 / OnClick
- 핸들러: Button2_OnClick
- 이벤트 유형: user-action
- 효과: navigation:popup, message:alert
- 흐름 요약: 수동 확인 필요

## 함수별 슈도코드

### form_OnLoadCompleted
- 분류: event-handler
- 연결 이벤트: form.OnLoadCompleted
- 파라미터: obj
- 읽는 dataset: 없음
- 쓰는 dataset: 없음
- 제어 컴포넌트: 없음
- 호출 함수: testNameSelect
- 호출 transaction: 없음
- navigation: 없음
- validation: 없음

```text
function form_OnLoadCompleted(obj):
  trigger = form.OnLoadCompleted
  call testNameSelect()
    downstreamTransactions = TX-TESTNAMESELECT-1
```

### Button0_OnClick
- 분류: event-handler
- 연결 이벤트: Button0.OnClick
- 파라미터: obj
- 읽는 dataset: 없음
- 쓰는 dataset: 없음
- 제어 컴포넌트: Combo0
- 호출 함수: 없음
- 호출 transaction: TX-BUTTON0ONCLICK-1
- navigation: 없음
- validation: Combo0:custom

```text
function Button0_OnClick(obj):
  trigger = Button0.OnClick
  validate Combo0 with custom
    condition = Combo0.Value==null
    failMessage = "어떤 시험입니까? 콤보박스에서 확인해주세요"
  call transaction TX-BUTTON0ONCLICK-1
    url = http://127.0.0.1:8080/miplatform/testScoreChk.do
    outputDatasets = ds_scorechk
    params = strParam
    callback = fnCallback
  show alert "어떤 시험입니까? 콤보박스에서 확인해주세요"
  control components = Combo0
```

### Button1_OnClick
- 분류: event-handler
- 연결 이벤트: Button1.OnClick
- 파라미터: obj
- 읽는 dataset: ds_screen
- 쓰는 dataset: 없음
- 제어 컴포넌트: Div0
- 호출 함수: 없음
- 호출 transaction: 없음
- navigation: subview:scurl
- validation: 없음

```text
function Button1_OnClick(obj):
  trigger = Button1.OnClick
  assign subview target = scurl
  read datasets = ds_screen
  control components = Div0
```

### Button2_OnClick
- 분류: event-handler
- 연결 이벤트: Button2.OnClick
- 파라미터: obj
- 읽는 dataset: 없음
- 쓰는 dataset: 없음
- 제어 컴포넌트: 없음
- 호출 함수: 없음
- 호출 transaction: 없음
- navigation: popup:DefApp::scholarship.xml
- validation: 없음

```text
function Button2_OnClick(obj):
  trigger = Button2.OnClick
  open popup DefApp::scholarship.xml
    parameters = "param="+Quote(param), 600, 300, AutoSize=false resize=false
```

### fnCmTr
- 분류: helper
- 연결 이벤트: 없음
- 파라미터: objFrm, svcid, strController, strVoClass, inputDs, outputDs, params, callbackFnc
- 읽는 dataset: 없음
- 쓰는 dataset: 없음
- 제어 컴포넌트: 없음
- 호출 함수: fnSetVoInfo
- 호출 transaction: TX-FNCMTR-1
- navigation: 없음
- validation: 없음

```text
function fnCmTr(objFrm, svcid, strController, strVoClass, inputDs, outputDs, params, callbackFnc):
  call fnSetVoInfo()
  call transaction TX-FNCMTR-1
    url = "svc::" + strController
    inputDatasets = "ds_voInfo, ", +, inputDs
    outputDatasets = outputDs
    params = params
    callback = fnCallback
```

### fnSetVoInfo
- 분류: helper
- 연결 이벤트: 없음
- 파라미터: objFrm, strVoClass
- 읽는 dataset: 없음
- 쓰는 dataset: ds_voInfo
- 제어 컴포넌트: 없음
- 호출 함수: 없음
- 호출 transaction: 없음
- navigation: 없음
- validation: 없음

```text
function fnSetVoInfo(objFrm, strVoClass):
  write datasets = ds_voInfo
```

### testNameSelect
- 분류: helper
- 연결 이벤트: 없음
- 파라미터: obj
- 읽는 dataset: 없음
- 쓰는 dataset: 없음
- 제어 컴포넌트: 없음
- 호출 함수: 없음
- 호출 transaction: TX-TESTNAMESELECT-1
- navigation: 없음
- validation: 없음

```text
function testNameSelect(obj):
  call transaction TX-TESTNAMESELECT-1
    url = http://127.0.0.1:8080/miplatform/testNameList.do
    outputDatasets = ds_testCategory
    callback = fnCallback
```

## R&R 정의

### FE 책임
- 화면 셸과 컴포넌트 구성: Grid0, Static5, Button0, Combo0, Static4, Button1, Div0, Button2
- dataset 바인딩 구현: Grid0->ds_scorechk, Grid0->ds_scorechk, Grid0->ds_scorechk, Grid0->ds_scorechk, Grid0->ds_scorechk, Grid0->ds_scorechk, Combo0->ds_testCategory, Combo0->ds_testCategory, Combo0->ds_testCategory
- 이벤트/함수 이관: fnSetVoInfo, testNameSelect, fnCmTr, Button0_OnClick, form_OnLoadCompleted, Button1_OnClick, Button2_OnClick
- 입력 검증 구현: Combo0:custom
- 팝업/서브화면 제어: subview:scurl, popup:DefApp::scholarship.xml

### BE 책임
- API 계약 제공: TX-TESTNAMESELECT-1:http://127.0.0.1:8080/miplatform/testNameList.do, TX-FNCMTR-1:"svc::" + strController, TX-BUTTON0ONCLICK-1:http://127.0.0.1:8080/miplatform/testScoreChk.do
- 응답 dataset 계약 유지: ds_scorechk, ds_testCategory
- 공통 wrapper 해석 필요 항목: TX-FNCMTR-1

### 공통 플랫폼 책임
- 메뉴/권한/공통 기능: 없음
- 플랫폼 키 관리: 메뉴=없음, 권한=없음
- 공통 팝업/레이아웃 사용 여부: 사용 추정

### 협의 필요 항목
- 동적 endpoint/동적 subview 해석: TX-FNCMTR-1:"svc::" + strController, subview:scurl
- 메시지/i18n 정리 대상: 디와이정보기술 2019학년도 성적조회, 성적조회, 시험, 과목 담당교수, Div0, 장학금대상, 어떤 시험입니까? 콤보박스에서 확인해주세요
- 레거시 메타데이터 정리: 페이지명=New Form, formId=form

## 확인 필요 / 리스크

- 동적 endpoint 또는 wrapper transaction이 있어 API 계약을 별도 확정해야 한다.
- 서브화면/팝업 target이 변수 또는 표현식 기반이라 route map을 수동 확정해야 한다.
- custom validation이 있어 FE 구현 전에 업무 규칙을 다시 문서화해야 한다.
- 페이지 제목이 일반명칭이므로 전환 후 메뉴명/페이지명을 별도로 정제해야 한다.
- 의미 없는 기본 Text 속성이 남아 있어 화면 문구와 디버그용 기본값을 구분해야 한다.

## 검토 체크리스트

- 권한 맵핑 누락 여부: 권한 키 확인 필요
- 결재 연계 필요 여부: 없음
- 공통 기능 중복 구현 여부: 추가 확인 필요
- 팝업/서브화면 누락 여부: navigation 포함
- UI 규칙 누락 여부: UI 규칙 요약 존재