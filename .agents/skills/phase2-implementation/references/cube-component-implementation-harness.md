# CUBE 공통 컴포넌트 구현 반영 하네스

## 목적

이 하네스는 CUBE 공통 컴포넌트를 "참조했다"에서 끝내지 않고, 실제 Vue 구현에 어떻게 반영할지 정의한다.

2단계에서 공통 컴포넌트는 다음 순서로 반영한다.

1. 레거시 화면 요소를 식별한다.
2. CUBE 공통 컴포넌트 후보를 찾는다.
3. props, events, slots, v-model, validation, i18n 연결 방식을 확정한다.
4. Vue shell placeholder를 CUBE 컴포넌트로 치환한다.
5. API response와 page state를 CUBE 컴포넌트 binding에 연결한다.
6. 단위 테스트 또는 최소 렌더링 검증으로 반영 결과를 확인한다.

## 입력

- 1단계 보고서
- components CSV
- datasets CSV
- events CSV
- validations/messages CSV
- Phase 1 Vue shell
- 스크린샷
- CUBE 컴포넌트 문서 또는 기존 사용 예시
- 대상 Vue 프로젝트의 component import/use 규칙

## Step 1. 화면 요소와 CUBE 컴포넌트 후보 매핑

### 작업

- shell의 영역별 placeholder를 식별한다.
- components CSV의 component ID와 화면 영역을 연결한다.
- CUBE에서 동일 목적의 컴포넌트를 찾는다.
- 동일 컴포넌트가 없으면 가장 가까운 CUBE primitive를 찾는다.
- CUBE에서도 없으면 platform gap으로 기록한다.

### 산출물

- `cube-component-mapping.csv`

### CSV 컬럼 예시

```text
legacyComponentId,shellRegion,cubeComponent,usageType,props,events,slots,vModel,pageStateKey,i18nKey,sourceEvidence,status
```

## Step 2. Props / Events / Slots 계약 확정

### 작업

각 CUBE 컴포넌트에 대해 다음을 정한다.

- 필수 props
- 선택 props
- event emit 이름
- slot 이름
- v-model 사용 여부
- disabled/readonly/loading 상태
- validation 연결 방식
- i18n label/key 연결 방식

### 반영 규칙

- CUBE 컴포넌트 API에 맞춰 page state를 조정한다.
- CUBE 컴포넌트 내부 동작을 복제하지 않는다.
- CUBE 컴포넌트가 요구하는 data shape와 API response shape가 다르면 page-local mapper를 둔다.

## Step 3. Vue Shell 치환

### 작업

Phase 1 shell의 placeholder를 CUBE 컴포넌트로 교체한다.

예시 패턴:

```vue
<template>
  <CubeSearchPanel @search="handleSearch">
    <CubeTextField
      v-model="searchForm.itemCode"
      :label="t('pages.sample.search.itemCode')"
      :disabled="loading"
    />
    <CubeDateRange
      v-model="searchForm.period"
      :label="t('pages.sample.search.period')"
    />
  </CubeSearchPanel>

  <CubeDataGrid
    :rows="rows"
    :columns="columns"
    :loading="loading"
    @row-click="handleRowClick"
  />
</template>
```

위 예시는 형식 예시다. 실제 컴포넌트명과 props는 대상 CUBE 기준을 따른다.

## Step 4. Page State와 API Binding 반영

### 작업

- datasets CSV를 기준으로 page state를 만든다.
- api-contract를 기준으로 request payload mapper를 만든다.
- response DTO를 grid/form binding shape로 변환한다.
- CUBE grid/form이 요구하는 key, row id, selection model을 맞춘다.

### 반영 위치

- page component
- composable
- API client
- mapper/helper

### 주의

mapper는 page-local 변환만 담당한다.

업무 규칙, 권위 있는 기본값, 저장 전 최종 validation은 Spring Service 책임이다.

## Step 5. Validation / Message / i18n 연결

### 작업

- validations/messages CSV의 항목을 i18n key로 매핑한다.
- UI 즉시 validation은 CUBE form validation 방식으로 연결한다.
- 서버 validation error는 CUBE error handler/message 체계로 표시한다.
- hard-coded user-facing text를 제거한다.

## Step 6. 구현 반영 점검

### 체크

- CUBE 컴포넌트 import/use 방식이 프로젝트 관례와 맞는가
- shell placeholder가 남아 있지 않은가
- props/events/slots가 CUBE 문서와 맞는가
- API response가 grid/form에 정상 binding 되는가
- loading/empty/error 상태가 CUBE 방식으로 표시되는가
- i18n key가 resolve 되는가
- 스크린샷 기준 주요 화면 우선순위가 유지되는가

### 산출물

- `cube-component-mapping.csv`
- `cube-component-implementation-notes.md`
- 관련 Vue 코드 변경
- 관련 unit/component test 또는 대체 검증 결과

