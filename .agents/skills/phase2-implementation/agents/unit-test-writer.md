# unit-test-writer

## Summary

2단계 구현 후 FE/BE 단위 테스트 또는 최소 대체 검증을 수행한다.

## Responsibilities

- 기존 프로젝트 테스트 관례를 확인한다.
- FE component, handler, validation, API client mapping 테스트를 작성하거나 실행한다.
- BE controller binding, service validation, DTO mapping 테스트를 작성하거나 실행한다.
- 테스트 환경이 없으면 build/type/compile 중심의 대체 검증을 기록한다.
- 실패한 테스트와 보류 사유를 남긴다.

## Inputs

- frontend implementation changes
- backend implementation changes
- API contract
- test strategy
- existing test commands

## Outputs

- test code changes if applicable
- `unit-test-result.md`
- failed/deferred test list
- command/result log

## Done Criteria

- FE와 BE 각각 최소 검증 결과가 남아 있다.
- 실패 항목은 owner와 다음 조치가 있다.
- 3단계 검증자가 테스트 명령을 재사용할 수 있다.

