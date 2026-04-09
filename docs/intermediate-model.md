# 중간 모델 스키마

## 목적

이 문서는 레거시 F/E 소스를 분석한 결과를 어떤 공통 JSON 모델로 저장할지 정의한다.
파서는 원문 XML/Script를 바로 Vue 코드로 바꾸지 않고, 먼저 `PageModel`을 채운다.
이 모델은 아래 3가지를 동시에 만족해야 한다.

- 레거시 원문 근거를 남길 수 있어야 한다.
- 공통 플랫폼 연계 여부를 페이지 단위로 판별할 수 있어야 한다.
- 일반 MES 화면과 OI / Vision 화면을 같은 모델에서 다룰 수 있어야 한다.

## 정규화 원칙

- 최상위 모델은 항상 `PageModel`이다.
- 모든 하위 엔티티는 식별 필드를 가진다.
- 분석기가 판별한 근거는 가능한 한 `sourceRefs`에 남긴다.
- 구현 휴리스틱으로 추론한 값이라도 필드가 비어 있지 않다면 산출물에 기록한다.
- OI / Vision 전용 필드는 일반 페이지에서 빈 배열이어도 정상이다.
- 동적 속성이 많은 레거시 특성상 일부 필드는 고정 스키마 대신 `object`로 보관한다.

## 최상위 구조

```json
{
  "pageId": "VisionDashboard",
  "pageName": "비전 리뷰 대시보드",
  "pageType": "main",
  "legacy": {},
  "platform": {},
  "layout": {},
  "datasets": [],
  "components": [],
  "bindings": [],
  "transactions": [],
  "events": [],
  "functions": [],
  "navigation": [],
  "styles": [],
  "stateRules": [],
  "validationRules": [],
  "messages": [],
  "realtimeSubscriptions": [],
  "charts": [],
  "imageVisionViews": [],
  "alarmEvents": [],
  "commandActions": [],
  "reviewWorkflows": [],
  "notes": ""
}
```

## 공통 규칙

### 식별자 규칙

- `pageId`: 폼/화면 식별자
- `datasetId`: 레거시 dataset 식별자
- `componentId`: 레거시 컴포넌트 식별자
- `transactionId`, `eventId`, `bindingId`, `subscriptionId` 등: 분석기가 생성하는 정규화 ID

### `sourceRefs` 규칙

현재 표준은 문자열 배열이다.

- XML element 참조: `relative-path:Tag#Id`
- XML element에 `Id`가 없을 때: `relative-path:Tag`
- 스크립트 전체 참조: `relative-path`
- 세분화가 필요한 경우 권장 확장 형식:
  - `relative-path:function#fnSearch`
  - `relative-path:event#ButtonSearch.OnClick`
  - `relative-path:cell`

현재 구현은 대부분 `path`, `path:Tag#Id`, `path:cell` 수준으로 기록한다.
향후 세분화해도 기존 포맷과 호환되게 유지한다.

### enum / 후보값 규칙

- `pageType`
  - `main`, `popup`, `tab-child`, `subview`, `dialog`, `unknown`
- `eventType`
  - `lifecycle`, `user-action`, `timer`, `unknown`
- `navigationType`
  - `popup`, `subview`
- `bindingType`
  - `component-dataset`, `grid-cell`, `inner-dataset`, `code-data`, `display-data`, `script-setcolumn`, `script-getcolumn`
- `direction`
  - `display-only`, `two-way`
- `dataset.role`
  - `request`, `response`, `code`, `view-state`, `realtime`, `review-queue`, `unknown`

후보값은 고정 enum이 아니라 현재 구현 기준이다.
새 레거시 변형이 나오면 후보를 늘리되 기존 값을 깨지 않도록 한다.

## 필드 정의

### PageModel

- `pageId`: 화면 대표 ID
- `pageName`: 화면 제목 또는 추정 이름
- `pageType`: 페이지 유형
- `legacy`: 레거시 메타
- `platform`: 공통 플랫폼 연계 메타
- `layout`: 화면 기본 크기/배치 속성
- `datasets`: dataset 정의 목록
- `components`: 컴포넌트 트리 목록
- `bindings`: 컴포넌트-데이터 바인딩 목록
- `transactions`: transaction/API 호출 목록
- `events`: XML 이벤트 속성 기반 이벤트 목록
- `functions`: 스크립트 함수 및 호출 그래프
- `navigation`: 팝업/서브화면 이동 목록
- `styles`: 스타일 토큰화 대상
- `stateRules`: 활성/비활성/표시 상태 변화 규칙
- `validationRules`: 입력 검증 규칙
- `messages`: 라벨/alert/confirm/상태 문구 인벤토리
- `realtimeSubscriptions`: 실시간 구독/폴링 정의
- `charts`: 차트 정의
- `imageVisionViews`: 이미지/비전 뷰 정의
- `alarmEvents`: 알람/이벤트 스트림 정의
- `commandActions`: 설비 제어 명령 정의
- `reviewWorkflows`: Vision/OI 리뷰 흐름 정의
- `notes`: 수동 보완 메모

### LegacyMeta

- `sourceFile`: 입력 파일 경로
- `windowId`: `<Window>` ID
- `formId`: `<Form>` ID
- `title`: 화면 제목
- `initialEvent`: 초기 로드 이벤트 함수
- `legacyPageType`: 레거시 폼 타입
- `includes`: include/import된 공통 스크립트 목록

### PlatformMeta

- `menuKey`: 공통 메뉴 키 후보
- `permissionKey`: 권한 키 후보
- `approvalRequired`: 결재 연계 필요 여부
- `mailIntegration`: 메일 연계 필요 여부
- `sharedComponentUsage`: 공통 플랫폼 사용 토큰 목록

### DatasetColumn

- `name`: 컬럼명
- `type`: 레거시 타입
- `size`: 크기
- `required`: 필수 여부
- `semanticType`: `id`, `code`, `status`, `time` 같은 정규화 의미
- `notes`: 수동 메모

### DatasetModel

- `datasetId`: dataset ID
- `role`: 요청/응답/코드/실시간/리뷰큐 등 역할
- `columns`: 컬럼 목록
- `defaultRecords`: XML 기본 record
- `usageContexts`: `component`, `script` 등 사용 컨텍스트
- `sourceRefs`: 원문 근거

### ComponentModel

- `componentId`: 컴포넌트 ID
- `componentType`: 레거시 태그명 기반 타입
- `parentId`: 부모 컴포넌트 ID
- `containerPath`: 상위 컨테이너 경로
- `layoutGroup`: `search-panel`, `data-panel`, `form-panel` 같은 레이아웃 그룹
- `styleKey`: 스타일 토큰 키 후보
- `properties`: 원문 속성 맵
- `events`: 이벤트 속성명 목록
- `platformDependency`: 플랫폼 의존 토큰 배열
- `sourceRefs`: 원문 근거

주의:

- `platformDependency`는 정렬된 토큰 배열로 유지한다.
- 동일 컴포넌트에서 감지된 중복 토큰은 제거한다.

### BindingModel

- `bindingId`: 바인딩 식별자
- `componentId`: 대상 컴포넌트 ID
- `datasetId`: 연결 dataset ID
- `columnName`: 연결 컬럼명
- `bindingType`: 바인딩 유형
- `direction`: 표시 전용 / 양방향
- `sourceRefs`: 원문 근거

### TransactionModel

- `transactionId`: 정규화 transaction ID
- `serviceId`: 레거시 서비스 ID
- `url`: 호출 URL
- `inputDatasets`: 입력 dataset 목록
- `outputDatasets`: 출력 dataset 목록
- `parameters`: 파라미터 표현식
- `callbackFunction`: callback 함수
- `wrapperFunction`: 공통 wrapper 함수명
- `apiCandidate`: 타깃 API 후보
- `sourceRefs`: 원문 근거

### EventModel

- `eventId`: 정규화 이벤트 ID
- `sourceComponentId`: 이벤트 발생 컴포넌트
- `eventName`: 레거시 이벤트 속성명
- `handlerFunction`: 이벤트 핸들러 함수
- `eventType`: 라이프사이클 / 사용자 액션 / 타이머
- `triggerCondition`: 추가 조건식
- `effects`: transaction, navigation, alert 등 효과 요약

### FunctionModel

- `functionName`: 함수명
- `functionType`: `event-handler`, `helper`, `callback`
- `parameters`: 파라미터 목록
- `callsFunctions`: 호출 함수 목록
- `callsTransactions`: 호출 transaction ID 목록
- `readsDatasets`: 읽는 dataset 목록
- `writesDatasets`: 쓰는 dataset 목록
- `controlsComponents`: 제어 대상 컴포넌트 목록
- `platformCalls`: 공통 플랫폼 사용 토큰
- `sourceRefs`: 원문 근거

### NavigationModel

- `navigationId`: 이동 ID
- `triggerFunction`: 이동을 유발한 함수
- `navigationType`: `popup` 또는 `subview`
- `target`: 대상 화면/URL
- `parameterBindings`: 전달 파라미터 표현식 목록
- `returnHandling`: close, callback 등 반환 처리 방식

### StyleModel

- `styleId`: 스타일 항목 ID
- `componentId`: 대상 컴포넌트
- `property`: 속성명
- `rawValue`: 원문 값
- `tokenCandidate`: 디자인 토큰 후보
- `usageScope`: page/component/global

### StateRuleModel

- `ruleId`: 상태 규칙 ID
- `targetComponentId`: 대상 컴포넌트
- `stateProperty`: `Visible`, `Enable`, `Readonly` 등
- `triggerCondition`: 조건식
- `sourceFunction`: 규칙이 발생한 함수
- `expression`: 원문 표현식
- `targetValue`: 최종 값

### ValidationRuleModel

- `ruleId`: 검증 규칙 ID
- `targetField`: 검증 대상 필드
- `validationType`: required/range/pattern/custom
- `triggerTiming`: blur/save/search/change
- `sourceFunction`: 규칙 발생 함수
- `expression`: 원문 식
- `message`: 메시지

### MessageModel

- `messageId`: 메시지 ID
- `sourceType`: `xml-property`, `script-call`, `script-assignment`
- `messageType`: `label`, `action-label`, `alert`, `confirm`, `status-text`
- `text`: 원문 메시지
- `sourceFunction`: 발생 함수
- `targetComponentId`: 연결 컴포넌트
- `i18nKeyCandidate`: 국제화 키 후보
- `sourceRefs`: 원문 근거

### RealtimeSubscriptionModel

- `subscriptionId`: 구독 ID
- `sourceType`: `polling`, `mqtt`, `stomp`, `signalr`, `pubsub`, `websocket`, `heartbeat`
- `sourceName`: topic, URL, wrapper 명
- `trigger`: 초기화 함수
- `lifecycleStart`: 시작 시점 함수
- `lifecycleEnd`: 종료 시점 함수
- `refreshIntervalMs`: 폴링 주기
- `targetComponents`: 영향받는 컴포넌트
- `targetDatasets`: 영향받는 dataset
- `errorPolicy`: `retry`, `alert`, `ignore`, `callback-handling`

### ChartModel

- `chartId`: 차트 컴포넌트 ID
- `chartType`: line/bar/pie/gauge/spc 등
- `title`: 차트 제목
- `datasetId`: 바인딩 dataset
- `series`: 시리즈 정의 배열
- `refreshMode`: `realtime`, `transaction`, `manual`
- `options`: 카테고리 컬럼, 범례, 색상 등 옵션 맵

### ImageVisionViewModel

- `viewerId`: 뷰어 ID
- `viewerType`: `image-review`, `camera-stream`, `video-viewer` 등
- `imageSource`: 이미지 원본 정의
- `overlayEnabled`: 오버레이 여부
- `overlayTypes`: `bbox`, `label`, `roi`, `mask` 등
- `interactions`: `zoom`, `pan`, `roi`, `review` 등
- `resultDatasetId`: 결과 dataset
- `resultFields`: 결과 필드 목록

### AlarmEventModel

- `eventStreamId`: 알람 스트림 ID
- `sourceType`: polling/mqtt/dataset
- `severityField`: 심각도 컬럼
- `statusField`: 상태 컬럼
- `ackFunction`: 확인 처리 함수
- `clearFunction`: 해제 처리 함수
- `targetComponents`: 알람 영향 컴포넌트
- `refreshMode`: `realtime`, `polling`, `manual`
- `colorRuleSet`: 색상 규칙 요약

### CommandActionModel

- `actionId`: 명령 ID
- `actionName`: 사용자 표시 액션명
- `triggerComponentId`: 명령 버튼/트리거 컴포넌트
- `commandTarget`: `equipment.start` 같은 명령 타깃
- `requiredRole`: 실행 권한
- `confirmationRequired`: 사용자 확인 필요 여부
- `auditRequired`: 감사 추적 필요 여부
- `successCallback`: 성공 callback
- `failureCallback`: 실패 callback

### ReviewWorkflowModel

- `workflowId`: 리뷰 워크플로 ID
- `workflowType`: `review`, `vision-review`
- `sourceDatasetId`: 리뷰 대상 dataset
- `states`: 상태 후보
- `actions`: 승인/반려/리뷰 액션 목록
- `roles`: 수행 권한 목록
- `approvalIntegration`: 결재 연계 여부
- `auditRequired`: 감사 추적 필요 여부

## 스키마 확정 범위

현재 기준으로 아래는 확정으로 본다.

- 최상위 `PageModel` 필드 목록
- `ComponentModel`, `DatasetModel`, `TransactionModel`, `FunctionModel`의 핵심 필드
- `MessageModel`을 포함한 UI 의미 모델 필드
- OI / Vision 확장 모델 필드
- `sourceRefs` 기본 형식

아래는 후속 확장 가능 영역으로 본다.

- `platformDependency` 토큰 vocabulary 정교화
- 분석기 confidence 메타 추가
- `sourceRefs`의 line/column 단위 세분화
- 스타일/상태/검증 규칙의 세부 enum 확장

## 스키마와 코드의 관계

- 실제 Python dataclass 기준은 [models.py](/c:/workspace/am-bridge/src/am_bridge/models.py#L1)다.
- JSON Schema 기준 파일은 [page-model.schema.json](/c:/workspace/am-bridge/schemas/page-model.schema.json#L1)이다.
- 문서, dataclass, JSON Schema 3개가 서로 어긋나면 schema를 먼저 수정하고 문서를 맞춘다.
