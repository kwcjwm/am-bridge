# 2단계 테스트와 피드백 루프 계약

## 목적

2단계는 구현만 하고 끝나는 단계가 아니다.

3단계 검증으로 넘기기 전에 구현자가 스스로 최소한의 단위 테스트, API 셀프 테스트, FE/BE 계약 루프를 수행해야 한다.

## 테스트 우선순위

1. API contract와 DTO shape 정합성
2. 대표 조회 API 동작
3. 저장성 API가 있으면 저장/수정/삭제 최소 동작
4. validation fail 처리
5. error response format
6. Vue payload 생성
7. Vue grid/detail binding
8. i18n key resolve
9. CUBE wrapper 사용 여부

## FE 단위 검증

프로젝트에 테스트 프레임워크가 있으면 기존 방식으로 테스트를 작성한다.

권장 대상:

- component render
- 주요 event handler
- validation function
- API client payload mapping
- i18n key existence
- grid/detail binding helper

테스트 프레임워크가 없으면 최소 대체 검증을 수행한다.

- type check
- lint
- build
- 주요 interaction 수동 점검 기록

## BE 단위 검증

프로젝트에 테스트 프레임워크가 있으면 기존 방식으로 테스트를 작성한다.

권장 대상:

- controller binding
- request DTO validation
- service business validation
- response DTO mapping
- error response

테스트 프레임워크가 없으면 최소 대체 검증을 수행한다.

- compile
- targeted Spring Boot test command
- API self-test로 controller binding 확인

## API 셀프 테스트

API별 최소 케이스:

- happy path
- empty result
- validation fail
- error response format
- permission/header condition
- save/update/delete success/fail if applicable

각 API 테스트 기록:

```text
API:
Method:
Endpoint:
Request sample:
Expected response:
Actual response:
Result:
Mismatch type:
Owner:
Retry:
```

## FE/BE 피드백 루프

기본 루프:

1. API contract 확인
2. Vue payload 생성 확인
3. Spring request DTO binding 확인
4. service/mapper 결과 확인
5. response DTO 확인
6. Vue grid/detail binding 확인
7. loading/empty/error/success 상태 확인
8. mismatch owner 결정
9. 수정 후 재실행

기본 반복 횟수는 2회다.

2회 이후에도 남는 문제는 보류 이슈로 넘긴다.

## Mismatch 분류

- `FE_PAYLOAD`
- `FE_BINDING`
- `BE_DTO`
- `API_CONTRACT`
- `SERVICE_RULE`
- `QUERY_RESULT`
- `CUBE_WRAPPER`
- `I18N`
- `TEST_ENV`
- `UNRESOLVED`

## 완료 기준

- 단위 테스트 또는 대체 검증 결과가 기록되어 있다.
- API 셀프 테스트 결과가 기록되어 있다.
- FE/BE mismatch가 해결 또는 보류 처리되어 있다.
- 보류 항목은 owner와 다음 단계가 명확하다.
- Phase 3 검증자가 재현할 수 있는 명령/샘플이 남아 있다.

