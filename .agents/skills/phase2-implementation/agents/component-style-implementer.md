# component-style-implementer

## Summary

CUBE style token, component variant, spacing, typography를 실제 Vue 구현에 반영한다.

## Responsibilities

- 유사 CUBE 화면의 style/layout 기준을 찾는다.
- shell 영역별 CUBE token/class/component variant를 매핑한다.
- page-local CSS 사용 범위를 최소화한다.
- 다국어 적용 후 label/button/grid header overflow를 점검한다.
- screenshot 기준 시각적 우선순위와 CUBE 표준 사이의 차이를 기록한다.

## Inputs

- screenshot
- Phase 1 Vue shell
- implemented Vue page
- CUBE style guide
- CUBE design tokens
- CUBE component examples
- i18n key plan

## Outputs

- `cube-style-reference-map.md`
- `style-token-mapping.csv`
- `style-implementation-notes.md`
- visual/style verification notes

## Done Criteria

- 색상, 간격, typography가 CUBE 기준을 따른다.
- local CSS가 필요한 항목은 이유와 범위가 명확하다.
- 다국어와 responsive 상태에서 UI가 깨지지 않는다.

