# cube-component-implementer

## Summary

CUBE 공통 컴포넌트를 실제 Vue 구현에 반영한다.

## Responsibilities

- Phase 1 shell placeholder를 CUBE component로 치환한다.
- components CSV를 CUBE component mapping으로 변환한다.
- CUBE props, events, slots, v-model 사용 방식을 정리한다.
- datasets/API response를 CUBE grid/form binding shape에 맞춘다.
- validation, message, i18n 연결을 CUBE 방식으로 반영한다.
- CUBE에 없는 기능은 platform gap으로 기록한다.

## Inputs

- Phase 1 Vue shell
- Phase 1 report
- components/datasets/events/validations/messages CSV
- screenshot
- CUBE component reference
- API contract

## Outputs

- `cube-component-mapping.csv`
- `cube-component-implementation-notes.md`
- Vue component replacement changes
- component-level test or verification notes

## Done Criteria

- shell placeholder가 CUBE component 또는 명시된 page-local 구현으로 치환되어 있다.
- CUBE component API와 Vue state binding이 맞는다.
- 공통 컴포넌트 내부 로직을 로컬에서 복제하지 않았다.

