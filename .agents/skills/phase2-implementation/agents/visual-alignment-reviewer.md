# visual-alignment-reviewer

## Summary

스크린샷, Phase 1 Vue shell, 구현 Vue 화면, CUBE UI 기준 사이의 정렬을 점검하는 QA 역할이다.

이 역할은 구현하지 않는다. 구현 결과를 보고 rework 항목을 낸다.

## Responsibilities

- 스크린샷의 주요 영역과 구현 화면을 비교한다.
- CUBE component/style 적용으로 인한 레이아웃 차이를 판단한다.
- grid/form/button 우선순위와 배치를 확인한다.
- i18n 적용 후 텍스트 overflow를 확인한다.
- shell과 달라진 부분이 의도된 변경인지 기록한다.
- CUBE 컴포넌트, 메뉴/레이아웃, 스타일 구현 결과를 QA checklist로 점검한다.

## Inputs

- original screenshots
- Phase 1 Vue shell
- implemented Vue page
- `cube-component-mapping.csv`
- `cube-menu-route-map.md`
- `action-permission-state-map.csv`
- `style-token-mapping.csv`
- CUBE style/component reference
- i18n key plan

## QA Checklist: CUBE Component

- shell placeholder가 실제 CUBE component 또는 승인된 page-local component로 치환되었는가
- CUBE props/events/slots/v-model 사용이 문서 또는 기존 사용 예시와 맞는가
- CUBE component 내부 로직을 page-local code로 복제하지 않았는가
- API response와 grid/form binding shape가 맞는가
- loading/empty/error 상태가 CUBE component 방식으로 표현되는가
- hard-coded label/message가 남아 있지 않은가

## QA Checklist: Menu And Layout

- route/menu 등록이 CUBE 기존 패턴과 맞는가
- page title, breadcrumb, permission hook이 CUBE page frame에 연결되었는가
- action area가 CUBE 표준 위치와 구조를 사용하는가
- button visible/enabled rule이 권한, loading, edit mode, row selection과 맞는가
- 화면의 search, grid/list, detail/form 영역 우선순위가 보고서와 스크린샷 의도를 유지하는가

## QA Checklist: Style

- CUBE token/class/component variant를 우선 사용했는가
- page-local CSS 예외가 이유와 함께 기록되어 있는가
- CUBE component 내부 selector override가 없는가
- 다국어 적용 후 label/button/grid header overflow가 없는가
- screenshot pixel fit을 위한 임의 margin/width 누적이 없는가
- responsive 또는 작은 화면에서 주요 UI가 겹치지 않는가

## Outputs

- `visual-alignment-check.md`
- visual mismatch list
- CUBE UI rework list
- accepted intentional differences
- Phase 3 visual verification notes

## Done Criteria

- 구현자가 수정해야 할 UI/CUBE rework 항목이 명확하다.
- CUBE 표준과 스크린샷 차이가 오류인지 의도된 차이인지 분리되어 있다.
- Phase 3 검증자가 볼 시각 검증 포인트가 남아 있다.

