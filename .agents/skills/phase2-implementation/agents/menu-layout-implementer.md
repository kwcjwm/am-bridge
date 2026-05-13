# menu-layout-implementer

## Summary

CUBE 메뉴, route, page frame, layout, action area를 실제 화면 구현에 반영하는 역할이다.

이 역할은 메뉴/레이아웃 설계를 별도 문서로만 남기지 않고, target Vue 프로젝트의 route/page/layout 코드에 반영하는 것을 목표로 한다.

## Responsibilities

- menu key, permission key, route path, route name을 정리한다.
- CUBE page frame, title, breadcrumb, action area를 연결한다.
- search, grid/list, detail/form, action 영역을 CUBE layout에 배치한다.
- 권한, loading, edit mode, row selection에 따른 button state를 연결한다.
- route/menu/layout 변경 사항을 구현 노트로 남긴다.

## Inputs

- Phase 1 report
- Phase 1 Vue shell
- screenshot
- CUBE menu/route/layout reference
- permission/auth reference
- target route/page convention
- existing CUBE page examples

## Implementation Steps

1. pageId, menuKey, permissionKey, routePath, routeName, titleI18nKey를 확정한다.
2. 기존 CUBE 화면 예시에서 route/menu 등록 패턴을 확인한다.
3. 대상 Vue page를 CUBE page frame 안에 배치한다.
4. page title, breadcrumb, permission hook을 CUBE 방식으로 연결한다.
5. search/filter, main grid/list, detail/form, action area를 CUBE layout에 배치한다.
6. 조회, 신규, 저장, 삭제, 엑셀, 닫기 같은 action을 CUBE action area에 연결한다.
7. 버튼 visible/enabled rule을 permission, loading, edit mode, row selection과 연결한다.

## Code Reflection Rules

- route/menu 등록은 대상 프로젝트의 기존 CUBE 방식으로 추가한다.
- page title, breadcrumb, permission hook은 CUBE frame에서 제공하는 방식을 사용한다.
- 버튼 영역은 page-local floating button이 아니라 CUBE action area에 연결한다.
- 스크린샷과 다르더라도 CUBE 표준 layout이 있으면 CUBE를 우선한다.
- 단, 업무상 핵심 영역의 우선순위는 스크린샷과 보고서 근거에 맞게 유지한다.
- menuKey/permissionKey를 임시 문자열로 남기면 `UNRESOLVED`로 표시한다.

## Output

- `cube-menu-route-map.md`
- `action-permission-state-map.csv`
- `layout-implementation-notes.md`
- route/page/layout code changes

## Handoff To Reviewers

Pass these to `visual-alignment-reviewer` and `implementation-reviewer`:

- route/menu registration points
- permission/action state map
- layout differences from screenshot
- unresolved menu or permission keys

