# MES Domain Model

## 왜 도메인 기준이 먼저 필요한가

운영 중인 대형 MES는 화면 수나 코드 양보다 데이터 흐름과 업무 경계가 더 중요하다.
따라서 레거시 화면명이나 controller 명칭을 그대로 따라가기보다, 먼저 범용 Smart Factory / MES 도메인으로 정규화할 기준이 필요하다.

## 권장 canonical domain

### 1. Master Data

- plant
- site
- area
- line
- work-center
- equipment
- operation
- route
- process-spec
- item
- BOM
- unit
- shift
- calendar
- code / dictionary

### 2. Production Execution

- work-order
- production-order
- dispatch
- lot
- serial
- WIP
- work-result
- start / complete / hold / resume / cancel

### 3. Material and Inventory

- material
- raw-material
- semi-finished
- finished-good
- warehouse
- location
- stock
- issue / return / move / consume

### 4. Quality

- inspection-plan
- inspection-result
- defect
- nonconformance
- SPC / quality-rule
- rework / scrap / release
- vision-inspection
- review-queue
- defect-class
- judge-result
- confidence-score

### 5. Traceability

- genealogy
- lot history
- serial history
- process history
- material trace

### 6. Resource and Equipment

- equipment state
- recipe / parameter set
- tooling
- maintenance request
- downtime
- alarm / event
- equipment-signal
- heartbeat
- camera-device
- light-controller
- plc-handshake

## OI / Vision에서 자주 보는 세부 객체

아래 객체들은 일반 MES에도 포함될 수 있지만, OI / Vision 화면 설계에서는 별도로 드러나는 경우가 많다.

### OI 공통 객체

- equipment-status
- line-kpi
- alarm-history
- event-stream
- andon-state
- command-action
- recipe-download
- model-change
- track-in / track-out

### Vision 공통 객체

- inspection-image
- image-overlay
- roi
- bbox
- polygon-annotation
- review-decision
- false-call
- missed-defect
- golden-sample
- defect-gallery

### 7. Interface and Integration

- ERP interface
- POP / PLC / sensor interface
- scheduler / batch
- external master sync
- file / message integration

### 8. Cross-cutting

- user / role / authorization
- audit trail
- attachment / document
- approval / exception
- common code / localization

## 표준 use case 관점

각 기능은 가능한 한 아래 패턴 중 하나로 정리한다.

- register
- plan
- release
- dispatch
- start
- complete
- inspect
- approve
- hold
- resume
- cancel
- search
- summarize
- synchronize
- monitor
- acknowledge
- review
- relabel
- compare

## 데이터 중심 매핑 원칙

- 화면 이름보다 business object를 먼저 찾는다.
- dataset 이름보다 request / response 의미를 먼저 찾는다.
- SQL query 이름보다 use case와 aggregate를 먼저 찾는다.
- controller endpoint보다 transaction semantic을 먼저 정리한다.

## 예시

레거시에서 아래처럼 보이면:

- `ds_lot`
- `saveLotInfo.do`
- `selectLotHistory`

타깃에서는 아래처럼 정리하는 쪽이 낫다.

- `Lot`
- `LotApplicationService`
- `POST /lots`
- `GET /lots/{lotId}/history`

즉, 화면 중심 구조를 도메인 중심 구조로 바꾸는 것이 핵심이다.
