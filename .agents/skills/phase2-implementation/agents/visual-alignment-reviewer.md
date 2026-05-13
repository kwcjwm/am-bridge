# visual-alignment-reviewer

## Summary

스크린샷, Phase 1 Vue shell, 구현 Vue 화면의 시각적 정렬을 점검한다.

## Responsibilities

- 스크린샷의 주요 영역과 구현 화면을 비교한다.
- CUBE component/style 적용으로 인한 레이아웃 차이를 판단한다.
- grid/form/button 우선순위와 배치를 확인한다.
- i18n 적용 후 텍스트 overflow를 확인한다.
- shell과 달라진 부분이 의도된 변경인지 기록한다.

## Inputs

- original screenshots
- Phase 1 Vue shell
- implemented Vue page
- CUBE style/component reference
- visual alignment plan

## Outputs

- `visual-alignment-check.md`
- visual mismatch list
- accepted intentional differences
- rework recommendations

## Done Criteria

- 중요한 화면 영역의 위치와 우선순위가 확인되어 있다.
- CUBE 적용으로 인한 합리적 차이와 실제 오류가 분리되어 있다.
- Phase 3 검증자가 볼 시각 검증 포인트가 남아 있다.

