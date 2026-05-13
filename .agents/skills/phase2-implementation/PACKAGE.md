# Phase 2 Implementation Skill Package

## Package Contents

이 패키지는 2단계 구현 하네스를 옮겨가기 위한 self-contained skill package다.

목표는 Phase 1 분석/설계와 Phase 1.5 QA 산출물을 바탕으로, CUBE 공통 플랫폼 기반 Vue3/Spring Boot 구현을 수행하는 것이다.

```text
phase2-implementation/
|-- SKILL.md
|-- PACKAGE.md
|-- agents/
|   |-- openai.yaml
|   |-- analysis-artifact-integrator.md
|   |-- implementation-readiness-reviewer.md
|   |-- cube-platform-adapter.md
|   |-- cube-component-implementer.md
|   |-- menu-layout-implementer.md
|   |-- component-style-implementer.md
|   |-- frontend-legacy-analyzer.md
|   |-- backend-legacy-analyzer.md
|   |-- rnr-architect.md
|   |-- backend-api-architect.md
|   |-- frontend-api-consumer.md
|   |-- test-strategy-planner.md
|   |-- frontend-implementation-architect.md
|   |-- implementation-planner.md
|   |-- frontend-implementer.md
|   |-- backend-implementer.md
|   |-- backend-contract-reviewer.md
|   |-- i18n-implementer.md
|   |-- unit-test-writer.md
|   |-- api-self-test-runner.md
|   |-- fe-be-feedback-loop-coordinator.md
|   |-- integration-reviewer.md
|   |-- visual-alignment-reviewer.md
|   |-- implementation-reviewer.md
|   `-- phase2-artifact-producer.md
`-- references/
    |-- WORKFLOW.md
    |-- sub-agent-usage-guide.md
    |-- implementation-contract.md
    |-- cube-platform-adoption-guide.md
    |-- cube-component-implementation-harness.md
    |-- cube-menu-layout-implementation-harness.md
    |-- cube-style-implementation-harness.md
    |-- i18n-contract.md
    |-- test-and-feedback-loop-contract.md
    `-- output-checklist.md
```

## Suggested Install Location

Copy this directory to the destination workspace:

```text
.agents/skills/phase2-implementation/
```

## Usage

Use this skill after Phase 1 analysis/design and Phase 1.5 QA are accepted.

Primary trigger:

```text
$phase2-implementation
```

## Important Concepts

- `WORKFLOW.md` is the primary operating document.
- Phase 1 report and CSV files are implementation inputs, not appendix-only documents.
- The Phase 1 Vue shell is a visual shell, not final implementation code.
- CUBE common platform features must be reused before page-local implementation.
- CUBE component, menu/layout, and style harnesses must be reflected in actual Vue route/page/component/style changes.
- Unit tests, API self-tests, and FE/BE feedback loops are part of Phase 2, not only Phase 3.

## Runtime Notes

- The `agents/*.md` files are role harnesses.
- In a single-model runtime, run each role sequentially as a focused prompt.
- In a multi-agent runtime, use `references/sub-agent-usage-guide.md` to decide which roles may run in parallel.
