# am-bridge

`am-bridge`는 레거시 UI/업무 소스를 현대화할 때 사용하는 AM 작업용 워크벤치다.
현재 기준의 출발점은 `MiPlatform + eGov/Spring + iBATIS` 계열이지만, 목적은 특정 샘플이나 특정 고객사 소스에 맞춘 전용 변환기가 아니라 범용 Smart Factory / MES 환경에서 재사용 가능한 분석 기준과 산출물 체계를 만드는 것이다.

이번 저장소의 실제 전제는 "공통 플랫폼은 이미 존재하고, 그 위에 업무 페이지를 `Vue 3`로 전환한다"는 것이다.
즉 메뉴, 결재, 권한, 인증, 메일 같은 공통 기능을 새로 만드는 저장소가 아니라, 그런 공통 기능을 활용하면서 레거시 업무 화면을 페이지 단위로 현대화하는 프레임이 본체다.

또한 이 저장소는 "내부 동작을 미리 확정"하려는 목적보다, 사내 `AI Pro + GLM-4.7` 환경에서 빠르게 AM 과제를 수행할 수 있도록 외부에서 하네스와 산출물 체계를 준비하는 목적이 더 크다.
그 관점에서 `am-bridge`는 두 개의 작업 레인을 함께 지원해야 한다.

- `UI Shell First`
  고객/현업이 먼저 보는 검색영역, 그리드, 버튼, 상세영역, 팝업 진입점 같은 화면 껍데기를 조기에 고정한다.
- `Behavior / Contract Lock`
  dataset, transaction, API, validation, 저장 흐름, 예외 메시지, 권한 경계를 뒤 단계에서 정확하게 잠근다.

## 워크스페이스 분리 원칙

이 저장소의 루트는 `외부 Codex 지원 워크스페이스`다.
여기서는 고성능 모델과 서브에이전트를 사용해 내부망 반입용 하네스, 프롬프트, 툴, 검토 체계를 준비한다.

회사 내부 AI에는 이 루트 저장소를 그대로 열지 않는다.
내부망에는 export된 `내부 단일 모델 작업 워크스페이스`만 반입하고, 그 워크스페이스의 시작 문서는 내부 전용 `AGENTS.md`여야 한다.

현재 내부 반입용 시작 문서 소스는 [deploy/internal-ai/AGENTS.md](/c:/workspace/am-bridge/deploy/internal-ai/AGENTS.md) 이고, export 스크립트는 이 파일을 번들 루트의 `AGENTS.md`로 복사한다.
운영자가 실제로 따라야 할 최소 절차는 [deploy/internal-ai/operator-script.md](/c:/workspace/am-bridge/deploy/internal-ai/operator-script.md) 에 정리한다.
기본 export 경로는 `exports/internal-ai-workspace` 이다.
`artifacts/` 는 외부 지원 워크스페이스의 AM 산출물만 두고, 내부 반입용 생성 워크스페이스는 `exports/` 로 분리한다.

## 이 저장소가 하는 일

- 외부 지원 워크스페이스에서 내부 반입용 AM 하네스와 운영 절차를 준비한다.
- 레거시 자산을 읽고 구조화하는 기준을 정리한다.
- 데이터 중심 MES 도메인 기준의 canonical model 초안을 유지한다.
- 공통 플랫폼 연계를 전제로 한 `Vue 3 업무 페이지 전환` 설계 산출물 템플릿을 제공한다.
- 고객/현업 구조 합의를 빠르게 끌어내기 위한 `UI Shell First` 자산을 제공한다.
- 공개 샘플 프로젝트는 파서와 산출물 흐름을 검증하는 입력셋으로만 사용한다.

## 이 저장소가 하지 않는 일

- 특정 고객사 MES 소스를 대체 저장소처럼 보관하지 않는다.
- 공개 샘플 프로젝트에 맞춘 전용 솔루션을 만들지 않는다.
- 자동 완전 변환을 약속하는 제품처럼 동작하지 않는다.
- 운영 기업의 반출 불가 소스를 이 저장소에 직접 담지 않는다.
- 메뉴, 결재, 권한, 인증, 메일 같은 공통 플랫폼 기능을 이 저장소에서 다시 구현하지 않는다.

## 기본 방향

- `code-first`보다 `data-first`
- 납품 단위는 `page`지만 설계 기준은 `transaction / dataset / service` 중심
- 고객사 화면명 보존보다 canonical domain 정규화 우선
- 자동 생성보다 분석 근거와 추적 가능성 우선
- UI 구조 합의와 행위 계약 잠금을 분리
- 샘플 검증과 본체 설계를 분리
- 공통 플랫폼 제공 영역과 업무 전환 영역을 명확히 분리

## 저장소 구조

- `docs/`: 배경, 원칙, 아키텍처, 로드맵
- `playbooks/`: 범용 MES 도메인 지도와 레거시 분석 체크리스트
- `templates/`: 분석 산출물, 타깃 계약서, 보고서 템플릿
- `artifacts/`: 외부 지원 워크스페이스에서 생성되는 분석/계획/리포트 산출물 보관 위치
- `exports/`: 내부망으로 들고 갈 생성형 워크스페이스 export 위치
- `deploy/internal-ai/`: 내부망에 반입할 단일 모델 워크스페이스의 시작 문서 소스
- `samples/`: 공개 샘플 입력셋과 검증용 참고 자료

## 표준 작업 흐름

1. 소스 접근 제약과 반출 가능 범위를 먼저 정의한다.
2. 페이지 난이도를 분류하고 `UI Shell First`가 허용되는지 먼저 판정한다.
3. 필요하면 고객/현업 합의용 `UI Shell`과 배치 청사진을 먼저 만든다.
4. 화면, dataset, transaction, controller, service, SQL map을 인벤토리화한다.
5. 공통 플랫폼이 제공하는 기능과 업무 페이지가 직접 구현할 기능을 분리한다.
6. 레거시 명칭을 canonical domain과 use case로 정규화한다.
7. 타깃 페이지 / API / DTO / 모듈 청사진을 만들고 행위 계약을 잠근다.
8. scaffold를 생성하되, 설계 검토와 수동 보정을 전제로 둔다.
9. 산출물 간 추적성을 유지한다.

주의:

- `UI Shell`은 구조 합의용이지 동작 확정본이 아니다.
- 버튼 placeholder, `연결 예정`, `미구현` 표시는 허용하지만, 이를 완료된 기능처럼 다루면 안 된다.

## 현재 전제

- 실제 대상은 운영 중인 대형 기업 MES다.
- 고객사 소스는 반출할 수 없으므로, 이 저장소는 범용 틀과 샘플 검증을 담당한다.
- 현재 `samples/ScoreRanking_Proj-master`는 PoC 입력셋일 뿐이며, 본체 구조를 규정하지 않는다.
- 공통 플랫폼은 이미 존재하며, 업무 화면은 그 표준 위에서 `Vue 3` 페이지 단위로 전환한다.

## 시작 순서

1. [TODO.md](/c:/workspace/am-bridge/TODO.md)에서 현재 진행 기준과 누락 항목을 확인한다.
2. [docs/context.md](/c:/workspace/am-bridge/docs/context.md)에서 범위와 제약을 확인한다.
3. [docs/architecture.md](/c:/workspace/am-bridge/docs/architecture.md)에서 AM 작업 골격을 본다.
4. [docs/platform-boundary.md](/c:/workspace/am-bridge/docs/platform-boundary.md)에서 공통 플랫폼과 업무 페이지 경계를 확인한다.
5. [docs/frontend-conversion-design.md](/c:/workspace/am-bridge/docs/frontend-conversion-design.md)에서 F/E 전환 상세 분석 항목을 확인한다.
6. [docs/oi-vision-component-checklist.md](/c:/workspace/am-bridge/docs/oi-vision-component-checklist.md)에서 OI / Vision 누락 항목을 점검한다.
7. [docs/mes-domain-model.md](/c:/workspace/am-bridge/docs/mes-domain-model.md)에서 범용 MES canonical domain을 확인한다.
8. [docs/intermediate-model.md](/c:/workspace/am-bridge/docs/intermediate-model.md)에서 중간 모델 필드 기준을 확인한다.
9. [docs/analyzer-io-spec.md](/c:/workspace/am-bridge/docs/analyzer-io-spec.md)에서 분석기별 예외 / fallback 규칙을 확인한다.
10. [docs/verification-strategy.md](/c:/workspace/am-bridge/docs/verification-strategy.md)에서 fixture / assertion 기준을 확인한다.
11. [docs/ai-pro-am-workflow.md](/c:/workspace/am-bridge/docs/ai-pro-am-workflow.md)에서 내부 AI Pro 운영 흐름을 확인한다.
12. [templates/analysis/system-profile.yaml](/c:/workspace/am-bridge/templates/analysis/system-profile.yaml)과 [templates/analysis/page-triage.yaml](/c:/workspace/am-bridge/templates/analysis/page-triage.yaml)부터 현재 프로젝트 프로파일과 페이지 분류를 작성한다.
13. 구조 선고정이 필요하면 [templates/target/ui-shell-blueprint.yaml](/c:/workspace/am-bridge/templates/target/ui-shell-blueprint.yaml)으로 `UI Shell`을 만든다.
14. 타깃 설계는 [templates/target/vue-page-blueprint.yaml](/c:/workspace/am-bridge/templates/target/vue-page-blueprint.yaml)과 [templates/target/platform-integration-spec.yaml](/c:/workspace/am-bridge/templates/target/platform-integration-spec.yaml)으로 이어간다.
