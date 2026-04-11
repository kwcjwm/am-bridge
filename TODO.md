# TODO

이 문서는 `am-bridge`의 실행 기준 TODO다.
목표는 "누락 없이 F/E 전환 분석 체계를 준비하고, 이후 구현을 순서대로 진행할 수 있게 하는 것"이다.

## 현재 상태

- [x] 저장소 목적 / 범위 / 비범위 정의
- [x] 외부 지원 워크스페이스와 내부 단일모델 반입 번들 역할 분리
- [x] 공통 플랫폼 경계 정의
- [x] 범용 MES canonical domain 초안 정의
- [x] F/E 전환 상세 분석 항목 정의
- [x] OI / Vision 누락 항목 보강
- [x] 기본 분석 산출물 템플릿 일부 작성
- [x] 분석 산출물 템플릿 전체 세트 1차 완성
- [x] `UI Shell First`와 `Behavior / Contract Lock` 이중 레인 운영모델 문서화
- [x] 중간 모델 스키마 초안 작성
- [x] 분석기별 입출력 스펙 초안 작성
- [x] 분석기 구현 착수
- [x] 2차 분석기 및 페이지 명세 생성기 1차 구현
- [x] 3차 OI / Vision 분석기 1차 구현
- [x] 4차 UI semantics 분석기 1차 구현

## 1. 필수 문서 기준선

- [x] [README.md](/c:/workspace/am-bridge/README.md) 정리
- [x] [docs/context.md](/c:/workspace/am-bridge/docs/context.md) 정리
- [x] [docs/architecture.md](/c:/workspace/am-bridge/docs/architecture.md) 정리
- [x] [docs/platform-boundary.md](/c:/workspace/am-bridge/docs/platform-boundary.md) 정리
- [x] [docs/frontend-conversion-design.md](/c:/workspace/am-bridge/docs/frontend-conversion-design.md) 정리
- [x] [docs/oi-vision-component-checklist.md](/c:/workspace/am-bridge/docs/oi-vision-component-checklist.md) 정리
- [x] [docs/mes-domain-model.md](/c:/workspace/am-bridge/docs/mes-domain-model.md) 정리
- [x] [docs/ai-pro-am-workflow.md](/c:/workspace/am-bridge/docs/ai-pro-am-workflow.md) 정리
- [x] 중간 모델 JSON 스키마 문서화

완료 기준:
- 분석 범위와 비범위를 팀이 오해 없이 설명할 수 있어야 한다.
- 공통 플랫폼 제공 기능과 업무 페이지 구현 기능이 분리되어 있어야 한다.

## 2. 분석 산출물 템플릿 세트 완성

### 2-1. 기본 분석 템플릿

- [x] [templates/analysis/system-profile.yaml](/c:/workspace/am-bridge/templates/analysis/system-profile.yaml)
- [x] [templates/analysis/page-triage.yaml](/c:/workspace/am-bridge/templates/analysis/page-triage.yaml)
- [x] [templates/analysis/screen-inventory.csv](/c:/workspace/am-bridge/templates/analysis/screen-inventory.csv)
- [x] [templates/analysis/component-inventory.csv](/c:/workspace/am-bridge/templates/analysis/component-inventory.csv)
- [x] [templates/analysis/dataset-contract.yaml](/c:/workspace/am-bridge/templates/analysis/dataset-contract.yaml)
- [x] [templates/analysis/transaction-map.csv](/c:/workspace/am-bridge/templates/analysis/transaction-map.csv)
- [x] [templates/analysis/function-map.csv](/c:/workspace/am-bridge/templates/analysis/function-map.csv)
- [x] [templates/analysis/page-flow.yaml](/c:/workspace/am-bridge/templates/analysis/page-flow.yaml)
- [x] [templates/analysis/platform-dependency-map.csv](/c:/workspace/am-bridge/templates/analysis/platform-dependency-map.csv)
- [x] [templates/analysis/realtime-subscription-map.csv](/c:/workspace/am-bridge/templates/analysis/realtime-subscription-map.csv)
- [x] [templates/analysis/chart-spec.yaml](/c:/workspace/am-bridge/templates/analysis/chart-spec.yaml)
- [x] [templates/analysis/image-vision-spec.yaml](/c:/workspace/am-bridge/templates/analysis/image-vision-spec.yaml)
- [x] [templates/analysis/event-map.csv](/c:/workspace/am-bridge/templates/analysis/event-map.csv)
- [x] [templates/analysis/navigation-map.csv](/c:/workspace/am-bridge/templates/analysis/navigation-map.csv)
- [x] [templates/analysis/style-token-map.csv](/c:/workspace/am-bridge/templates/analysis/style-token-map.csv)
- [x] [templates/analysis/state-rule-map.csv](/c:/workspace/am-bridge/templates/analysis/state-rule-map.csv)
- [x] [templates/analysis/validation-rule-map.csv](/c:/workspace/am-bridge/templates/analysis/validation-rule-map.csv)

### 2-2. OI / Vision 특화 템플릿

- [x] [templates/analysis/alarm-event-map.csv](/c:/workspace/am-bridge/templates/analysis/alarm-event-map.csv)
- [x] [templates/analysis/command-action-map.csv](/c:/workspace/am-bridge/templates/analysis/command-action-map.csv)
- [x] [templates/analysis/review-workflow-spec.yaml](/c:/workspace/am-bridge/templates/analysis/review-workflow-spec.yaml)

완료 기준:
- `frontend-conversion-design.md`와 `oi-vision-component-checklist.md`에서 요구한 산출물을 모두 저장소에서 생성할 수 있어야 한다.

## 3. 타깃 산출물 템플릿 세트 완성

- [x] [templates/target/page-conversion-spec.md](/c:/workspace/am-bridge/templates/target/page-conversion-spec.md)
- [x] [templates/target/module-blueprint.yaml](/c:/workspace/am-bridge/templates/target/module-blueprint.yaml)
- [x] [templates/target/api-contract.openapi.yaml](/c:/workspace/am-bridge/templates/target/api-contract.openapi.yaml)
- [x] [templates/reports/conversion-report.md](/c:/workspace/am-bridge/templates/reports/conversion-report.md)
- [x] [templates/target/ui-shell-blueprint.yaml](/c:/workspace/am-bridge/templates/target/ui-shell-blueprint.yaml)
- [x] [templates/target/vue-page-blueprint.yaml](/c:/workspace/am-bridge/templates/target/vue-page-blueprint.yaml)
- [x] [templates/target/platform-integration-spec.yaml](/c:/workspace/am-bridge/templates/target/platform-integration-spec.yaml)

완료 기준:
- 분석 산출물에서 타깃 산출물로 자연스럽게 이어지는 체인이 있어야 한다.

## 4. 중간 모델 스키마 확정

- [x] 페이지 정규화 모델 필드 목록 확정
- [x] 컴포넌트 모델 스키마 확정
- [x] dataset 모델 스키마 확정
- [x] transaction 모델 스키마 확정
- [x] function call graph 모델 스키마 확정
- [x] OI / Vision 확장 필드 정의

권장 산출물:
- `docs/intermediate-model.md`
- `schemas/page-model.schema.json`

완료 기준:
- 각 분석기가 어떤 JSON을 입력/출력하는지 명확해야 한다.

## 5. 분석기별 입출력 스펙 작성

### 5-1. 구조 추출기

- [x] 화면 셸 분석기 스펙
- [x] 컴포넌트 트리 분석기 스펙
- [x] XML dataset 추출기 스펙
- [x] Script 블록 추출기 스펙
- [x] 이벤트 속성 추출기 스펙

### 5-2. 의미 분석기

- [x] 데이터 바인딩 분석기 스펙
- [x] transaction 분석기 스펙
- [x] 이벤트 분석기 스펙
- [x] 함수 / 호출 그래프 분석기 스펙
- [x] 상태 변화 분석기 스펙
- [x] 검증 규칙 분석기 스펙
- [x] 팝업 / 내비게이션 분석기 스펙
- [x] Grid 전용 분석기 스펙
- [x] 스타일 분석기 스펙
- [x] 메시지 분석기 스펙
- [x] 공통 플랫폼 의존 분석기 스펙

### 5-3. OI / Vision 분석기

- [x] 실시간 데이터 분석기 스펙
- [x] 차트 분석기 스펙
- [x] 이미지 / 비전 분석기 스펙
- [x] 알람 / 이벤트 스트림 분석기 스펙
- [x] 설비 / 제어 명령 분석기 스펙
- [x] Vision 판정 / 리뷰 분석기 스펙

완료 기준:
- 각 분석기마다 입력 소스, 추출 규칙, 출력 모델, 예외 케이스가 적혀 있어야 한다.

## 6. 구현 우선순위

### 6-1. 1차 구현

- [x] 화면 셸 분석기 구현
- [x] 컴포넌트 트리 분석기 구현
- [x] dataset 정의 분석기 구현
- [x] 데이터 바인딩 분석기 구현
- [x] transaction 분석기 구현
- [x] 이벤트 / 함수 분석기 구현

### 6-2. 2차 구현

- [x] Grid 전용 분석기 구현
- [x] 플랫폼 의존 분석기 구현
- [x] 페이지 전환 명세 생성기 구현

### 6-3. 3차 구현

- [x] 실시간 데이터 분석기 구현
- [x] 차트 분석기 구현
- [x] 이미지 / 비전 분석기 구현
- [x] 알람 / 이벤트 스트림 분석기 구현
- [x] 명령 액션 분석기 구현
- [x] 리뷰 워크플로 분석기 구현

### 6-4. 4차 구현

- [x] 스타일 분석기 구현
- [x] 상태 변화 분석기 구현
- [x] 검증 규칙 분석기 구현
- [x] 메시지 분석기 구현

완료 기준:
- 실제 입력 소스에서 템플릿을 자동 또는 반자동으로 채울 수 있어야 한다.

## 7. 검증 체계

- [x] [docs/verification-strategy.md](/c:/workspace/am-bridge/docs/verification-strategy.md)에 분석기 단위 테스트 전략 정의
- [x] [docs/verification-strategy.md](/c:/workspace/am-bridge/docs/verification-strategy.md)에 XML fixture 샘플 형식 정의
- [x] [docs/verification-strategy.md](/c:/workspace/am-bridge/docs/verification-strategy.md)에 Script fixture 샘플 형식 정의
- [x] [docs/verification-strategy.md](/c:/workspace/am-bridge/docs/verification-strategy.md)에 결과 비교 기준 정의
- [x] [docs/verification-strategy.md](/c:/workspace/am-bridge/docs/verification-strategy.md)에 누락 검출 체크리스트 정의

완료 기준:
- 분석기 결과의 누락률을 눈으로만 판단하지 않아야 한다.

## 8. 즉시 다음 작업

- [x] 누락 템플릿 추가
- [x] 중간 모델 스키마 문서 초안 작성
- [x] 분석기 입출력 스펙 문서 초안 작성

## 현재 마지막 점검 결과

현재 기준에서 가장 큰 남은 누락은 아래다.

- [x] `platformDependency` 모델 배열 정규화
- [x] `popup / complex-grid / platform-heavy` fixture 확장
- [x] page conversion spec 생성기에 style/state/validation/message 반영
- [x] 고객 구조합의용 `UI Shell` 레인과 템플릿 정리
- [ ] `UI Shell`과 staged contract lock을 연결하는 실제 실행 스크립트나 자동화 포인트 확정
- [ ] evidence / parity를 도입할지, 도입한다면 어떤 수준까지 도입할지 실제 현업 조건에 맞춰 결정

즉, 방향은 맞다.
이제부터는 "문서 정리"보다 "스키마와 스펙 고정"으로 넘어가야 한다.
