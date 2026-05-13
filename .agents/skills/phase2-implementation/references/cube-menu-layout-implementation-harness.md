# CUBE 메뉴/배치 레이아웃 구현 반영 하네스

## 목적

이 하네스는 화면을 CUBE 메뉴, route, page frame, layout, action area에 실제로 연결하는 방법을 정의한다.

2단계 구현에서는 메뉴와 레이아웃을 새로 만들지 않는다.

CUBE가 제공하는 메뉴, 권한, route, breadcrumb, page title, content frame, action area, layout grid를 사용한다.

## 입력

- 1단계 보고서
- 스크린샷
- Phase 1 Vue shell
- CUBE menu/route/layout reference
- permission/auth reference
- target route convention
- target page directory convention

## Step 1. 메뉴/Route Metadata 식별

### 작업

- 대상 화면의 menu key 후보를 확인한다.
- permission key 후보를 확인한다.
- route path, route name, page title key를 정한다.
- breadcrumb 표시 기준을 확인한다.
- 화면 진입 파라미터가 있는지 확인한다.

### 산출물

- `cube-menu-route-map.md`

### 기록 항목

```text
pageId:
menuKey:
permissionKey:
routePath:
routeName:
titleI18nKey:
breadcrumb:
entryParams:
sourceEvidence:
unresolved:
```

## Step 2. CUBE Page Frame 반영

### 작업

- 대상 Vue page를 CUBE page frame 안에 배치한다.
- page title, breadcrumb, permission hook을 연결한다.
- CUBE action area가 있으면 조회/저장/삭제/닫기 버튼을 그 영역에 배치한다.
- 메뉴 권한에 따라 버튼 visible/enabled 상태를 연결한다.

### 반영 규칙

- page-local wrapper로 CUBE frame을 흉내 내지 않는다.
- route/menu 등록 방식은 대상 프로젝트 기존 화면을 따른다.
- 버튼 위치는 스크린샷보다 CUBE 표준이 우선이다. 단, 업무상 중요한 버튼 우선순위는 유지한다.

## Step 3. 화면 배치 구조 반영

### 작업

스크린샷과 shell을 기준으로 화면 영역을 CUBE layout에 배치한다.

일반 패턴:

```text
PageFrame
|-- Search / Filter Area
|-- Main Content
|   |-- Grid/List
|   `-- Detail/Form
`-- Action Area
```

화면이 master-detail이면 다음을 명시한다.

- master 영역
- detail 영역
- selection 기준
- resize/fixed 영역 여부
- scroll owner

## Step 4. 권한과 버튼 상태 반영

### 작업

- menu permission과 page action을 연결한다.
- 조회, 신규, 저장, 삭제, 엑셀, 닫기 등 action을 분류한다.
- 권한 없는 action은 CUBE 권한 처리 방식에 따른다.
- row selection, edit mode, loading 상태에 따른 disabled 조건을 정의한다.

### 산출물

- `action-permission-state-map.csv`

### CSV 컬럼 예시

```text
actionId,labelKey,cubeAction,permissionKey,visibleRule,enabledRule,handler,sourceEvidence
```

## Step 5. 구현 반영 점검

### 체크

- route/menu/page title이 CUBE 방식으로 등록되었는가
- permission key가 임시 문자열로 방치되지 않았는가
- action area가 CUBE 표준 위치를 사용하는가
- 화면 scroll과 fixed 영역이 깨지지 않는가
- breadcrumb/page title/i18n이 연결되었는가
- 스크린샷 대비 주요 업무 영역 우선순위가 유지되는가

### 산출물

- `cube-menu-route-map.md`
- `action-permission-state-map.csv`
- `layout-implementation-notes.md`
- 관련 route/page/layout 코드 변경

