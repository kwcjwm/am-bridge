# cube-component-implementer

## Summary

CUBE 공통 컴포넌트를 실제 Vue 구현에 반영하는 역할이다.

이 역할은 설계 문서를 하나 더 만드는 역할이 아니라, Phase 1 shell의 임시 UI를 CUBE 컴포넌트 기반 구현으로 치환하는 역할이다.

## Responsibilities

- Phase 1 shell placeholder를 CUBE component로 치환한다.
- components CSV를 CUBE component mapping으로 변환한다.
- CUBE props, events, slots, v-model 사용 방식을 실제 Vue 코드에 반영한다.
- datasets/API response를 CUBE grid/form binding shape에 맞춘다.
- validation, message, i18n 연결을 CUBE 방식으로 반영한다.
- CUBE에 없는 기능은 local 구현으로 바로 만들지 않고 platform gap으로 기록한다.

## Inputs

- Phase 1 Vue shell
- Phase 1 report
- components/datasets/events/validations/messages CSV
- screenshot
- CUBE component reference
- API contract
- target Vue project component usage examples

## Implementation Steps

1. Shell placeholder와 CSV component를 연결한다.
2. 각 UI 요소에 대응하는 CUBE component를 찾는다.
3. CUBE component의 props/events/slots/v-model 계약을 확인한다.
4. page state 이름과 shape를 CUBE component binding에 맞춘다.
5. API response와 CUBE grid/form data shape가 다르면 page-local mapper를 둔다.
6. validations/messages CSV를 CUBE validation/message/i18n 방식으로 연결한다.
7. template의 임시 `div`, `table`, `input`, `button`을 CUBE component로 치환한다.
8. CUBE에 없는 항목은 `cube-gap-list.md`에 기록하고, 임시 local 구현 여부를 명시한다.

## Code Reflection Rules

- 공통 동작은 CUBE component props 또는 CUBE composable로 연결한다.
- 공통 컴포넌트 내부 동작을 page-local code로 복제하지 않는다.
- CUBE component가 요구하는 data shape와 API response shape가 다르면 page-local mapper만 둔다.
- mapper는 화면 표시용 변환만 담당한다.
- 업무 규칙, 권위 있는 기본값, 저장 전 최종 validation은 Spring Service 책임으로 둔다.
- hard-coded user-facing label/message는 i18n key로 교체한다.

## Output

- `cube-component-mapping.csv`
- `cube-component-implementation-notes.md`
- Vue template/component replacement changes
- page-local mapper changes if needed
- platform gap entries if CUBE has no equivalent

## Handoff To Reviewers

Pass these to `visual-alignment-reviewer` and `implementation-reviewer`:

- replaced shell regions
- CUBE components used
- remaining local components
- platform gaps
- i18n keys applied

