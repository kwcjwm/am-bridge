# F/E 전환 상세 설계

## 목적

이 문서는 공통 플랫폼 위에서 레거시 업무 화면을 `Vue 3` 페이지로 전환하기 위해, 프런트엔드 관점에서 무엇을 빠짐없이 분석해야 하는지 정리한 상세 설계 문서다.

핵심은 아래 두 가지다.

- 화면 파일을 바로 Vue 코드로 바꾸려 하지 않는다.
- 먼저 레거시 화면을 구조화한 뒤, 중간 모델로 정규화하고, 그 다음 타깃 페이지 설계로 넘긴다.

## 기본 전제

- 공통 플랫폼은 이미 존재한다.
- 메뉴, 결재, 권한, 인증, 메일, 공통 레이아웃은 재구현 대상이 아니다.
- 실제 납품 단위는 페이지다.
- 하지만 분석 기준은 여전히 `dataset / transaction / component / function / domain`이어야 한다.

## 보통 들어오는 레거시 화면 구조

MiPlatform 계열 화면은 보통 아래와 비슷한 구조를 가진다.

```xml
<Window>
  <Form ...>
    <Datasets>...</Datasets>
    <Grid ... />
    <Combo ... />
    <Button ... />
    <Div ... />
  </Form>
  <Script><![CDATA[
    function form_OnLoadCompleted(obj) { ... }
    function Button0_OnClick(obj) { ... }
  ]]></Script>
</Window>
```

실제 프로젝트마다 차이는 있지만, 대체로 아래 축으로 나뉜다.

- 화면 껍데기
- dataset 정의
- 컴포넌트 트리
- 속성 및 스타일
- 이벤트 연결
- 내부 스크립트 함수
- 공통 스크립트 호출
- transaction 호출
- 팝업 / 서브화면 연결

즉 F/E 전환은 XML 태그 치환 문제가 아니라, 화면 구조 + 데이터 바인딩 + 이벤트 흐름 + 호출 규칙을 함께 읽어야 하는 문제다.

## 전환 전에 반드시 확보해야 하는 산출물

- 페이지 인벤토리
- 컴포넌트 인벤토리
- dataset 계약서
- 컴포넌트-데이터 바인딩 맵
- transaction 맵
- 실시간 구독 맵
- 이벤트 맵
- 함수 맵
- 팝업 / 내비게이션 맵
- 스타일 / 디자인 토큰 맵
- 상태 / 검증 규칙 맵
- 공통 플랫폼 의존 맵
- 차트 명세
- 이미지 / 비전 표시 명세
- 알람 / 이벤트 처리 맵
- 페이지 전환 명세서

이 산출물이 있어야 그 다음에 Vue 페이지 구조, 컴포넌트 구조, API 계약, 상태 관리 방식을 결정할 수 있다.

## 추천 중간 모델

레거시 화면을 바로 타깃 코드로 만들지 말고, 먼저 페이지별 정규화 모델을 만든다.

```json
{
  "pageId": "PAGE-001",
  "sourceFile": "legacy/form.xml",
  "shell": {},
  "datasets": [],
  "components": [],
  "bindings": [],
  "transactions": [],
  "events": [],
  "functions": [],
  "styles": [],
  "navigation": [],
  "validationRules": [],
  "platformDependencies": []
}
```

모든 분석기는 이 중간 모델의 일부를 채우는 방식으로 설계하는 편이 낫다.

## 분석기 분류

아래는 F/E 전환을 위해 준비해야 하는 분석기 목록이다.

### 1. 화면 셸 분석기

분석 대상:

- `Window`
- `Form`
- 화면 ID
- 타이틀
- 초기 로드 이벤트
- 메인 화면 / 팝업 화면 여부
- 포함 관계

입력 소스:

- 화면 XML
- 프로젝트 메인 설정 파일
- 화면 로딩 설정 파일

산출물:

- 페이지 기본 메타
- 화면 유형
- 루트 컨테이너 구조

구현 포인트:

- XML DOM 파서 기반으로 구현
- 루트 태그, Form 속성, 초기 이벤트를 우선 추출

### 2. 컴포넌트 트리 분석기

분석 대상:

- Grid
- Button
- Static
- Edit
- MaskEdit
- TextArea
- Combo
- Radio
- CheckBox
- Calendar
- Div
- Tab
- ImageViewer
- WebBrowser
- 사용자 정의 컴포넌트

입력 소스:

- 화면 XML

산출물:

- 컴포넌트 인벤토리
- 부모-자식 관계
- 컨테이너 구조
- 컴포넌트 유형별 개수

구현 포인트:

- XML 태그명을 컴포넌트 타입으로 읽는다.
- `Id`, 컨테이너 위치, 부모 경로를 함께 저장한다.

### 3. 레이아웃 분석기

분석 대상:

- `Left`, `Top`, `Width`, `Height`
- `Right`, `Bottom`
- 절대 배치
- 컨테이너 내부 배치
- 탭 / 디브 / 팝업 내부 레이아웃

입력 소스:

- 화면 XML 속성

산출물:

- 레이아웃 모델
- responsive 전환 난이도
- 레이아웃 재구성 후보

구현 포인트:

- 절대좌표 기반 화면은 그대로 옮기지 않는다.
- 컴포넌트 군집을 찾아 섹션, 폼영역, 검색영역, 그리드영역으로 재분류해야 한다.

### 4. 스타일 분석기

분석 대상:

- `BkColor`
- `Color`
- `Font`
- `Align`
- `Border`
- `CssClass` 유사 속성
- 이미지 리소스
- 공통 스타일 스크립트

입력 소스:

- 화면 XML 속성
- 공통 스타일 파일
- 이미지 / 리소스 경로

산출물:

- 스타일 인벤토리
- 공통 디자인 토큰 후보
- 컴포넌트별 스타일 규칙

구현 포인트:

- 인라인 속성은 토큰화 후보로 모은다.
- 색상, 폰트, 정렬, 강조 패턴을 중복 기준으로 그룹핑한다.

### 5. dataset 정의 분석기

분석 대상:

- dataset ID
- 컬럼명
- 타입
- 길이
- 기본 record
- 초기 데이터
- 내부 전용 dataset

입력 소스:

- XML 내 `Datasets`
- 스크립트 내 dataset 조작 코드

산출물:

- dataset schema
- request/response 후보
- 코드 테이블 후보

구현 포인트:

- `ds_` 네이밍만 믿지 말고 실제 사용 위치를 같이 읽는다.
- 조회용, 저장용, 코드목록용, 화면상태용 dataset을 구분해야 한다.

### 6. 데이터 바인딩 분석기

분석 대상:

- `BindDataset`
- `colid`
- `CodeColumn`
- `DataColumn`
- `InnerDataset`
- 그리드 head/body cell 매핑
- 편집 컴포넌트와 dataset 컬럼 연결

입력 소스:

- XML 컴포넌트 속성
- Grid `contents`
- Script 내 `setColumn`, `getColumn`, `copyData`, `clearData`

산출물:

- 컴포넌트-컬럼 매핑표
- 화면 입력 / 출력 필드 목록
- DTO 필드 후보

구현 포인트:

- Grid는 별도 분석기로 세분화하는 편이 낫다.
- Combo는 코드값 컬럼과 표시값 컬럼을 함께 추출해야 한다.

### 7. transaction 분석기

분석 대상:

- `transaction(...)` 호출
- `svcid`
- URL
- input dataset
- output dataset
- parameter string
- callback 함수
- 공통 wrapper 함수

입력 소스:

- 화면 Script
- 공통 Script
- 서비스 URL 설정

산출물:

- transaction 맵
- API 초안 후보
- 입력/출력 dataset 연결표

구현 포인트:

- 직접 `transaction(...)` 호출과 wrapper 함수 호출을 둘 다 잡아야 한다.
- `svc::` 별칭, 절대 URL, 상대 URL 케이스를 모두 고려한다.

### 8. 이벤트 분석기

분석 대상:

- `OnLoadCompleted`
- `OnClick`
- `OnChanged`
- `OnSelChanged`
- `OnKeyDown`
- `OnRowPosChanged`
- 기타 컴포넌트 이벤트

입력 소스:

- XML 이벤트 속성
- Script 함수 정의

산출물:

- 이벤트 맵
- 페이지 라이프사이클 흐름
- 사용자 액션 시나리오

구현 포인트:

- 이벤트 속성에 적힌 함수와 실제 함수 정의를 연결해야 한다.
- 이벤트가 transaction, popup, validation 중 무엇을 유발하는지 분류한다.

### 9. 함수 / 메서드 분석기

분석 대상:

- 페이지 내부 함수
- 공통 함수
- wrapper 함수
- callback 함수
- helper 함수
- dataset 조작 함수
- 화면 제어 함수

입력 소스:

- `Script <![CDATA[ ... ]]>`
- 공통 JS

산출물:

- 함수 인벤토리
- 호출 그래프
- 부작용 목록
- 재사용 가능 공통 로직 목록

구현 포인트:

- 1차는 함수 시그니처와 호출 관계를 추출한다.
- 2차는 함수가 dataset, transaction, popup, component state에 미치는 영향을 태깅한다.

### 10. 상태 변화 분석기

분석 대상:

- `Visible`
- `Enable`
- `ReadOnly`
- `TabStop`
- `Value`
- 버튼 클릭 후 상태 변경
- 조회 후 그리드 활성화
- 권한에 따른 화면 제어

입력 소스:

- XML 기본 속성
- Script 내 상태 변경 함수

산출물:

- 상태 전이 규칙
- 조건부 렌더링 후보
- 조건부 비활성화 규칙

구현 포인트:

- Vue 전환 시 `ref`, `computed`, `v-if`, `v-show`, `disabled`로 옮길 대상인지 구분해야 한다.

### 11. 검증 규칙 분석기

분석 대상:

- 필수값 체크
- 길이 체크
- 숫자 / 날짜 / 코드 형식
- 마스킹
- 저장 전 검증
- 중복 체크
- 경고 / alert 메시지

입력 소스:

- Script
- 컴포넌트 속성
- 공통 검증 함수

산출물:

- 필드 검증 명세
- 페이지 검증 시나리오
- 공통 검증 유틸 후보

구현 포인트:

- 단순 regex보다 "언제 검증하는가"가 중요하다.
- 입력 즉시 검증, 저장 시 검증, 조회 조건 검증을 구분해야 한다.

### 12. 팝업 / 내비게이션 분석기

분석 대상:

- `Dialog(...)`
- `Div.Url`
- 탭 전환
- 팝업 호출
- 부모-자식 화면 관계
- 파라미터 전달
- 반환값 처리

입력 소스:

- Script
- XML 내 서브화면 정의

산출물:

- 페이지 이동 맵
- 팝업 명세
- route 설계 후보

구현 포인트:

- 라우트 전환, 모달, 드로어, 인라인 서브뷰 중 무엇으로 옮길지 판단 근거를 남겨야 한다.

### 13. Grid 전용 분석기

분석 대상:

- head / body / summary 구조
- 컬럼 순서
- 컬럼 폭
- display 타입
- checkbox / combo / button cell
- merge / 정렬 / 합계
- editable 여부
- row 상태

입력 소스:

- Grid `contents`
- Grid 속성
- Script 내 Grid 조작 코드

산출물:

- Grid 컬럼 명세
- 표준 테이블 컴포넌트 매핑표
- 셀 렌더링 규칙

구현 포인트:

- Grid는 일반 컴포넌트 분석기와 분리해야 한다.
- 대부분의 업무 화면 복잡도가 Grid에 몰린다.

### 14. 코드성 컴포넌트 분석기

분석 대상:

- Combo
- Radio
- CheckBox
- 멀티선택 리스트
- 코드 조회 dataset

입력 소스:

- XML 속성
- 코드 dataset 정의
- 초기 조회 transaction

산출물:

- 코드값-표시값 매핑표
- 옵션 로딩 전략
- 공통 코드 연계 후보

구현 포인트:

- 공통 플랫폼 코드 서비스로 치환 가능한지 먼저 판단한다.

### 15. 메시지 / 문구 분석기

분석 대상:

- `Text`
- alert 문구
- confirm 문구
- 상태 메시지
- 하드코딩 라벨

입력 소스:

- XML
- Script
- 메시지 리소스 파일

산출물:

- 라벨 인벤토리
- 국제화 후보
- 공통 메시지 분리 후보

구현 포인트:

- 하드코딩 텍스트는 나중에 반드시 문제 된다.
- 페이지 전환 단계에서 메시지 키 체계도 같이 정리하는 편이 낫다.

### 16. 공통 플랫폼 의존 분석기

분석 대상:

- 메뉴 연계
- 권한 키
- 인증 정보 접근
- 결재 호출
- 메일 발송 호출
- 공통 팝업 / 공통 코드 / 공통 레이아웃 사용

입력 소스:

- 화면 Script
- 공통 JS
- 공통 플랫폼 연계 문서
- 메뉴 / 권한 정책 문서

산출물:

- 플랫폼 의존 맵
- 플랫폼 호출 포인트 목록
- 재구현 금지 목록

구현 포인트:

- 이 분석기가 없으면 업무 페이지 범위가 계속 부풀어진다.

### 17. 오류 / 콜백 분석기

분석 대상:

- `fnCallback`
- result code
- result message
- 오류 alert
- 공통 예외 처리

입력 소스:

- Script
- 공통 JS
- backend 응답 패턴 문서

산출물:

- 성공 / 실패 처리 시나리오
- 공통 에러 처리 규칙

구현 포인트:

- Vue 전환 시 토스트, 다이얼로그, 글로벌 에러 핸들러 중 어디로 보낼지 기준이 필요하다.

### 18. 특수 기능 분석기

분석 대상:

- 엑셀 다운로드
- 업로드
- 인쇄
- 차트
- 클립보드
- 파일 첨부
- 외부 호출
- 브라우저 임베드

입력 소스:

- Script
- 사용자 정의 컴포넌트
- backend 연계 문서

산출물:

- 특수 기능 목록
- 별도 전환 전략 필요 항목

구현 포인트:

- 이 영역은 일반 페이지 전환 규칙으로 처리되지 않는 경우가 많다.

### 19. 실시간 데이터 분석기

분석 대상:

- polling
- timer
- 주기성 조회
- websocket 유사 통신
- 서버 push
- heartbeat
- 설비 상태 갱신
- KPI 자동 새로고침

입력 소스:

- Script
- 공통 JS
- 통신 wrapper
- backend 실시간 인터페이스 문서

산출물:

- 실시간 구독 맵
- 갱신 주기 표
- 상태 동기화 규칙
- lifecycle 해제 규칙

구현 포인트:

- OI와 Vision은 일반 업무 화면보다 실시간성이 훨씬 중요하다.
- `mounted / unmounted` 기준의 구독 / 해제 규칙까지 남겨야 한다.

### 20. 차트 분석기

분석 대상:

- line chart
- bar chart
- stacked bar
- pie / donut
- scatter
- histogram
- heatmap
- pareto
- control chart
- trend chart
- gauge
- sparkline

입력 소스:

- 사용자 정의 차트 컴포넌트
- Script
- dataset
- 차트 설정 객체

산출물:

- 차트 명세
- 차트별 입력 dataset / series 매핑
- 실시간 차트 여부
- 공통 차트 컴포넌트 매핑 후보

구현 포인트:

- 차트는 "그림"이 아니라 `series / axis / aggregation / refresh rule`까지 분석해야 한다.

### 21. 이미지 / 비전 분석기

분석 대상:

- image viewer
- multi-image panel
- camera feed
- snapshot
- thumbnail strip
- image compare
- overlay
- bbox / polygon / roi
- defect marker
- measurement line
- zoom / pan / rotate

입력 소스:

- XML 컴포넌트
- Script
- 사용자 정의 이미지 컴포넌트
- 이미지 경로 / binary 응답 연계 문서

산출물:

- 이미지 / 비전 컴포넌트 명세
- 이미지 소스 유형
- 오버레이 / annotation 규칙
- 뷰어 상호작용 명세

구현 포인트:

- Vision 계열은 일반 이미지 표시와 다르게 좌표계, 오버레이, 판정결과 표시가 핵심이다.

### 22. 알람 / 이벤트 스트림 분석기

분석 대상:

- alarm banner
- event list
- ack / clear
- severity
- 발생시간 / 해제시간
- 설비상태 전이
- 경광등 / 색상상태

입력 소스:

- Script
- dataset
- 공통 알람 함수
- 실시간 이벤트 인터페이스 문서

산출물:

- 알람 / 이벤트 맵
- severity 규칙
- 상태색 매핑표
- 확인 / 해제 액션 명세

구현 포인트:

- OI 화면은 알람과 설비 상태가 핵심이므로, 이 영역을 일반 메시지 처리와 분리해야 한다.

### 23. 설비 / 제어 명령 분석기

분석 대상:

- start / stop / reset
- recipe download
- model change
- lot track in / out
- bypass
- retry
- 장비 명령 버튼
- interlock 표시

입력 소스:

- Script
- 버튼 이벤트
- backend command api 문서
- 권한 정책 문서

산출물:

- 제어 명령 명세
- 위험 액션 목록
- 이중 확인 / 권한 필요 액션 목록

구현 포인트:

- OI는 조회 화면이 아니라 제어 화면일 수 있으므로, 명령 액션은 일반 CRUD와 별도로 다뤄야 한다.

### 24. Vision 판정 / 리뷰 분석기

분석 대상:

- OK / NG 판정
- defect class
- confidence score
- review result
- operator relabel
- reject reason
- sample review queue
- image history

입력 소스:

- dataset
- Script
- 결과 Grid
- 이미지 뷰어 overlay 데이터

산출물:

- 판정 결과 모델
- defect taxonomy
- 리뷰 워크플로
- 운영자 보정 액션 명세

구현 포인트:

- Vision 시스템은 "이미지 표시"보다 "판정과 리뷰 흐름"이 더 중요할 수 있다.

## 컴포넌트 계열별 준비 항목

### 입력 계열

- Edit
- MaskEdit
- TextArea
- Calendar
- CheckBox
- Radio
- Combo

준비할 것:

- value 바인딩 방식
- 필드 타입
- 검증 규칙
- placeholder / 기본값
- 읽기전용 / 활성화 상태
- 코드 테이블 연계 여부

### 액션 계열

- Button
- ImageButton
- Toolbar 유사 컴포넌트

준비할 것:

- 이벤트 함수
- 호출 transaction
- 팝업 / 저장 / 조회 / 삭제 유형
- 권한 체크 여부

### 데이터 표시 계열

- Grid
- Static
- ImageViewer
- 차트
- KPI 카드
- 상태 배지
- 알람 배너
- 이벤트 리스트
- 히스토리 타임라인

준비할 것:

- 바인딩 dataset
- 컬럼 / 셀 구조
- 포맷팅
- 정렬 / 합계 / 강조 규칙
- 실시간 갱신 여부
- 상태색 / severity 규칙

### 컨테이너 계열

- Div
- Tab
- GroupBox
- Popup
- Splitter
- Accordion
- 좌우 비교 패널
- 썸네일 필름스트립 컨테이너

준비할 것:

- 자식 컴포넌트 구조
- 서브화면 로딩 규칙
- 파라미터 전달
- 라우트 또는 모달 전환 전략
- 실시간 구독 해제 범위

### OI / Vision 특화 계열

- 설비 상태 패널
- Andon / 신호등 패널
- KPI 보드
- 트렌드 차트
- SPC / control chart
- histogram
- heatmap
- defect map
- camera live view
- image review viewer
- ROI editor
- overlay canvas
- annotation toolbar
- thumbnail gallery
- alarm console
- event timeline
- recipe parameter panel
- model selector

준비할 것:

- 실시간성
- 이미지 / 바이너리 소스
- 좌표계
- 판정 결과 데이터
- 상태색 규칙
- 제어 명령 권한
- 리뷰 / 승인 흐름

## 분석 소스 우선순위

페이지를 분석할 때는 아래 순서가 낫다.

1. 화면 XML
2. 페이지 Script
3. 공통 Script
4. 프로젝트 메인 설정
5. backend controller / service / SQL
6. 공통 플랫폼 문서

이 순서를 추천하는 이유는, F/E 전환은 결국 "화면에서 어떤 데이터를 언제 어떤 흐름으로 쓰는가"를 잡는 일이기 때문이다.

## 구현 전략

분석기를 한 번에 만들지 말고 3계층으로 나누는 편이 낫다.

### 1계층. 구조 추출기

- XML 파서
- Script 블록 추출기
- 함수 정의 추출기
- 이벤트 속성 추출기

역할:

- 원문 소스에서 구조를 잃지 않고 추출한다.

### 2계층. 의미 분석기

- dataset 분석기
- binding 분석기
- transaction 분석기
- function call graph 분석기
- navigation 분석기
- validation 분석기
- style 분석기
- platform dependency 분석기

역할:

- 구조를 업무 의미와 연결한다.

### 3계층. 타깃 설계기

- page conversion spec 생성기
- component inventory 생성기
- API draft 생성기
- Vue page blueprint 생성기
- chart spec 생성기
- image / vision view spec 생성기
- realtime subscription spec 생성기

역할:

- 분석 결과를 실제 전환 산출물로 바꾼다.

## 먼저 준비해야 할 항목

우선순위 기준으로 보면 아래부터 준비하는 것이 맞다.

1. 화면 셸 분석기
2. 컴포넌트 트리 분석기
3. dataset 정의 분석기
4. 데이터 바인딩 분석기
5. transaction 분석기
6. 이벤트 / 함수 분석기
7. Grid 전용 분석기
8. 공통 플랫폼 의존 분석기
9. 페이지 전환 명세 생성기
10. 실시간 데이터 분석기
11. 차트 분석기
12. 이미지 / 비전 분석기
13. 알람 / 이벤트 스트림 분석기
14. 스타일 / 검증 / 메시지 분석기

## 주의할 점

- XML만 보고 전환하면 반드시 실패한다.
- Script만 보고 전환해도 실패한다.
- Grid를 일반 컴포넌트처럼 처리하면 실패한다.
- 공통 플랫폼 경계를 먼저 자르지 않으면 범위가 무한정 커진다.
- 페이지 단위로 납품하되, 중간 모델은 페이지보다 더 구조적으로 가져가야 한다.

## 바로 다음 산출물 제안

이 문서 다음으로 바로 필요한 것은 아래 3개다.

- `component inventory`
- `function map`
- `page flow spec`

이 3개가 있어야 실제 페이지 단위 전환 설계를 돌릴 수 있다.
