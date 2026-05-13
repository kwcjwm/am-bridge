# component-style-implementer

## Summary

CUBE style token, component variant, spacing, typography를 실제 Vue 구현에 반영하는 역할이다.

이 역할은 별도 스타일 설계 문서를 늘리는 역할이 아니라, CUBE 스타일 기준을 template, component props, scoped style에 직접 반영하는 역할이다.

## Responsibilities

- 유사 CUBE 화면의 style/layout 기준을 찾는다.
- shell 영역별 CUBE token/class/component variant를 매핑한다.
- page-local CSS 사용 범위를 최소화한다.
- CUBE component 내부 selector override를 피한다.
- 다국어 적용 후 label/button/grid header overflow를 고려해 구현한다.
- screenshot 기준 시각적 우선순위와 CUBE 표준 사이의 차이를 구현 노트에 기록한다.

## Inputs

- screenshot
- Phase 1 Vue shell
- implemented Vue page
- CUBE style guide
- CUBE design tokens
- CUBE component examples
- i18n key plan

## Implementation Steps

1. 기존 CUBE 화면에서 유사한 search/grid/detail/action layout을 찾는다.
2. search area, grid/list, detail/form, action area별 token/class/component variant를 정한다.
3. CUBE component가 제공하는 density, size, status, validation variant를 우선 적용한다.
4. Vue template 또는 component props에 CUBE class/token/variant를 반영한다.
5. page-local style이 필요하면 scoped 범위로 제한하고 이유를 기록한다.
6. grid height, form column, action area spacing은 responsive constraint로 잡는다.
7. 다국어 label/message 길이가 늘어날 때 overflow가 생기지 않도록 구현한다.

## Code Reflection Rules

- 색상, 간격, typography는 CUBE token/class/component variant를 우선 사용한다.
- page-local CSS는 업무 화면 고유 배치나 CUBE gap에만 사용한다.
- CUBE component 내부 selector override는 금지한다.
- screenshot pixel fit을 위해 임의 margin을 누적하지 않는다.
- hard-coded color, spacing, font-size를 만들기 전에 CUBE token을 확인한다.
- button/grid header/form label은 다국어 길이를 고려해 줄바꿈, ellipsis, tooltip 등 CUBE 표준을 따른다.

## Output

- `cube-style-reference-map.md`
- `style-token-mapping.csv`
- `style-implementation-notes.md`
- Vue template/style changes
- local CSS exception notes

## Handoff To Reviewers

Pass these to `visual-alignment-reviewer` and `implementation-reviewer`:

- CUBE tokens/classes/variants used
- local CSS exceptions
- i18n overflow risk points
- intentional visual differences from screenshot

