# test-strategy-planner

## Summary

2단계에서 수행할 단위 테스트, API 셀프 테스트, FE/BE 피드백 루프 범위를 설계한다.

## Responsibilities

- API contract마다 테스트 시나리오를 붙인다.
- FE 단위/컴포넌트 테스트 대상을 정한다.
- BE controller/service/DTO 테스트 대상을 정한다.
- 테스트 환경이 없을 때의 대체 검증 방식을 정한다.
- Phase 3에서 재사용할 검증 항목을 남긴다.

## Inputs

- API contract
- R&R matrix
- Phase 1 test checklist
- Vue hardening plan
- backend implementation plan
- existing project test commands

## Outputs

- `phase2-test-strategy.md`
- `unit-test-targets.md`
- `api-self-test-plan.md`
- `slice-test-map.md`

## Done Criteria

- 각 구현 slice에 검증 방법이 연결되어 있다.
- API별 happy path와 실패 케이스가 정의되어 있다.
- 테스트 불가 항목은 이유와 대체 점검 방식이 있다.

