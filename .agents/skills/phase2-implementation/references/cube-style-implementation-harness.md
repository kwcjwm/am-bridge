# CUBE 컴포넌트 스타일 구현 반영 하네스

## 목적

이 하네스는 CUBE 스타일, design token, spacing, typography, grid/form 밀도 기준을 실제 Vue 구현에 반영하는 방법을 정의한다.

2단계에서는 화면을 임의 CSS로 맞추는 것이 아니라 CUBE 스타일 체계를 우선 사용한다.

## 입력

- 스크린샷
- Phase 1 Vue shell
- CUBE style guide
- CUBE design token
- CUBE component examples
- target project CSS/SCSS convention
- i18n key plan

## 기본 규칙

- CUBE token/class/component variant를 먼저 사용한다.
- 페이지 전용 CSS는 업무 화면 고유 배치나 예외에만 사용한다.
- 공통 컴포넌트 내부 스타일을 override하지 않는다.
- 색상, 간격, typography를 임의 값으로 만들지 않는다.
- 다국어 적용 후 텍스트 길이가 늘어나는 경우를 고려한다.

## Step 1. 스타일 기준 수집

### 작업

- 기존 CUBE 화면의 유사 레이아웃을 찾는다.
- grid/form/search/action area의 표준 간격을 확인한다.
- dense 업무 화면인지, 일반 업무 화면인지 판단한다.
- button variant, status color, validation color 기준을 확인한다.

### 산출물

- `cube-style-reference-map.md`

## Step 2. Shell 영역별 Style Mapping

### 작업

- search area
- grid/list area
- detail/form area
- button/action area
- popup entry
- status/message area

각 영역에 사용할 CUBE class, token, component variant를 매핑한다.

### 산출물

- `style-token-mapping.csv`

### CSV 컬럼 예시

```text
shellRegion,cubePattern,tokenOrClass,componentVariant,localStyleAllowed,reason,sourceEvidence
```

## Step 3. Vue 코드 반영

### 작업

- CUBE class/token을 template 또는 component props에 반영한다.
- page-local style은 scoped로 제한한다.
- 반복되는 로컬 스타일은 CUBE pattern으로 치환 가능한지 다시 확인한다.
- grid height, form column, action area spacing은 responsive constraint를 둔다.

### 금지

- hard-coded color 남발
- CUBE component 내부 selector override
- screenshot pixel fit을 위한 임의 margin 누적
- 다국어 텍스트 overflow를 무시한 fixed width

## Step 4. 다국어와 화면 깨짐 점검

### 작업

- label/message 길이가 늘어날 때 layout이 깨지는지 확인한다.
- button text가 overflow 되는지 확인한다.
- grid header가 잘리는지 확인한다.
- CUBE tooltip/ellipsis 기준을 적용한다.

## Step 5. 구현 반영 점검

### 체크

- CUBE token/class/component variant를 사용했는가
- 로컬 CSS가 필요한 이유가 기록되어 있는가
- 스크린샷의 주요 배치 의도를 유지하는가
- 다국어 적용 후 텍스트 overflow가 없는가
- 공통 스타일을 로컬에서 재정의하지 않았는가

### 산출물

- `cube-style-reference-map.md`
- `style-token-mapping.csv`
- `style-implementation-notes.md`
- visual alignment result

