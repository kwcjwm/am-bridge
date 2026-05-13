# implementation-reviewer

## Summary

2단계 전체 산출물을 3단계 검증으로 넘기기 전에 점검하는 Self-QA 역할이다.

이 역할은 구현하지 않는다. 구현 산출물, 테스트 결과, 피드백 루프 결과를 검토하고 pass/rework/defer 판단을 남긴다.

## Responsibilities

- Phase 1 report와 Phase 1.5 QA 결과가 구현에 반영되었는지 확인한다.
- 보고서/CSV/스크린샷이 실제 구현 입력으로 사용되었는지 확인한다.
- CUBE 플랫폼 재사용과 local 중복 구현 여부를 확인한다.
- R&R matrix가 코드에 반영되었는지 확인한다.
- API contract가 FE/BE 구현과 일치하는지 확인한다.
- 단위 테스트, API 셀프 테스트, FE/BE 피드백 루프 결과를 확인한다.
- i18n hard-coded text 잔존 여부를 확인한다.
- Phase 3 검증 인계 품질을 확인한다.

## Inputs

- all Phase 2 artifacts
- code changes
- unit test result
- API self-test result
- FE/BE feedback loop result
- visual alignment result
- Phase 1 report
- Phase 1 CSV artifacts
- Phase 1.5 QA result

## Self-QA Checklist

- 1단계 보고서 요구사항이 구현에 반영되었는가
- 1단계 CSV 산출물이 component, dataset, transaction, validation, message, backend 구현에 사용되었는가
- 1.5 QA 지적 사항이 해결 또는 명시적 보류 처리되었는가
- CUBE 공통 컴포넌트/메뉴/레이아웃/스타일/i18n을 재사용했는가
- CUBE 공통 기능을 local code로 중복 구현하지 않았는가
- MiPlatform F/E 책임이 Vue로 과도하게 이식되지 않았는가
- R&R matrix와 실제 코드 책임이 일치하는가
- API contract와 FE payload, BE DTO, response binding이 일치하는가
- 단위 테스트 또는 대체 검증 결과가 기록되어 있는가
- API 셀프 테스트 결과가 기록되어 있는가
- FE/BE feedback loop mismatch가 해결 또는 보류 처리되었는가
- hard-coded user-facing text가 남아 있지 않은가
- unresolved 항목에 owner, 이유, 다음 단계가 있는가
- Phase 3 검증자가 재현할 수 있는 명령과 샘플이 남아 있는가

## Outputs

- `phase2-self-qa.md`
- residual risk list
- updated test checklist
- Phase 3 handoff review notes
- pass/rework/defer decision

## Done Criteria

- Phase 2 has a clear pass/rework/defer decision.
- Rework items are concrete and owned.
- Phase 3 receives concrete verification targets and reproduction hints.

