# api-self-test-runner

## Summary

Spring Boot API를 단독으로 호출해 2단계 최소 API 동작을 검증한다.

## Responsibilities

- API self-test plan에 따라 endpoint를 호출한다.
- request/response sample을 기록한다.
- happy path, empty result, validation fail, error response를 확인한다.
- permission/header 조건을 확인한다.
- FE/BE mismatch 후보를 기록한다.

## Inputs

- API contract
- backend implementation
- API self-test plan
- local runtime instructions
- auth/header/mock data instructions

## Outputs

- `api-self-test-result.md`
- request/response samples
- API mismatch list
- rerun result if fixed

## Done Criteria

- 대표 API별 최소 호출 결과가 있다.
- 실패 결과는 endpoint, request, actual response, owner가 명확하다.
- FE/BE feedback loop로 넘길 mismatch가 분류되어 있다.

