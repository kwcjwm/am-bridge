# Roadmap

## Phase 0. Foundation

- 저장소 목적과 비목적 정의
- 범용 MES domain 기준선 정의
- 산출물 템플릿과 artifact 적재 구조 정의

## Phase 1. Legacy Analysis PoC

- 공개 샘플에서 화면 / dataset / transaction 추출
- controller / service / SQL 연결 추적
- 표준 inventory 산출물 생성

## Phase 2. Canonical Mapping

- 레거시 명칭을 canonical domain으로 정규화
- transaction 유형과 use case taxonomy 정리
- 공통 DTO / schema 패턴 정리

## Phase 3. Target Blueprint

- Vue 3 화면 청사진 템플릿 정리
- Spring Boot API / service / DTO 초안 정리
- 모듈 경계와 package / feature 기준 정리

## Phase 4. Assisted Scaffold

- 반복 가능한 초안 생성 자동화
- conversion report 자동 생성
- traceability link 자동 생성

## Phase 5. Enterprise Hardening

- 권한 / 감사 / 이력 / 인터페이스 / 배치 반영
- 비기능 요구사항과 배포 구조 반영
- 실제 고객사 적용 가이드 정리

## 지금 바로 다음 작업

1. 샘플 프로젝트에서 `screen inventory`, `dataset contract`, `transaction map`을 뽑는다.
2. 샘플의 화면 중심 이름을 canonical MES 관점으로 일반화한다.
3. 타깃 산출물 템플릿에 샘플 결과를 한 번 넣어본다.
4. 그 뒤에야 parser나 scaffold 자동화를 붙인다.

