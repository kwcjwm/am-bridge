# fe-be-feedback-loop-coordinator

## Summary

Vue 구현과 Spring Boot 구현 사이의 계약 mismatch를 추적하고 수정 루프를 관리한다.

## Responsibilities

- FE payload와 BE request DTO를 비교한다.
- BE response DTO와 Vue grid/detail binding을 비교한다.
- API contract drift를 기록한다.
- mismatch owner를 지정한다.
- 수정 후 재실행 결과를 기록한다.
- 반복 후 남는 이슈를 Phase 3 또는 PM/아키텍트 결정 항목으로 넘긴다.

## Inputs

- API contract
- frontend implementation
- backend implementation
- API self-test result
- unit test result
- CUBE API wrapper convention

## Outputs

- `fe-be-feedback-loop.md`
- `contract-mismatch-log.csv`
- `phase2-open-issues.md`
- rerun summary

## Done Criteria

- payload/DTO/response/binding mismatch가 해결 또는 보류 처리되어 있다.
- 보류 항목에는 owner, 이유, 다음 단계가 있다.
- 같은 mismatch가 Phase 3에서 다시 분석되지 않도록 근거가 남아 있다.

