# 분석기 입출력 스펙

## 목적

이 문서는 각 분석기가 무엇을 읽고, 어떤 규칙으로 추출하며, 어떤 필드를 채우는지 정의한다.
핵심 목적은 아래 3가지다.

- 분석기 간 인터페이스 흔들림 방지
- 휴리스틱 추출 기준 명시
- 예외 케이스와 fallback 정책 고정

## 공통 규칙

- 모든 분석기는 `PageSource`와 `PageModel`을 입력으로 받는다.
- 출력은 `PageModel` 일부 갱신으로 본다.
- 분석기는 원칙적으로 덮어쓰기보다 보강 방식으로 동작한다.
- 식별이 애매하면 빈 값보다 후보값을 남기되, `sourceRefs` 또는 주변 필드로 근거를 남긴다.
- 파싱 실패가 일부 발생해도 전체 페이지 분석은 중단하지 않는 것을 기본 정책으로 둔다.

## 공통 fallback 원칙

- XML 구조가 일부 비정형이어도 가능한 필드만 채운다.
- 컴포넌트/함수/transaction 식별이 안 되면 해당 항목만 부분 누락시키고 전체 모델은 유지한다.
- OI / Vision 특화 분석기는 일반 MES 화면에서 빈 배열을 반환해도 정상으로 본다.
- 강한 추론이 필요한 값은 "보수적 추정"을 우선한다.

## 5-1. 구조 추출기

### 화면 셸 분석기

- 입력
  - `<Window>`, `<Form>` XML
- 선행 조건
  - XML 파싱 성공
- 추출 규칙
  - `Form.Id`, `Title`, 크기/위치 속성을 읽는다.
  - `OnLoadCompleted`, `OnClose` 같은 라이프사이클 이벤트를 읽는다.
  - `popup`, `dialog`, `subview` 여부는 태그/속성/파일명 힌트로 추정한다.
- 출력
  - `pageId`
  - `pageName`
  - `pageType`
  - `legacy`
  - `layout`
- 예외 케이스
  - 루트가 바로 `<Form>`인 경우
  - `<Window>`는 있으나 `<Form>`이 없는 경우
- fallback
  - `Form`이 없으면 `pageType`은 `unknown`
  - 제목이 없으면 `pageId` 또는 파일명 기반 보정

### 컴포넌트 트리 분석기

- 입력
  - `Form` 하위 XML
- 선행 조건
  - `source.form`이 존재해야 한다.
- 추출 규칙
  - `NON_COMPONENT_TAGS`를 제외하고 태그를 컴포넌트로 간주한다.
  - 부모-자식 관계를 순회하며 `parentId`, `containerPath`를 구성한다.
  - `Top`, 태그 타입으로 `layoutGroup`을 추정한다.
  - 이벤트 속성은 `events[]`에 기록한다.
- 출력
  - `components[]`
- 예외 케이스
  - dataset, grid 내부 format/cell, record 등이 컴포넌트처럼 보이는 경우
  - `Id` 없는 컴포넌트
- fallback
  - `Id`가 없으면 `Tag_순번` 규칙으로 synthetic ID 생성
  - 부모를 못 찾으면 `parentId=""`

### XML dataset 추출기

- 입력
  - `<Datasets>` XML
  - Script dataset 조작 코드
- 선행 조건
  - dataset 태그를 식별할 수 있어야 한다.
- 추출 규칙
  - `colinfo`에서 컬럼 정의를 만든다.
  - `record`에서 기본값을 읽는다.
  - 컬럼명/사용 패턴으로 `semanticType`을 추정한다.
  - transaction/binding/script 사용처를 바탕으로 `role`, `usageContexts`를 추정한다.
- 출력
  - `datasets[]`
- 예외 케이스
  - `colinfo` 없이 record만 있는 dataset
  - 타입/사이즈 누락
- fallback
  - 정의 없는 컬럼은 record key를 기준으로 최소 컬럼 스키마 생성
  - 역할 추정 실패 시 `role="unknown"`

### Script 블록 추출기

- 입력
  - `<Script><![CDATA[...]]></Script>`
- 선행 조건
  - CDATA 전체를 문자열로 읽을 수 있어야 한다.
- 추출 규칙
  - `function name(...) { ... }` 패턴을 balanced scan으로 추출한다.
  - 문자열/주석/중첩 괄호를 최대한 안전하게 건너뛴다.
- 출력
  - `extract_functions()` 결과를 사용하는 하위 분석기 입력
- 예외 케이스
  - 주석/문자열 안의 괄호
  - 비정상 종료된 함수 블록
- fallback
  - 함수 단위 복구가 실패하면 이후 함수만 계속 탐색
  - 일부 함수 누락은 허용하고 전체 스크립트 분석은 계속 진행

### 이벤트 속성 추출기

- 입력
  - XML 속성 중 `On*`
- 선행 조건
  - 컴포넌트 또는 폼 element 접근 가능
- 추출 규칙
  - `OnClick`, `OnChanged`, `OnLoadCompleted`, `OnClose` 등을 모두 이벤트 후보로 본다.
  - 핸들러명과 연결 함수가 있으면 `effects`를 계산한다.
- 출력
  - `events[]`
- 예외 케이스
  - 핸들러 함수가 실제 스크립트에 없는 경우
  - 이벤트명이 비표준인 경우
- fallback
  - 핸들러 함수가 없어도 이벤트 엔트리는 남긴다.
  - 이벤트 타입 판별 실패 시 `eventType="unknown"`

## 5-2. 의미 분석기

### 데이터 바인딩 분석기

- 입력
  - 컴포넌트 속성
  - Grid body cell
  - Script의 `setColumn/getColumn`
- 선행 조건
  - `components[]`, `datasets[]`
- 추출 규칙
  - `BindDataset`, `InnerDataset`, `CodeColumn`, `DataColumn`을 읽는다.
  - Grid `colid`를 컬럼 바인딩으로 기록한다.
  - Script dataset 조작에서 column 단위 binding 힌트를 추출한다.
- 출력
  - `bindings[]`
- 예외 케이스
  - 표현식 내부 dataset/column 결합
  - Grid column은 있으나 dataset 연결이 누락
- fallback
  - dataset은 있으나 컬럼명을 못 알면 component-dataset 수준까지만 기록

### transaction 분석기

- 입력
  - Script 함수 body
- 선행 조건
  - 함수 블록 추출 가능
- 추출 규칙
  - `transaction(...)` 호출을 찾는다.
  - 인자 순서 기준으로 `serviceId`, `url`, 입력/출력 dataset, callback을 해석한다.
  - 함수명과 호출 순번으로 `transactionId`를 생성한다.
- 출력
  - `transactions[]`
- 예외 케이스
  - 공통 wrapper 내부 호출
  - 6개 미만 인자
- fallback
  - 누락된 인자는 빈 문자열 처리
  - URL이 없더라도 transaction 엔트리는 유지

### 이벤트 분석기

- 입력
  - XML 이벤트 속성
  - 함수 body
- 선행 조건
  - 이벤트 속성 추출기, Script 블록 추출기
- 추출 규칙
  - 이벤트명과 소스 컴포넌트를 연결한다.
  - 핸들러 body에서 transaction, navigation, alert 효과를 계산한다.
- 출력
  - `events[]`
- 예외 케이스
  - 한 이벤트가 공통 함수 여러 단계를 거쳐 실제 로직을 호출하는 경우
- fallback
  - 직접 handler body만 기준으로 1차 효과만 계산

### 함수 / 호출 그래프 분석기

- 입력
  - Script 함수 목록
  - 컴포넌트 ID 목록
- 선행 조건
  - Script 블록 추출기
- 추출 규칙
  - 함수 타입을 이벤트/헬퍼/callback으로 추정한다.
  - 함수 호출, dataset read/write, component control, platform call을 추출한다.
- 출력
  - `functions[]`
- 예외 케이스
  - 동적 함수 호출
  - 문자열 조합 함수명
- fallback
  - 정적 해석이 가능한 직접 호출만 기록

### 상태 변화 분석기

- 입력
  - Script의 `Enable`, `Visible`, `Readonly`, `set_enable` 등 상태 변경 코드
  - 컴포넌트 속성
- 선행 조건
  - `components[]`, 함수 body
- 추출 규칙
  - 컴포넌트 상태 속성 변경 구문을 탐지한다.
  - 트리거 함수, 대상 컴포넌트, 표현식을 분리한다.
- 출력
  - `stateRules[]`
- 예외 케이스
  - 복합 조건문 내부 상태 변경
- fallback
  - 조건식 전체를 `expression` 문자열로 남기고 정규화는 후순위

### 검증 규칙 분석기

- 입력
  - `if`, `alert`, `confirm`, `isNull`, `length`, `regex` 패턴
- 선행 조건
  - 함수 body 분석 가능
- 추출 규칙
  - 필수값, 길이, 형식, 범위, custom rule을 구분한다.
  - 메시지가 있으면 함께 기록한다.
- 출력
  - `validationRules[]`
- 예외 케이스
  - 검증 함수가 공통 util에 숨겨진 경우
- fallback
  - 검증 유형이 불명확하면 `validationType="custom"`

### 팝업 / 내비게이션 분석기

- 입력
  - `Dialog(...)`
  - `.Url = ...`
- 선행 조건
  - Script 함수 목록
- 추출 규칙
  - `Dialog`는 `popup`
  - `.Url =`은 `subview`
  - 파라미터 표현식을 문자열 그대로 남긴다.
- 출력
  - `navigation[]`
- 예외 케이스
  - 공통 popup wrapper
  - 다단계 문자열 조합
- fallback
  - target만 식별되면 parameterBindings는 비워도 허용

### Grid 전용 분석기

- 입력
  - Grid XML format/head/body/summary
- 선행 조건
  - `components[]`에 Grid 존재
- 추출 규칙
  - band별 cell 메타를 읽는다.
  - `columnCount`, `hasSummary`, `editable`을 계산한다.
- 출력
  - `components[].properties.gridMeta`
- 예외 케이스
  - 다단 header, merged cell, tree grid
- fallback
  - 현재는 cell 단위 플랫 메타만 유지

### 스타일 분석기

- 입력
  - 컴포넌트 style 속성
  - theme/class/token 속성
- 선행 조건
  - `components[]`
- 추출 규칙
  - 색상, 폰트, border, class, css-like 속성을 수집한다.
  - 토큰화 가능한 반복 값을 `tokenCandidate`로 추정한다.
- 출력
  - `styles[]`
- 예외 케이스
  - 인라인 style 문자열 파싱
  - 테마 상속
- fallback
  - 파싱이 애매하면 rawValue 그대로 보존

### 메시지 분석기

- 입력
  - `alert`, `confirm`, `trace`, 메시지 함수
  - 컴포넌트 `Text`
- 선행 조건
  - 함수 body
  - `components[]`
- 추출 규칙
  - 사용자 메시지 텍스트와 호출 맥락을 추출한다.
  - 라벨, 액션 라벨, alert, confirm, 상태 텍스트를 구분한다.
  - 추후 i18n 키 후보를 만들 수 있도록 원문을 보존한다.
- 출력
  - `messages[]`
  - `notes` 보강
- 예외 케이스
  - 메시지 코드 테이블 참조
- fallback
  - 문자열 literal만 우선 추출

### 공통 플랫폼 의존 분석기

- 입력
  - 함수 body
  - 이벤트-함수 매핑
  - 컴포넌트 텍스트/ID
- 선행 조건
  - `functions[]`, `events[]`, `components[]`
- 추출 규칙
  - approval, mail, auth, permission, menu 키워드를 찾는다.
  - 핸들러 함수를 통해 트리거 컴포넌트까지 역전파한다.
  - `menuKey`, `permissionKey` 후보를 만든다.
- 출력
  - `platform`
  - `components[].platformDependency`
- 예외 케이스
  - 공통 util wrapper 뒤에 숨은 호출
- fallback
  - 함수 body 탐지 실패 시 컴포넌트 텍스트/ID 기반 휴리스틱 적용

## 5-3. OI / Vision 분석기

### 실시간 데이터 분석기

- 입력
  - `setInterval`, `mqttSubscribe`, `stompSubscribe`, `signalRSubscribe`, `openSocket`, `registerHeartbeat`
  - 함수 호출 그래프
- 선행 조건
  - `functions[]`, `transactions[]`, `events[]`
- 추출 규칙
  - 폴링과 push 구독을 모두 `realtimeSubscriptions[]`로 정규화한다.
  - 시작 함수는 lifecycle caller를 거슬러 올라가 추정한다.
  - 종료 함수는 `OnClose`, `unsubscribe`, `clearInterval`, `disconnect` 힌트로 찾는다.
  - 핸들러가 갱신하는 dataset/component를 타깃으로 연결한다.
- 출력
  - `realtimeSubscriptions[]`
- 예외 케이스
  - 익명 함수 기반 interval
  - 공통 wrapper 안에 실제 subscribe가 숨은 경우
- fallback
  - 핸들러 함수명을 못 찾으면 `targetDatasets`, `targetComponents`를 비운 채 subscription만 기록

### 차트 분석기

- 입력
  - Chart/Graph/Gauge/Trend 계열 컴포넌트 속성
  - realtime/transaction 결과
- 선행 조건
  - `components[]`, `realtimeSubscriptions[]`, `transactions[]`
- 추출 규칙
  - `BindDataset`, `ChartType`, `Series`, `CategoryColumn`을 읽는다.
  - refresh mode는 realtime > transaction > manual 순으로 판정한다.
- 출력
  - `charts[]`
- 예외 케이스
  - 다중 dataset 차트
  - series가 스크립트에서 동적 변경되는 경우
- fallback
  - 차트 타입만 식별되면 series는 빈 배열 허용

### 이미지 / 비전 분석기

- 입력
  - ImageViewer/Canvas/Camera/Video 계열 컴포넌트
  - viewer 관련 함수 body
- 선행 조건
  - `components[]`, `datasets[]`
- 추출 규칙
  - 이미지 소스를 `stream`, `dataset-field`, `static-url`, `unknown`으로 구분한다.
  - overlay, ROI, zoom/pan/review 상호작용을 추출한다.
  - 결과 dataset과 비전 결과 필드를 연결한다.
- 출력
  - `imageVisionViews[]`
- 예외 케이스
  - 공통 캔버스 wrapper
  - 오버레이가 완전히 스크립트 안에만 있는 경우
- fallback
  - viewer와 dataset만 연결해도 1차 산출물로 인정

### 알람 / 이벤트 스트림 분석기

- 입력
  - dataset 컬럼
  - realtimeSubscriptions
  - alarm ack/clear 함수
- 선행 조건
  - `datasets[]`, `realtimeSubscriptions[]`, `functions[]`
- 추출 규칙
  - dataset/컬럼명에 `alarm`, `severity`, `alarmStatus`가 있으면 알람 후보로 본다.
  - severity/status 컬럼을 찾고, ack/clear 함수명을 연결한다.
  - 관련 grid/button을 `targetComponents`에 연결한다.
- 출력
  - `alarmEvents[]`
- 예외 케이스
  - 일반 event log dataset과 알람 dataset 혼재
- fallback
  - 알람 identity와 상태 필드 둘 다 없으면 생성하지 않는다.

### 설비 / 제어 명령 분석기

- 입력
  - 사용자 액션 이벤트
  - command 계열 함수 호출
  - confirm/role 문자열
- 선행 조건
  - `events[]`, `functions[]`, Script 함수 body
- 추출 규칙
  - `commandExecute`, `sendCommand`, `controlEquipment` 등 호출을 찾는다.
  - 트리거 버튼, 명령 타깃, 권한, confirm, callback을 정규화한다.
- 출력
  - `commandActions[]`
- 예외 케이스
  - review 승인/반려와 command가 섞여 보이는 함수명
- fallback
  - 명령 호출이 없더라도 함수명에 `start/stop/reset`가 있으면 후보로 기록

### Vision 판정 / 리뷰 분석기

- 입력
  - review/defect/judge dataset
  - 사용자 액션 이벤트
  - approval/platform 정보
- 선행 조건
  - `datasets[]`, `events[]`, `imageVisionViews[]`, `platform`
- 추출 규칙
  - review 대상 dataset을 찾는다.
  - 승인/반려/리뷰 함수와 버튼을 워크플로 액션으로 묶는다.
  - 상태 후보, 역할, 결재 연계를 정리한다.
- 출력
  - `reviewWorkflows[]`
- 예외 케이스
  - 로드 함수가 review queue를 조회하기 때문에 review action처럼 보이는 경우
- fallback
  - 사용자 액션 이벤트만 workflow action 후보로 인정한다.

## sourceRefs 표준

- 최소 단위: 파일 경로
- 권장 단위: `파일:Tag#Id`
- 세분화 권장 대상:
  - function
  - event
  - grid cell
  - dataset column

`sourceRefs`는 1차 분석 정확도보다 추적성 확보가 우선이다.
즉 line number가 없어도 원문 위치를 다시 찾을 수 있으면 유효하다.

## 예외 / fallback 운영 원칙

- 구조 분석기는 "최대한 많이 담기" 우선
- 의미 분석기는 "오탐보다 누락을 약간 허용" 우선
- OI / Vision 분석기는 "일반 화면에서 조용히 비우기" 우선
- 공통 플랫폼 분석기는 "중복 구현 방지"를 위해 약한 신호도 후보로 남김

## 현재 상태 기준

- 1차, 2차, 3차 구현 분석기 스펙은 현재 코드에 맞춰 정리했다.
- 스타일, 상태, 검증, 메시지 분석기까지 1차 구현이 반영되어 있다.
