---
name: phase2-implementation
description: Use after Phase 1 analysis/design and Phase 1.5 QA are accepted, when strengthening a Phase 1 Vue shell into implementation-grade CUBE-based Vue3/Spring Boot artifacts with FE/BE R&R redesign, API/controller contract design, i18n, unit tests, API self-tests, and FE/BE feedback loops.
---

# Phase 2 Implementation

## 목적

2단계는 1단계 분석/설계 산출물과 1.5단계 QA 결과를 바탕으로, 간이 Vue shell을 실제 구현 가능한 `Vue3 + Spring Boot + CUBE 공통 플랫폼` 구조로 강화하는 단계다.

1단계 Vue 파일은 화면 껍데기이며, 최종 구현 코드가 아니다. 2단계에서는 보고서, CSV, 스크린샷, 레거시 MiPlatform F/E, 관련 B/E 소스, CUBE 공통 기능을 모두 근거로 삼아 실제 구현 책임과 API 연결 구조를 잠근다.

## 2단계의 핵심 목표

- CUBE 공통 플랫폼 기능을 먼저 재사용한다.
- MiPlatform F/E에 몰려 있던 책임을 Vue, Spring Controller, Service, Mapper, CUBE로 재분배한다.
- Vue에서 호출할 Spring Boot API/controller 계약을 설계한다.
- 분석 보고서와 CSV 산출물을 구현 입력으로 적극 사용한다.
- 스크린샷과 Phase 1 shell을 기준으로 Vue shell을 구현 수준으로 강화한다.
- 다국어는 CUBE/platform i18n 체계를 사용한다.
- 단위 테스트, 간단 API 셀프 테스트, FE/BE 피드백 루프를 2단계 안에서 수행한다.
- 3단계 검증으로 넘길 수 있는 구현 패키지와 검증 근거를 남긴다.

## 필수 입력

- 1단계 메인 분석/설계 보고서
- 1단계 상세 CSV 산출물
- 1단계 Vue shell
- 1단계 test checklist
- 1.5단계 QA 결과
- 레거시 MiPlatform F/E 소스
- 관련 B/E 소스
- 화면 스크린샷 또는 실행 캡처
- CUBE 컴포넌트/스타일/API/i18n 참조
- 대상 프로젝트의 Vue3/Spring Boot 코드 규칙
- 기존 테스트 실행 방식

## Reference 읽기 순서

1. `references/WORKFLOW.md`
2. `references/implementation-contract.md`
3. `references/cube-platform-adoption-guide.md`
4. `references/i18n-contract.md`
5. `references/cube-component-implementation-harness.md`
6. `references/cube-menu-layout-implementation-harness.md`
7. `references/cube-style-implementation-harness.md`
8. `references/test-and-feedback-loop-contract.md`
9. `references/sub-agent-usage-guide.md`
10. `references/output-checklist.md`

## 핵심 규칙

- MiPlatform F/E 책임을 그대로 Vue로 이식하지 않는다.
- CUBE가 제공하는 기능은 로컬로 재구현하지 않는다.
- Vue는 화면 상태, 사용자 상호작용, CUBE 컴포넌트 조합, API 호출 타이밍을 담당한다.
- Spring Boot는 API 경계, 권위 있는 validation, 비즈니스 규칙, 저장/조회 orchestration을 담당한다.
- API/controller 계약은 본격 Vue 구현 전에 먼저 잠근다.
- i18n은 CUBE/platform 다국어 체계를 사용한다.
- 구현 결정은 보고서, CSV, QA 결과, 스크린샷, 소스, CUBE 참조, PM 결정 중 하나로 추적 가능해야 한다.
- 테스트는 별도 3단계로 미루지 않고, 2단계에서 최소 단위 테스트와 API 셀프 테스트까지 수행한다.

## 주요 산출물

- 분석 산출물 통합 인덱스
- CUBE 사용 맵
- CUBE 공통 컴포넌트 반영 맵
- CUBE 메뉴/route/layout 반영 맵
- CUBE style/token 반영 맵
- FE/BE/CUBE R&R 매트릭스
- API/controller 계약서
- Vue shell 강화 계획
- 구현 수준 Vue3 코드
- Spring Boot controller/service/DTO/mapper 변경 또는 설계
- i18n key inventory
- 단위 테스트 결과
- API 셀프 테스트 결과
- FE/BE 피드백 루프 결과
- 갱신된 test checklist
- 3단계 검증 인계 노트
