# 검증 전략

## 목적

이 문서는 `am-bridge` 분석기의 검증 기준을 정의한다.
핵심 목표는 아래다.

- 분석기별 회귀를 빠르게 감지한다.
- 누락과 오탐을 분리해서 본다.
- fixture 작성 규칙과 기대 결과 비교 규칙을 고정한다.

## 검증 레이어

### 1. 단위 테스트

- 대상
  - `script_utils.py`
  - analyzer별 핵심 추출 함수
  - generator 문자열 생성 로직
- 목적
  - 휴리스틱의 기본 동작 보장
  - 문자열 파싱 회귀 방지

### 2. fixture 기반 통합 테스트

- 대상
  - `pipeline.analyze_file()`
  - CLI 출력
- 목적
  - 실제 XML + Script 조합에서 최종 `PageModel` 결과를 확인
  - 페이지 전환 명세 생성기까지 함께 확인

### 3. 산출물 검토 테스트

- 대상
  - `artifacts/target/*.md`
  - `artifacts/*.json`
- 목적
  - 사람이 보는 문서 품질과 핵심 누락 여부 확인

## fixture 작성 형식

### XML fixture 원칙

- 한 fixture는 하나의 분석 목적을 분명히 가져야 한다.
- 태그/속성명은 레거시 실무 패턴에 가깝게 유지한다.
- 최소 fixture와 종합 fixture를 분리한다.

권장 레벨:

- `basic_page.xml`
  - 1차/2차 분석기 회귀 검증
- `oi_vision_page.xml`
  - 3차 OI / Vision 분석기 회귀 검증
- `validation_heavy_page.xml`
  - 스타일 / 상태 / 검증 / 메시지 분석기 회귀 검증
- 향후 추가 권장
  - `popup_page.xml`
  - `complex_grid_page.xml`
  - `platform_heavy_page.xml`

### Script fixture 원칙

- 가능하면 XML 내부 `<Script>`에 함께 둔다.
- 독립 함수 파싱이 필요한 경우만 별도 텍스트 fixture를 둔다.
- 한 fixture 안에서는 아래 패턴을 의도적으로 섞는다.
  - direct call
  - wrapper call
  - nested condition
  - string concat
  - confirm / alert / callback

## 결과 비교 기준

### 핵심 비교

- 완전한 JSON 문자열 비교는 우선순위가 낮다.
- 의미 단위 assertion을 우선한다.

권장 assertion 축:

- page shell
  - `pageId`, `pageType`
- dataset
  - 개수, 주요 ID, 주요 컬럼
- component
  - 주요 컴포넌트 ID/타입
- binding
  - 핵심 dataset-column 매핑
- transaction
  - URL, input/output dataset
- event/function
  - 주요 handler, call graph
- platform
  - approval, menuKey, permissionKey 후보
- OI / Vision
  - realtime source
  - chart dataset/type
  - image viewer source/overlay
  - alarm ack/clear
  - command target/role
  - review states/actions
- UI semantics
  - style token candidate
  - state rule target/condition
  - validation type/message
  - message inventory/i18n key candidate

### 문자열 산출물 비교

- `page conversion spec`는 전체 문서 일치보다 핵심 라인 포함 여부를 본다.
- assertion 대상은 아래처럼 고정한다.
  - 페이지 ID
  - 결재 여부
  - 팝업/서브화면 여부
  - OI / Vision 특화 섹션 존재 여부
  - 주요 command/review/alarm 요약

## 누락 검출 체크리스트

테스트 통과와 별개로 아래를 눈으로 점검한다.

- 레거시 dataset이 모델에 하나도 빠지지 않았는가
- Grid body column이 누락되지 않았는가
- 사용자 액션 버튼이 event/function으로 연결되었는가
- transaction output dataset과 target component 연결이 자연스러운가
- 공통 플랫폼 기능을 로컬 기능으로 오인하지 않았는가
- 일반 화면을 OI / Vision 화면으로 과탐하지 않았는가
- 알람 dataset을 일반 event log로 축소하지 않았는가
- review queue와 command action이 서로 섞이지 않았는가

## 허용 누락 / 허용 오탐 기준

### 허용 누락

- line/column 수준의 정밀 `sourceRefs`
- 공통 util 안에 숨은 간접 호출 일부
- 스타일 토큰 세분화

### 허용 오탐

- 없음이 원칙이다.
- 다만 플랫폼 의존 후보, pageType 후보처럼 "후보" 성격 필드는 약한 오탐을 허용한다.

## 실패 분류 기준

- Critical
  - 페이지 구조 자체가 깨짐
  - 핵심 dataset / transaction 누락
  - command / approval 같은 고위험 기능 오분류
- Major
  - Grid/Chart/Image/Alarm 주요 메타 누락
  - event/function 연결 누락
- Minor
  - notes, tokenCandidate, 일부 message 누락

## 실행 규칙

- `pytest`가 있으면 정식 테스트 러너로 수행한다.
- `pytest`가 없는 환경에서도 테스트 함수 직접 실행 스크립트를 유지한다.
- 새 분석기 추가 시 최소 1개 fixture와 1개 양성 assertion 세트를 함께 추가한다.
- 오탐 버그를 수정했으면 반드시 역회귀 assertion을 추가한다.

## 현재 기준선

- 현재 fixture
  - [basic_page.xml](/c:/workspace/am-bridge/tests/fixtures/basic_page.xml#L1)
  - [oi_vision_page.xml](/c:/workspace/am-bridge/tests/fixtures/oi_vision_page.xml#L1)
  - [validation_heavy_page.xml](/c:/workspace/am-bridge/tests/fixtures/validation_heavy_page.xml#L1)
- 현재 통합 테스트
  - [test_pipeline.py](/c:/workspace/am-bridge/tests/test_pipeline.py#L1)

다음 확장 우선순위는 `popup`, `complex grid`, `platform-heavy` fixture다.
