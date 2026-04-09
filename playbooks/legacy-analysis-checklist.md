# Legacy Analysis Checklist

## 1. Source Access

- 반출 가능한 자산은 무엇인가
- 원본 소스 대신 메타데이터만 남겨야 하는가
- 익명화가 필요한 식별자와 코드값은 무엇인가

## 2. UI Asset

- 화면 정의 파일 종류는 무엇인가
- 화면별 dataset, component, event, popup, include 관계는 무엇인가
- transaction 호출 패턴은 어디에 정의되어 있는가

## 3. Backend Asset

- controller endpoint 목록
- request parameter 해석 방식
- service / DAO / mapper 연결 구조
- 예외 처리와 공통 interceptor 구조

## 4. Data Access

- SQL map 또는 mapper 파일 위치
- query id와 업무 기능의 연결
- CRUD 유형과 파라미터 구조
- 저장 프로시저 / 함수 / batch 의존성

## 5. Domain and Process

- 화면명이 아니라 업무 object는 무엇인가
- 조회 / 저장 / 승인 / 배치 / 인터페이스 중 어떤 유형인가
- MES 공통 도메인 중 어느 영역에 속하는가

## 6. Cross-cutting

- 권한 처리 위치
- 감사 / 이력 / 상태변경 기록 방식
- 인터페이스 / 파일 연계 / 배치 스케줄링 존재 여부

## 7. Migration Readiness

- 추적성이 확보되었는가
- 타깃 API 계약서로 정리 가능한가
- 자동 생성 가능한 부분과 수동 설계가 필요한 부분이 분리되었는가

