# Architecture

## 목표 아키텍처 관점

이 저장소는 레거시 코드를 직접 변환하는 도구보다, "공통 플랫폼 위에서 업무 페이지를 `Vue 3`로 전환"하는 7단계 파이프라인을 지원하는 작업 프레임을 목표로 한다.

1. `Source Intake`
2. `Legacy Inventory`
3. `Platform Boundary Definition`
4. `Canonical Normalization`
5. `Target Blueprint`
6. `Scaffold Generation`
7. `Review and Verification`

## 레이어 구성

### 1. Source Intake

- 입력 소스 유형 정의
- 반출 가능 범위 정의
- 익명화 / 요약 / 메타데이터 추출 기준 정의

입력 대상 예시:

- MiPlatform / XPlatform / Nexacro 화면 XML
- Spring MVC Controller / Service / DAO
- iBATIS / MyBatis SQL map
- DB 모델링 산출물
- 배치 / 인터페이스 명세
- 공통 플랫폼 연계 문서 / 공통 컴포넌트 가이드 / 인증 규칙

### 2. Legacy Inventory

레거시 자산을 아래 단위로 수집한다.

- 화면 인벤토리
- dataset 인벤토리
- transaction 인벤토리
- endpoint 인벤토리
- service / query 인벤토리
- 배치 / 인터페이스 인벤토리
- 공통 기능 의존 인벤토리

핵심은 "파일 목록"이 아니라 "업무 추적 단위"로 정리하는 것이다.

### 3. Platform Boundary Definition

공통 플랫폼이 이미 제공하는 기능과, 업무 페이지가 직접 담당해야 할 기능을 먼저 나눈다.

- 공통 플랫폼 제공 기능
- 업무 페이지 구현 기능
- 플랫폼 API / SDK / 공통 컴포넌트 연계 포인트
- 페이지별 권한 / 결재 / 메일 호출 여부

이 단계가 빠지면 실제 전환 범위가 과대평가된다.

### 4. Canonical Normalization

레거시 명칭과 구현 흔적을 범용 개념으로 정규화한다.

- 화면명 -> use case
- dataset -> request / response contract
- controller method -> application service
- SQL query -> business capability / data access pattern
- 고객사 코드값 -> canonical code / reference data

이 단계에서 고객사 종속 표현과 샘플 종속 표현을 걷어낸다.

### 5. Target Blueprint

타깃 산출물은 코드 자체보다 청사진을 우선한다.

- frontend page spec
- platform integration spec
- backend API contract
- DTO / schema draft
- service boundary
- module map
- migration notes

기본 타깃은 `Vue 3 업무 페이지`를 전제로 두되, 업무 로직과 공통 플랫폼 기능을 분리해서 본다.
backend는 항상 신규 구축 대상으로 가정하지 않고, 업무 API 정비 또는 연계 필요 여부를 별도로 판정한다.

### 6. Scaffold Generation

자동 생성은 다음처럼 제한적으로 본다.

- page scaffold
- route / menu meta draft
- platform integration hook draft
- REST controller / DTO / service skeleton
- mapper / repository placeholder
- OpenAPI draft
- conversion report draft

자동 생성 결과는 "초안"이며, 설계 검토와 보정이 필수다.

### 7. Review and Verification

검증은 코드 컴파일 여부만으로 끝내지 않는다.

- 레거시 기능 누락 여부
- transaction / dataset 매핑 누락 여부
- domain naming 적합성
- 화면-API-DB 추적성
- 공통 플랫폼 연계 적합성
- 권한 / 이력 / 감사 / 인터페이스 영향

## 표준 산출물 체인

아래 산출물은 서로 추적 가능해야 한다.

- `screen inventory`
- `dataset contract`
- `transaction map`
- `platform dependency map`
- `service/use-case map`
- `sql inventory`
- `canonical domain map`
- `page conversion spec`
- `api contract draft`
- `module blueprint`
- `conversion report`

## 현재 저장소에서 먼저 만들 것

- 범용 MES 도메인 지식의 최소 기준선
- 분석 체크리스트
- 산출물 템플릿
- 샘플 검증용 artifact 적재 구조
- 공통 플랫폼 경계 정의 문서

## 나중에 붙일 수 있는 것

- XML parser
- controller / SQL relation extractor
- canonical mapping rule engine
- scaffold generator
- 변경 영향도 리포터
- 공통 플랫폼 연계 코드 생성기
