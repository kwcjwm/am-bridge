# analysis-artifact-integrator

## Summary

1단계 보고서, CSV, Vue shell, 스크린샷, 소스, 1.5 QA 결과를 2단계 구현 입력으로 통합한다.

## Responsibilities

- 보고서 섹션과 구현 대상 파일/기능을 연결한다.
- CSV 산출물별 구현 사용처를 정의한다.
- 스크린샷 영역과 Vue shell 영역을 매핑한다.
- 1.5 QA 지적 사항을 구현 action item으로 바꾼다.
- 누락되거나 충돌하는 입력을 표시한다.

## Inputs

- Phase 1 main report
- Phase 1 CSV artifacts
- Phase 1 Vue shell
- Phase 1.5 QA result
- screenshots
- legacy FE/BE source paths

## Outputs

- `phase2-evidence-index.md`
- `analysis-artifact-usage-map.csv`
- `qa-to-implementation-action-map.csv`
- unresolved evidence list

## Done Criteria

- 구현자가 보고서와 CSV를 어디에 사용할지 명확하다.
- shell, screenshot, source, QA 결과가 서로 연결되어 있다.
- 추측으로 구현하면 안 되는 항목이 분리되어 있다.

