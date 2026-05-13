# menu-layout-implementer

## Summary

CUBE 메뉴, route, page frame, layout, action area를 실제 화면 구현에 반영한다.

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

## Outputs

- `cube-menu-route-map.md`
- `action-permission-state-map.csv`
- `layout-implementation-notes.md`
- route/page/layout code changes

## Done Criteria

- 화면이 CUBE page frame과 route/menu 체계에 연결되어 있다.
- action area와 permission state가 CUBE 기준으로 반영되어 있다.
- layout 차이가 있으면 CUBE 표준과 screenshot 근거로 설명되어 있다.

