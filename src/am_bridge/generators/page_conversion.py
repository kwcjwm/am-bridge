from __future__ import annotations

from collections import defaultdict
import re

from am_bridge.models import (
    BindingModel,
    ComponentModel,
    EventModel,
    FunctionModel,
    MessageModel,
    NavigationModel,
    PageModel,
    StateRuleModel,
    TransactionModel,
    ValidationRuleModel,
)


def generate_page_conversion_spec(model: PageModel) -> str:
    domain = _infer_domain(model)
    use_cases = _infer_use_cases(model)
    vue_page_name = _derive_vue_page_name(model.pageId)
    route = _derive_route(model.pageId)
    state_strategy = (
        "페이지 로컬 reactive state + 실시간 구독 상태 분리"
        if model.realtimeSubscriptions
        else "페이지 로컬 reactive state"
    )
    components = _join_or_none(component.componentId for component in model.components)
    datasets = _join_or_none(dataset.datasetId for dataset in model.datasets)
    transactions = _join_or_none(
        f"{transaction.transactionId}({transaction.url})" for transaction in model.transactions
    )
    navigation = _join_or_none(
        f"{item.navigationType}:{item.target}" for item in model.navigation
    )
    platform_components = _join_or_none(model.platform.sharedComponentUsage)
    component_dependencies = _summarize_platform_dependencies(model)
    api_strategy = _infer_api_strategy(model)
    flow_summary = _summarize_flow(model)
    ui_rules = _build_ui_rule_summary(model)
    oi_vision_section = _build_oi_vision_section(model)
    function_names = _join_or_none(function.functionName for function in model.functions)

    lines = [
        "# 페이지 전환 명세",
        "",
        "## 기본 정보",
        "",
        f"- 페이지 ID: {model.pageId or '미정'}",
        f"- 페이지명: {model.pageName or '미정'}",
        f"- 페이지 유형: {model.pageType or 'unknown'}",
        f"- 레거시 원본 파일: {model.legacy.sourceFile or '미정'}",
        f"- 업무 도메인: {domain}",
        f"- 주요 유스케이스: {', '.join(use_cases) if use_cases else '미정'}",
        "",
        "## 기존 화면 구조(아스키 와이어프레임)",
        "",
        *_build_ascii_wireframe_section(model),
        "",
        "## 공통 플랫폼 연계",
        "",
        f"- 메뉴 키: {model.platform.menuKey or '플랫폼 확인 필요'}",
        f"- 권한 키: {model.platform.permissionKey or '플랫폼 확인 필요'}",
        f"- 인증 연계: {'공통 플랫폼 사용' if model.platform.permissionKey else '확인 필요'}",
        f"- 결재: {'필요' if model.platform.approvalRequired else '없음'}",
        f"- 메일: {'필요' if model.platform.mailIntegration else '없음'}",
        f"- 공통 기능 사용: {platform_components}",
        f"- 컴포넌트별 의존성: {component_dependencies}",
        "",
        "## 레거시 분석 요약",
        "",
        f"- 주요 dataset: {datasets}",
        f"- 주요 transaction: {transactions}",
        f"- 주요 함수: {function_names}",
        f"- 팝업 / 서브화면: {navigation}",
        "- 연계 controller / service / SQL: 후속 backend trace 설계 필요",
        "",
        "## Vue 페이지 설계 초안",
        "",
        f"- Vue 페이지명: {vue_page_name}",
        f"- 라우트: {route}",
        f"- 상태 관리 방식: {state_strategy}",
        f"- 주요 컴포넌트: {components}",
        f"- 입력 / 조회 / 저장 흐름: {flow_summary}",
        "",
        "## UI 규칙 요약",
        "",
        *ui_rules,
        "",
        "## API 전략",
        "",
        f"- 기존 API 재사용: {api_strategy['reuse']}",
        f"- 기존 API 보정: {api_strategy['adapt']}",
        f"- 신규 API 필요: {api_strategy['new']}",
        f"- 공통 플랫폼 API 연계: {api_strategy['platform']}",
        "",
        "## 상세 분석",
        "",
        *_build_dataset_section(model),
        "",
        *_build_component_section(model),
        "",
        *_build_transaction_section(model),
        "",
        "## 함수 호출 연계",
        "",
        *_build_function_linkage_section(model),
        "",
        "## 이벤트 / 시나리오 흐름",
        "",
        *_build_event_section(model),
        "",
        "## 함수별 슈도코드",
        "",
        *_build_function_pseudocode_section(model),
        "",
        "## R&R 정의",
        "",
        *_build_rr_section(model),
    ]

    if oi_vision_section:
        lines.extend(["", "## OI / Vision 특화", "", *oi_vision_section])

    lines.extend(
        [
            "",
            "## 확인 필요 / 리스크",
            "",
            *_build_risk_section(model),
            "",
            "## 검토 체크리스트",
            "",
            f"- 권한 맵핑 누락 여부: {'권한 키 정보 존재' if model.platform.permissionKey else '권한 키 확인 필요'}",
            f"- 결재 연계 필요 여부: {'필요' if model.platform.approvalRequired else '없음'}",
            f"- 공통 기능 중복 구현 여부: {'공통 기능 재사용 우선' if model.platform.sharedComponentUsage else '추가 확인 필요'}",
            f"- 팝업/서브화면 누락 여부: {'navigation 포함' if model.navigation else '팝업/서브화면 없음 또는 확인 필요'}",
            f"- UI 규칙 누락 여부: {'UI 규칙 요약 존재' if ui_rules else '후속 확인 필요'}",
        ]
    )
    return "\n".join(lines)


def _build_ascii_wireframe_section(model: PageModel) -> list[str]:
    if not model.components:
        return [
            "```text",
            "+------------------------------------------------------------+",
            f"| PAGE {model.pageId or 'unknown'}".ljust(61) + "|",
            "|".ljust(61) + "|",
            "| 컴포넌트 없음".ljust(61) + "|",
            "+------------------------------------------------------------+",
            "```",
        ]

    bindings_by_component: dict[str, list[BindingModel]] = defaultdict(list)
    for binding in model.bindings:
        if binding.componentId:
            bindings_by_component[binding.componentId].append(binding)

    page_width = _page_metric(model, "width")
    page_height = _page_metric(model, "height")
    rows = _group_components_by_row(model.components)

    frame_width = 126
    content_width = frame_width - 2
    wireframe_lines = [
        "+" + "-" * content_width + "+",
        "|" + _center_text(f"PAGE {model.pageId or 'unknown'} ({page_width}x{page_height})", content_width) + "|",
        "|" + _center_text("레거시 화면을 좌표 기준으로 축약한 ASCII 와이어프레임", content_width) + "|",
        "|" + "-" * content_width + "|",
        "|" + " " * content_width + "|",
    ]

    for index, row in enumerate(rows, start=1):
        row_label = _infer_row_label(row)
        wireframe_lines.append("|" + _fit_text(f" [ROW {index:02d}] {row_label}", content_width) + "|")
        wireframe_lines.append("|" + " " * content_width + "|")
        rendered_row = _render_ascii_row(
            row=row,
            bindings_by_component=bindings_by_component,
            content_width=content_width - 2,
            page_width=page_width,
        )
        for line in rendered_row:
            wireframe_lines.append("| " + line.ljust(content_width - 2) + "|")
        wireframe_lines.append("|" + " " * content_width + "|")

    wireframe_lines.append("+" + "-" * content_width + "+")
    return ["```text", *wireframe_lines, "```"]


def _build_design_outline_section(model: PageModel) -> list[str]:
    if not model.components:
        return [
            "```text",
            f"PAGE {model.pageId or 'unknown'}",
            "(컴포넌트 없음)",
            "```",
        ]

    bindings_by_component: dict[str, list[BindingModel]] = defaultdict(list)
    for binding in model.bindings:
        if binding.componentId:
            bindings_by_component[binding.componentId].append(binding)

    width = model.layout.get("width", "") or "?"
    height = model.layout.get("height", "") or "?"
    rows = _group_components_by_row(model.components)

    lines = [
        "```text",
        f"PAGE {model.pageId or 'unknown'} ({width}x{height})",
        "",
    ]
    for index, row in enumerate(rows, start=1):
        row_top = _component_metric(row[0], "Top")
        row_components = "  ".join(
            _format_component_brief(component, bindings_by_component.get(component.componentId, []))
            for component in row
        )
        lines.append(f"ROW {index:02d} y={row_top}")
        lines.append(row_components)
        lines.append("")
    lines.append("```")
    return lines


def _render_ascii_row(
    row: list[ComponentModel],
    bindings_by_component: dict[str, list[BindingModel]],
    content_width: int,
    page_width: int,
) -> list[str]:
    if not row:
        return []

    page_width = max(page_width, 1)
    row_height = max(_component_box_height(component) for component in row)
    canvas = [[" "] * content_width for _ in range(row_height)]
    placements: list[tuple[int, int, ComponentModel]] = []
    cursor = 0

    for component in row:
        left = _component_metric(component, "Left")
        width = _component_metric(component, "Width")
        box_left = round(left / page_width * content_width)
        box_width = max(14, round(max(width, 48) / page_width * content_width))

        if box_left < cursor:
            box_left = cursor
        if box_left >= content_width - 6:
            box_left = max(content_width - 14, 0)
        if box_left + box_width > content_width:
            box_width = content_width - box_left
        if box_width < 12:
            box_width = min(max(content_width - box_left, 12), content_width)
            box_left = max(content_width - box_width, 0)

        placements.append((box_left, box_width, component))
        cursor = min(box_left + box_width + 1, content_width)

    for box_left, box_width, component in placements:
        _draw_component_box(
            canvas=canvas,
            left=box_left,
            width=box_width,
            height=row_height,
            component=component,
            bindings=bindings_by_component.get(component.componentId, []),
        )

    return ["".join(line).rstrip() for line in canvas]


def _draw_component_box(
    canvas: list[list[str]],
    left: int,
    width: int,
    height: int,
    component: ComponentModel,
    bindings: list[BindingModel],
) -> None:
    if not canvas:
        return

    max_width = len(canvas[0])
    width = min(width, max_width - left)
    if width < 4:
        return

    inner_width = width - 2
    top = 0
    bottom = height - 1

    canvas[top][left] = "+"
    canvas[top][left + width - 1] = "+"
    canvas[bottom][left] = "+"
    canvas[bottom][left + width - 1] = "+"

    for x in range(left + 1, left + width - 1):
        canvas[top][x] = "-"
        canvas[bottom][x] = "-"

    for y in range(top + 1, bottom):
        canvas[y][left] = "|"
        canvas[y][left + width - 1] = "|"

    body_height = max(height - 2, 0)
    body_lines = _build_component_wireframe_lines(component, bindings, limit=body_height)
    for index in range(body_height):
        text = body_lines[index] if index < len(body_lines) else ""
        padded = _fit_text(text, inner_width)
        for offset, character in enumerate(padded, start=1):
            canvas[top + 1 + index][left + offset] = character


def _build_component_wireframe_lines(
    component: ComponentModel,
    bindings: list[BindingModel],
    limit: int,
) -> list[str]:
    detail = _infer_component_brief_detail(component, bindings)
    component_type = component.componentType.lower()
    handlers = _extract_component_handlers(component)
    lines = [component.componentId, f"{component.componentType} / {detail}"]

    if handlers:
        lines.append(_format_handler_brief(handlers))

    if component_type == "grid":
        grid_meta = component.properties.get("gridMeta", {})
        columns = [
            column.get("columnName")
            for column in grid_meta.get("bodyColumns", [])
            if column.get("columnName")
        ]
        if columns:
            lines.append(f"cols: {_take(columns, limit=3)}")
        dataset_name = str(component.properties.get("BindDataset", "")).strip()
        if dataset_name:
            lines.append(f"dataset: {dataset_name}")
    elif component_type == "div":
        lines.append("embedded view area")
        lines.append("target: dynamic or popup-linked")
    elif component_type == "combo":
        lines.append("selection input")
        lines.append(f"dataset: {_join_or_none(sorted({binding.datasetId for binding in bindings if binding.datasetId}))}")
    elif component_type == "button":
        lines.append("action trigger")
    elif component_type in {"edit", "maskedit", "textarea"}:
        lines.append("input field")

    if limit <= 0:
        return []
    return lines[:limit]


def _component_box_height(component: ComponentModel) -> int:
    component_type = component.componentType.lower()
    if component_type in {"grid", "div", "textarea", "imageviewer", "chart"}:
        return 7
    return 5


def _infer_row_label(row: list[ComponentModel]) -> str:
    component_types = {component.componentType.lower() for component in row}
    if "grid" in component_types and "div" in component_types:
        return "결과 목록 + 서브뷰 영역"
    if "grid" in component_types:
        return "결과 목록 영역"
    if "button" in component_types or "combo" in component_types:
        return "조회 조건 / 액션 영역"
    if component_types <= {"static", "label"}:
        return "타이틀 / 안내 영역"
    return "화면 구성 영역"


def _extract_component_handlers(component: ComponentModel) -> list[str]:
    handlers: list[str] = []
    for key, value in component.properties.items():
        if key.startswith("On"):
            text = str(value).strip()
            if text:
                handlers.append(text)
    return handlers


def _format_handler_brief(handlers: list[str]) -> str:
    if not handlers:
        return ""
    if len(handlers) == 1:
        return handlers[0]
    return " / ".join(handlers[:2])


def _page_metric(model: PageModel, key: str) -> int:
    raw_value = model.layout.get(key, "")
    try:
        value = int(str(raw_value).strip())
    except ValueError:
        value = 0

    if value > 0:
        return value

    if key == "width":
        return max(
            (
                _component_metric(component, "Left") + _component_metric(component, "Width")
                for component in model.components
            ),
            default=0,
        )
    if key == "height":
        return max(
            (
                _component_metric(component, "Top") + _component_metric(component, "Height")
                for component in model.components
            ),
            default=0,
        )
    return 0


def _center_text(text: str, width: int) -> str:
    if width <= 0:
        return ""
    text = _fit_text(text, width)
    padding = width - len(text)
    left = padding // 2
    right = padding - left
    return (" " * left) + text + (" " * right)


def _fit_text(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text.ljust(width)
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def _build_dataset_section(model: PageModel) -> list[str]:
    if not model.datasets:
        return ["### Dataset", "", "- dataset 정의 없음"]

    bindings_by_dataset: dict[str, list[BindingModel]] = defaultdict(list)
    for binding in model.bindings:
        if binding.datasetId:
            bindings_by_dataset[binding.datasetId].append(binding)

    lines = ["### Dataset", ""]
    for dataset in model.datasets:
        lines.extend(
            [
                f"#### {dataset.datasetId}",
                f"- 역할: {dataset.role or 'unknown'}",
                f"- 컬럼: {_format_columns(dataset.columns)}",
                f"- 기본 레코드 수: {len(dataset.defaultRecords)}",
                f"- 사용 컨텍스트: {_join_or_none(dataset.usageContexts)}",
                f"- 연결 컴포넌트: {_join_or_none(sorted({binding.componentId for binding in bindings_by_dataset.get(dataset.datasetId, []) if binding.componentId}))}",
                f"- 입력 transaction: {_join_or_none(transaction.transactionId for transaction in model.transactions if dataset.datasetId in transaction.inputDatasets)}",
                f"- 출력 transaction: {_join_or_none(transaction.transactionId for transaction in model.transactions if dataset.datasetId in transaction.outputDatasets)}",
                f"- 읽는 함수: {_join_or_none(function.functionName for function in model.functions if dataset.datasetId in function.readsDatasets)}",
                f"- 쓰는 함수: {_join_or_none(function.functionName for function in model.functions if dataset.datasetId in function.writesDatasets)}",
                "",
            ]
        )
    return lines[:-1]


def _build_component_section(model: PageModel) -> list[str]:
    if not model.components:
        return ["### Component", "", "- 컴포넌트 정의 없음"]

    bindings_by_component: dict[str, list[BindingModel]] = defaultdict(list)
    events_by_component: dict[str, list[EventModel]] = defaultdict(list)
    for binding in model.bindings:
        if binding.componentId:
            bindings_by_component[binding.componentId].append(binding)
    for event in model.events:
        if event.sourceComponentId:
            events_by_component[event.sourceComponentId].append(event)

    lines = ["### Component", ""]
    for component in model.components:
        lines.extend(
            [
                f"#### {component.componentId}",
                f"- 유형: {component.componentType}",
                f"- 레이아웃 그룹: {component.layoutGroup or 'unknown'}",
                f"- 부모 / 컨테이너: {component.parentId or '없음'} / {component.containerPath or '루트'}",
                f"- 이벤트: {_join_or_none(f'{event.eventName}->{event.handlerFunction}' for event in events_by_component.get(component.componentId, []))}",
                f"- 바인딩: {_join_or_none(_format_binding(binding) for binding in bindings_by_component.get(component.componentId, []))}",
                f"- styleKey: {component.styleKey or '없음'}",
                f"- 플랫폼 의존: {_join_or_none(component.platformDependency)}",
                f"- 추정 역할: {_infer_component_role(component)}",
                "",
            ]
        )
    return lines[:-1]


def _build_transaction_section(model: PageModel) -> list[str]:
    if not model.transactions:
        return ["### Transaction / API", "", "- transaction 정의 없음"]

    lines = ["### Transaction / API", ""]
    for transaction in model.transactions:
        lines.extend(
            [
                f"#### {transaction.transactionId}",
                f"- 서비스 ID: {transaction.serviceId or '미정'}",
                f"- URL: {transaction.url or '미정'}",
                f"- 입력 dataset: {_join_or_none(transaction.inputDatasets)}",
                f"- 출력 dataset: {_join_or_none(transaction.outputDatasets)}",
                f"- 파라미터 표현식: {transaction.parameters or '없음'}",
                f"- callback: {transaction.callbackFunction or '없음'}",
                f"- wrapper: {transaction.wrapperFunction or '없음'}",
                f"- 해석 메모: {_describe_transaction_shape(transaction)}",
                "",
            ]
        )
    return lines[:-1]


def _build_event_section(model: PageModel) -> list[str]:
    if not model.events:
        return ["- 이벤트 정의 없음"]

    lines: list[str] = []
    for event in _ordered_events(model.events):
        lines.extend(
            [
                f"### {event.eventId}",
                f"- 트리거: {event.sourceComponentId or '페이지'} / {event.eventName}",
                f"- 핸들러: {event.handlerFunction or '미정'}",
                f"- 이벤트 유형: {event.eventType or 'unknown'}",
                f"- 효과: {_join_or_none(event.effects)}",
                f"- 흐름 요약: {_summarize_event_flow(event, model)}",
                "",
            ]
        )
    return lines[:-1]


def _build_function_linkage_section(model: PageModel) -> list[str]:
    if not model.functions:
        return ["- 함수 연계 정보 없음"]

    function_lookup = {function.functionName: function for function in model.functions}
    events_by_handler: dict[str, list[EventModel]] = defaultdict(list)
    callers_by_function: dict[str, list[str]] = defaultdict(list)
    navigation_by_function: dict[str, list[NavigationModel]] = defaultdict(list)
    state_by_function: dict[str, list[StateRuleModel]] = defaultdict(list)
    validation_by_function: dict[str, list[ValidationRuleModel]] = defaultdict(list)
    messages_by_function: dict[str, list[MessageModel]] = defaultdict(list)
    transactions_by_id = {transaction.transactionId: transaction for transaction in model.transactions}

    for event in model.events:
        if event.handlerFunction:
            events_by_handler[event.handlerFunction].append(event)

    for function in model.functions:
        for called_name in function.callsFunctions:
            callers_by_function[called_name].append(f"FUNC:{function.functionName}")
        for transaction_id in function.callsTransactions:
            transaction = transactions_by_id.get(transaction_id)
            if transaction and transaction.callbackFunction and transaction.callbackFunction in function_lookup:
                callers_by_function[transaction.callbackFunction].append(f"TX:{transaction.transactionId}.callback")

    for item in model.navigation:
        if item.triggerFunction:
            navigation_by_function[item.triggerFunction].append(item)
    for item in model.stateRules:
        if item.sourceFunction and item.sourceFunction != "__initial__":
            state_by_function[item.sourceFunction].append(item)
    for item in model.validationRules:
        if item.sourceFunction:
            validation_by_function[item.sourceFunction].append(item)
    for item in model.messages:
        if item.sourceFunction:
            messages_by_function[item.sourceFunction].append(item)

    lines: list[str] = []
    for function in _ordered_functions(model.functions, events_by_handler):
        transactions = [
            transactions_by_id[transaction_id]
            for transaction_id in function.callsTransactions
            if transaction_id in transactions_by_id
        ]
        linkage_tree = _render_function_linkage_tree(
            function=function,
            events=events_by_handler.get(function.functionName, []),
            caller_links=sorted(set(callers_by_function.get(function.functionName, []))),
            called_functions=[function_lookup[name] for name in function.callsFunctions if name in function_lookup],
            transactions=transactions,
            navigation=navigation_by_function.get(function.functionName, []),
            state_rules=state_by_function.get(function.functionName, []),
            validation_rules=validation_by_function.get(function.functionName, []),
            messages=messages_by_function.get(function.functionName, []),
        )
        lines.extend(
            [
                f"### {function.functionName}",
                f"- 호출 주체: {_join_or_none(_format_caller_label(value) for value in callers_by_function.get(function.functionName, []))}",
                f"- 직접 연결 이벤트: {_join_or_none(f'{event.sourceComponentId}.{event.eventName}' for event in events_by_handler.get(function.functionName, []))}",
                f"- 직접 하위 함수: {_join_or_none(function.callsFunctions)}",
                f"- 직접 하위 transaction: {_join_or_none(transaction.transactionId for transaction in transactions)}",
                f"- 직접 navigation: {_join_or_none(f'{item.navigationType}:{item.target}' for item in navigation_by_function.get(function.functionName, []))}",
                "",
                "```text",
                *linkage_tree,
                "```",
                "",
            ]
        )
    return lines[:-1]


def _build_function_pseudocode_section(model: PageModel) -> list[str]:
    if not model.functions:
        return ["- 함수 정의 없음"]

    function_lookup = {function.functionName: function for function in model.functions}
    events_by_handler: dict[str, list[EventModel]] = defaultdict(list)
    navigation_by_function: dict[str, list[NavigationModel]] = defaultdict(list)
    state_by_function: dict[str, list[StateRuleModel]] = defaultdict(list)
    validation_by_function: dict[str, list[ValidationRuleModel]] = defaultdict(list)
    messages_by_function: dict[str, list[MessageModel]] = defaultdict(list)
    transactions_by_id = {transaction.transactionId: transaction for transaction in model.transactions}

    for event in model.events:
        if event.handlerFunction:
            events_by_handler[event.handlerFunction].append(event)
    for item in model.navigation:
        if item.triggerFunction:
            navigation_by_function[item.triggerFunction].append(item)
    for item in model.stateRules:
        if item.sourceFunction and item.sourceFunction != "__initial__":
            state_by_function[item.sourceFunction].append(item)
    for item in model.validationRules:
        if item.sourceFunction:
            validation_by_function[item.sourceFunction].append(item)
    for item in model.messages:
        if item.sourceFunction:
            messages_by_function[item.sourceFunction].append(item)

    lines: list[str] = []
    for function in _ordered_functions(model.functions, events_by_handler):
        transactions = [
            transactions_by_id[transaction_id]
            for transaction_id in function.callsTransactions
            if transaction_id in transactions_by_id
        ]
        pseudocode_steps = _render_function_pseudocode(
            function=function,
            called_functions=[function_lookup[name] for name in function.callsFunctions if name in function_lookup],
            events=events_by_handler.get(function.functionName, []),
            transactions=transactions,
            navigation=navigation_by_function.get(function.functionName, []),
            state_rules=state_by_function.get(function.functionName, []),
            validation_rules=validation_by_function.get(function.functionName, []),
            messages=messages_by_function.get(function.functionName, []),
        )

        lines.extend(
            [
                f"### {function.functionName}",
                f"- 분류: {function.functionType or 'unknown'}",
                f"- 연결 이벤트: {_join_or_none(f'{event.sourceComponentId}.{event.eventName}' for event in events_by_handler.get(function.functionName, []))}",
                f"- 파라미터: {_join_or_none(function.parameters)}",
                f"- 읽는 dataset: {_join_or_none(function.readsDatasets)}",
                f"- 쓰는 dataset: {_join_or_none(function.writesDatasets)}",
                f"- 제어 컴포넌트: {_join_or_none(function.controlsComponents)}",
                f"- 호출 함수: {_join_or_none(function.callsFunctions)}",
                f"- 호출 transaction: {_join_or_none(transaction.transactionId for transaction in transactions)}",
                f"- navigation: {_join_or_none(f'{item.navigationType}:{item.target}' for item in navigation_by_function.get(function.functionName, []))}",
                f"- validation: {_join_or_none(f'{item.targetField}:{item.validationType}' for item in validation_by_function.get(function.functionName, []))}",
                "",
                "```text",
                *pseudocode_steps,
                "```",
                "",
            ]
        )
    return lines[:-1]


def _render_function_linkage_tree(
    function: FunctionModel,
    events: list[EventModel],
    caller_links: list[str],
    called_functions: list[FunctionModel],
    transactions: list[TransactionModel],
    navigation: list[NavigationModel],
    state_rules: list[StateRuleModel],
    validation_rules: list[ValidationRuleModel],
    messages: list[MessageModel],
) -> list[str]:
    lines = [f"[FUNC] {function.functionName}({', '.join(function.parameters)})"]

    if events:
        for event in events:
            source = event.sourceComponentId or "page"
            lines.append(f"  <- [EVENT] {source}.{event.eventName}")

    if caller_links:
        for caller in caller_links:
            lines.append(f"  <- [{caller.split(':', 1)[0]}] {_format_caller_payload(caller)}")

    if validation_rules:
        for rule in validation_rules:
            lines.append(
                f"  -> [VALIDATION] {rule.targetField or 'field'} / {rule.validationType or 'custom'}"
            )
            if rule.expression:
                lines.append(f"       condition = {rule.expression}")
            if rule.message:
                lines.append(f'       failMessage = "{rule.message}"')

    if function.readsDatasets:
        lines.append(f"  -> [READ] {', '.join(function.readsDatasets)}")
    if function.writesDatasets:
        lines.append(f"  -> [WRITE] {', '.join(function.writesDatasets)}")
    if function.controlsComponents:
        lines.append(f"  -> [CONTROL] {', '.join(function.controlsComponents)}")

    if called_functions:
        for called in called_functions:
            signature = ", ".join(called.parameters)
            lines.append(f"  -> [FUNC] {called.functionName}({signature})")
            if called.callsTransactions:
                lines.append(f"       downstreamTransactions = {', '.join(called.callsTransactions)}")

    if transactions:
        for transaction in transactions:
            lines.append(f"  -> [TX] {transaction.transactionId} / {transaction.url or '미정'}")
            if transaction.inputDatasets:
                lines.append(f"       input = {', '.join(transaction.inputDatasets)}")
            if transaction.outputDatasets:
                lines.append(f"       output = {', '.join(transaction.outputDatasets)}")
            if transaction.parameters:
                lines.append(f"       params = {transaction.parameters}")
            if transaction.wrapperFunction:
                lines.append(f"       wrapper = {transaction.wrapperFunction}")
            if transaction.callbackFunction:
                lines.append(f"       callback = {transaction.callbackFunction}")

    if navigation:
        for item in navigation:
            lines.append(f"  -> [NAV] {item.navigationType} / {item.target}")
            if item.parameterBindings:
                lines.append(f"       params = {', '.join(item.parameterBindings)}")

    if state_rules:
        for rule in state_rules:
            condition = rule.triggerCondition or "always"
            lines.append(
                f"  -> [STATE] {rule.targetComponentId}.{rule.stateProperty} = {rule.targetValue!r} when {condition}"
            )

    if messages:
        for message in messages:
            target = f" -> {message.targetComponentId}" if message.targetComponentId else ""
            lines.append(f'  -> [MSG] {message.messageType}{target} / "{message.text}"')

    if function.platformCalls:
        lines.append(f"  -> [PLATFORM] {', '.join(function.platformCalls)}")

    if len(lines) == 1:
        lines.append("  -> no linked calls")
    return lines


def _format_caller_label(value: str) -> str:
    kind, payload = value.split(":", 1)
    if kind == "FUNC":
        return f"함수 {payload}"
    if kind == "TX":
        return f"transaction callback {payload}"
    return value


def _format_caller_payload(value: str) -> str:
    kind, payload = value.split(":", 1)
    if kind == "FUNC":
        return payload
    if kind == "TX":
        return payload
    return value


def _build_rr_section(model: PageModel) -> list[str]:
    lines = [
        "### FE 책임",
        f"- 화면 셸과 컴포넌트 구성: {_join_or_none(component.componentId for component in model.components)}",
        f"- dataset 바인딩 구현: {_join_or_none(f'{binding.componentId}->{binding.datasetId}' for binding in model.bindings if binding.componentId)}",
        f"- 이벤트/함수 이관: {_join_or_none(function.functionName for function in model.functions if function.functionType in {'event-handler', 'helper'})}",
        f"- 입력 검증 구현: {_join_or_none(f'{rule.targetField}:{rule.validationType}' for rule in model.validationRules)}",
        f"- 팝업/서브화면 제어: {_join_or_none(f'{item.navigationType}:{item.target}' for item in model.navigation)}",
        "",
        "### BE 책임",
        f"- API 계약 제공: {_join_or_none(f'{transaction.transactionId}:{transaction.url}' for transaction in model.transactions)}",
        f"- 응답 dataset 계약 유지: {_join_or_none(dataset.datasetId for dataset in model.datasets if any(dataset.datasetId in transaction.outputDatasets for transaction in model.transactions))}",
        f"- 공통 wrapper 해석 필요 항목: {_join_or_none(transaction.transactionId for transaction in model.transactions if _is_dynamic_transaction(transaction))}",
        "",
        "### 공통 플랫폼 책임",
        f"- 메뉴/권한/공통 기능: {_join_or_none(model.platform.sharedComponentUsage)}",
        f"- 플랫폼 키 관리: 메뉴={model.platform.menuKey or '없음'}, 권한={model.platform.permissionKey or '없음'}",
        f"- 공통 팝업/레이아웃 사용 여부: {'사용 추정' if model.navigation else '없음'}",
        "",
        "### 협의 필요 항목",
        f"- 동적 endpoint/동적 subview 해석: {_join_or_none(_collect_dynamic_points(model))}",
        f"- 메시지/i18n 정리 대상: {_join_or_none(message.text for message in model.messages if message.text)}",
        f"- 레거시 메타데이터 정리: 페이지명={model.pageName or '미정'}, formId={model.legacy.formId or '미정'}",
    ]
    return lines


def _build_risk_section(model: PageModel) -> list[str]:
    risks = _collect_risks(model)
    if not risks:
        return ["- 현재 중간모델 기준으로 즉시 눈에 띄는 추가 리스크 없음"]
    return [f"- {item}" for item in risks]


def _render_function_pseudocode(
    function: FunctionModel,
    called_functions: list[FunctionModel],
    events: list[EventModel],
    transactions: list[TransactionModel],
    navigation: list[NavigationModel],
    state_rules: list[StateRuleModel],
    validation_rules: list[ValidationRuleModel],
    messages: list[MessageModel],
) -> list[str]:
    header = f"function {function.functionName}({', '.join(function.parameters)})"
    lines = [f"{header}:"]

    if events:
        event_descriptions = ", ".join(
            f"{event.sourceComponentId}.{event.eventName}" for event in events if event.sourceComponentId
        )
        if event_descriptions:
            lines.append(f"  trigger = {event_descriptions}")

    if validation_rules:
        for rule in validation_rules:
            lines.append(f"  validate {rule.targetField or 'field'} with {rule.validationType or 'custom'}")
            if rule.expression:
                lines.append(f"    condition = {rule.expression}")
            if rule.message:
                lines.append(f'    failMessage = "{rule.message}"')

    if called_functions:
        for called in called_functions:
            lines.append(f"  call {called.functionName}()")
            if called.callsTransactions:
                lines.append(
                    f"    downstreamTransactions = {', '.join(called.callsTransactions)}"
                )

    if transactions:
        for transaction in transactions:
            lines.append(f"  call transaction {transaction.transactionId}")
            lines.append(f"    url = {transaction.url or '미정'}")
            if transaction.inputDatasets:
                lines.append(f"    inputDatasets = {', '.join(transaction.inputDatasets)}")
            if transaction.outputDatasets:
                lines.append(f"    outputDatasets = {', '.join(transaction.outputDatasets)}")
            if transaction.parameters:
                lines.append(f"    params = {transaction.parameters}")
            if transaction.callbackFunction:
                lines.append(f"    callback = {transaction.callbackFunction}")

    if state_rules:
        for rule in state_rules:
            condition = rule.triggerCondition or "always"
            lines.append(
                f"  set {rule.targetComponentId}.{rule.stateProperty} = {rule.targetValue!r} when {condition}"
            )

    if navigation:
        for item in navigation:
            if item.navigationType == "popup":
                lines.append(f"  open popup {item.target}")
            elif item.navigationType == "subview":
                lines.append(f"  assign subview target = {item.target}")
            else:
                lines.append(f"  navigate to {item.target}")
            if item.parameterBindings:
                lines.append(f"    parameters = {', '.join(item.parameterBindings)}")

    for message in messages:
        if message.messageType == "alert":
            lines.append(f'  show alert "{message.text}"')
        elif message.messageType == "confirm":
            lines.append(f'  ask confirm "{message.text}"')
        elif message.messageType == "status-text":
            lines.append(
                f'  update {message.targetComponentId or "status"} text = "{message.text}"'
            )

    if function.readsDatasets:
        lines.append(f"  read datasets = {', '.join(function.readsDatasets)}")
    if function.writesDatasets:
        lines.append(f"  write datasets = {', '.join(function.writesDatasets)}")
    if function.controlsComponents:
        lines.append(f"  control components = {', '.join(function.controlsComponents)}")
    if function.platformCalls:
        lines.append(f"  use platform features = {', '.join(function.platformCalls)}")

    if len(lines) == 1:
        lines.append("  no-op or manual review required")
    return lines


def _infer_domain(model: PageModel) -> str:
    haystack = " ".join(
        [
            model.pageId,
            model.pageName,
            *(dataset.datasetId for dataset in model.datasets),
            *(transaction.url for transaction in model.transactions),
            *(function.functionName for function in model.functions),
        ]
    ).lower()

    if any(token in haystack for token in ("image", "vision", "defect", "review", "inspection")):
        return "quality"
    if any(token in haystack for token in ("equipment", "alarm", "recipe", "heartbeat", "signal")):
        return "resource-equipment"
    if any(token in haystack for token in ("lot", "work", "order", "dispatch", "score", "scholar")):
        return "production-execution"
    return "unknown"


def _infer_use_cases(model: PageModel) -> list[str]:
    candidates: set[str] = set()
    for transaction in model.transactions:
        text = f"{transaction.serviceId} {transaction.url}".lower()
        if any(token in text for token in ("search", "list", "select", "status")):
            candidates.add("search")
        if any(token in text for token in ("save", "update", "create", "register")):
            candidates.add("register")
        if any(token in text for token in ("approve", "approval")):
            candidates.add("approve")
    for navigation in model.navigation:
        if navigation.navigationType == "popup":
            candidates.add("review")
    if model.alarmEvents:
        candidates.add("monitor")
    if model.commandActions:
        candidates.add("control")
    if model.reviewWorkflows:
        candidates.add("review")
    return sorted(candidates)


def _derive_vue_page_name(page_id: str) -> str:
    page_id = page_id or "LegacyPage"
    normalized = re.sub(r"[^A-Za-z0-9]+", " ", page_id).strip()
    parts = normalized.split()
    if not parts:
        return "LegacyPage"
    return "".join(part[:1].upper() + part[1:] for part in parts) + "Page"


def _derive_route(page_id: str) -> str:
    if not page_id:
        return "/legacy-page"
    kebab = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", page_id)
    kebab = re.sub(r"[^A-Za-z0-9]+", "-", kebab).strip("-").lower()
    return "/" + (kebab or "legacy-page")


def _infer_api_strategy(model: PageModel) -> dict[str, str]:
    if not model.transactions:
        return {
            "reuse": "없음",
            "adapt": "없음",
            "new": "확인 필요",
            "platform": "없음",
        }

    urls = ", ".join(transaction.url for transaction in model.transactions if transaction.url)
    return {
        "reuse": urls or "원본 확인 필요",
        "adapt": "응답/파라미터 구조 검토 필요",
        "new": "기존 transaction만으로 부족한 경우에만 추가",
        "platform": _join_or_none(model.platform.sharedComponentUsage),
    }


def _summarize_flow(model: PageModel) -> str:
    event_handlers = [event.handlerFunction for event in model.events if event.eventType == "lifecycle"]
    action_handlers = [event.handlerFunction for event in model.events if event.eventType == "user-action"]
    parts = []
    if event_handlers:
        parts.append(f"초기 로드: {', '.join(event_handlers)}")
    if action_handlers:
        parts.append(f"사용자 액션: {', '.join(action_handlers)}")
    if model.transactions:
        parts.append(f"주요 호출 {len(model.transactions)}건")
    if model.realtimeSubscriptions:
        parts.append(f"실시간 구독 {len(model.realtimeSubscriptions)}건")
    return " / ".join(parts) or "분석 필요"


def _build_ui_rule_summary(model: PageModel) -> list[str]:
    shared_style_tokens = sorted(
        {
            style.tokenCandidate
            for style in model.styles
            if style.tokenCandidate and style.usageScope == "shared"
        }
    )
    style_tokens = shared_style_tokens + [
        token
        for token in sorted({style.tokenCandidate for style in model.styles if style.tokenCandidate})
        if token not in shared_style_tokens
    ]
    state_targets = sorted(
        {f"{rule.targetComponentId}.{rule.stateProperty}" for rule in model.stateRules if rule.targetComponentId}
    )
    validation_types = sorted({rule.validationType for rule in model.validationRules if rule.validationType})
    message_types = sorted({message.messageType for message in model.messages if message.messageType})

    return [
        f"- 스타일: 총 {len(model.styles)}건 / 대표 토큰: {_take(style_tokens)}",
        f"- 상태 규칙: 총 {len(model.stateRules)}건 / 대상: {_take(state_targets)}",
        f"- 검증 규칙: 총 {len(model.validationRules)}건 / 유형: {_take(validation_types)}",
        f"- 메시지: 총 {len(model.messages)}건 / 유형: {_take(message_types)}",
    ]


def _build_oi_vision_section(model: PageModel) -> list[str]:
    lines: list[str] = []
    if model.realtimeSubscriptions:
        realtime_summary = ", ".join(
            f"{item.sourceType}:{item.sourceName}" for item in model.realtimeSubscriptions
        )
        lines.append(f"- 실시간 구독: {realtime_summary}")
    if model.charts:
        chart_summary = ", ".join(
            f"{item.chartId}({item.chartType}/{item.datasetId or 'dataset 미정'})"
            for item in model.charts
        )
        lines.append(f"- 차트: {chart_summary}")
    if model.imageVisionViews:
        view_summary = ", ".join(
            f"{item.viewerId}({item.viewerType}/{item.resultDatasetId or 'dataset 미정'})"
            for item in model.imageVisionViews
        )
        lines.append(f"- 이미지 / 비전 뷰: {view_summary}")
    if model.alarmEvents:
        alarm_summary = ", ".join(
            f"{item.eventStreamId}({item.refreshMode}/{item.ackFunction or 'ack 없음'})"
            for item in model.alarmEvents
        )
        lines.append(f"- 알람 스트림: {alarm_summary}")
    if model.commandActions:
        command_summary = ", ".join(
            f"{item.actionName}({item.commandTarget})" for item in model.commandActions
        )
        lines.append(f"- 제어 명령: {command_summary}")
    if model.reviewWorkflows:
        workflow_summary = ", ".join(
            f"{item.workflowId}({item.workflowType}/{item.sourceDatasetId})"
            for item in model.reviewWorkflows
        )
        lines.append(f"- 리뷰 워크플로: {workflow_summary}")
    return lines


def _summarize_platform_dependencies(model: PageModel) -> str:
    pairs = [
        f"{component.componentId}[{', '.join(component.platformDependency)}]"
        for component in sorted(model.components, key=lambda item: item.componentId)
        if component.platformDependency
    ]
    return _take(pairs)


def _format_columns(columns) -> str:
    if not columns:
        return "없음"
    return ", ".join(
        f"{column.name}({column.type or 'unknown'})"
        + (f" size={column.size}" if column.size is not None else "")
        for column in columns
    )


def _format_binding(binding: BindingModel) -> str:
    parts = [binding.bindingType or "binding", binding.datasetId]
    if binding.columnName:
        parts.append(binding.columnName)
    return ":".join(part for part in parts if part)


def _format_component_brief(component: ComponentModel, bindings: list[BindingModel]) -> str:
    detail = _infer_component_brief_detail(component, bindings)
    return f"[{component.componentId}|{component.componentType}|{detail}]"


def _infer_component_brief_detail(component: ComponentModel, bindings: list[BindingModel]) -> str:
    text = str(component.properties.get("Text", "")).strip()
    component_type = component.componentType.lower()
    dataset_ids = sorted({binding.datasetId for binding in bindings if binding.datasetId})

    if component_type == "grid":
        bind_dataset = str(component.properties.get("BindDataset", "")).strip()
        return bind_dataset or _join_or_none(dataset_ids) or "grid"
    if component_type == "combo":
        return _join_or_none(dataset_ids) if dataset_ids else (text or "combo")
    if component_type in {"static", "button", "label"} and text:
        return text
    if component_type == "div":
        return "container"
    if dataset_ids:
        return _join_or_none(dataset_ids)
    return text or component.componentType


def _group_components_by_row(components: list[ComponentModel]) -> list[list[ComponentModel]]:
    sorted_components = sorted(
        components,
        key=lambda component: (
            _component_metric(component, "Top"),
            _component_metric(component, "Left"),
            component.componentId,
        ),
    )
    rows: list[list[ComponentModel]] = []
    threshold = 36

    for component in sorted_components:
        top = _component_metric(component, "Top")
        if not rows:
            rows.append([component])
            continue
        last_row_top = _component_metric(rows[-1][0], "Top")
        if abs(top - last_row_top) <= threshold:
            rows[-1].append(component)
        else:
            rows.append([component])

    for row in rows:
        row.sort(key=lambda component: (_component_metric(component, "Left"), component.componentId))
    return rows


def _component_metric(component: ComponentModel, key: str) -> int:
    raw_value = component.properties.get(key, "0")
    try:
        return int(str(raw_value).strip())
    except ValueError:
        return 0


def _infer_component_role(component: ComponentModel) -> str:
    text = str(component.properties.get("Text", "")).strip()
    component_type = component.componentType.lower()
    if component_type == "grid":
        return "목록 / 결과 표시"
    if component_type == "button" and text:
        return f"사용자 액션 버튼({text})"
    if component_type in {"combo", "edit", "textarea"}:
        return "입력 / 조건 제어"
    if component_type in {"static", "label"}:
        return "라벨 / 안내 문구"
    if component_type == "div":
        return "서브뷰 / 컨테이너"
    return "수동 확인 필요"


def _describe_transaction_shape(transaction: TransactionModel) -> str:
    if transaction.wrapperFunction:
        return "공통 wrapper를 거치는 호출이므로 FE client 규약과 BE endpoint 해석 규칙을 함께 확인해야 한다"
    if _looks_dynamic_expression(transaction.url):
        return "URL 표현식이 동적이므로 endpoint 해석 규칙을 별도 확정해야 한다"
    if transaction.parameters and _looks_dynamic_expression(transaction.parameters):
        return "직접 endpoint 호출이지만 파라미터 조립 로직을 FE에서 명시적으로 이관해야 한다"
    if any(_looks_dynamic_dataset_reference(item) for item in [*transaction.inputDatasets, *transaction.outputDatasets]):
        return "입출력 dataset 표현식에 변수/식이 포함되어 dataset contract를 수동 확정해야 한다"
    return "직접 endpoint 호출"


def _ordered_events(events: list[EventModel]) -> list[EventModel]:
    return sorted(
        events,
        key=lambda item: (
            0 if item.eventType == "lifecycle" else 1,
            item.sourceComponentId,
            item.eventName,
        ),
    )


def _ordered_functions(
    functions: list[FunctionModel],
    events_by_handler: dict[str, list[EventModel]],
) -> list[FunctionModel]:
    def sort_key(item: FunctionModel) -> tuple[int, str]:
        linked_events = events_by_handler.get(item.functionName, [])
        if any(event.eventType == "lifecycle" for event in linked_events):
            return (0, item.functionName)
        if linked_events:
            return (1, item.functionName)
        if item.functionType == "callback":
            return (3, item.functionName)
        return (2, item.functionName)

    return sorted(functions, key=sort_key)


def _summarize_event_flow(event: EventModel, model: PageModel) -> str:
    function_lookup = {function.functionName: function for function in model.functions}
    function = function_lookup.get(event.handlerFunction)
    if function is None:
        return "핸들러 본문 추가 확인 필요"

    parts = []
    if function.callsFunctions:
        parts.append(f"하위 함수 호출: {', '.join(function.callsFunctions)}")
    if function.callsTransactions:
        parts.append(f"transaction 호출: {', '.join(function.callsTransactions)}")
    if function.controlsComponents:
        parts.append(f"컴포넌트 제어: {', '.join(function.controlsComponents)}")
    if not parts:
        parts.append("수동 확인 필요")
    return " / ".join(parts)


def _collect_dynamic_points(model: PageModel) -> list[str]:
    points: list[str] = []
    for transaction in model.transactions:
        if _is_dynamic_transaction(transaction):
            points.append(f"{transaction.transactionId}:{transaction.url}")
    for item in model.navigation:
        if _looks_dynamic_expression(item.target):
            points.append(f"{item.navigationType}:{item.target}")
    return sorted(set(points))


def _collect_risks(model: PageModel) -> list[str]:
    risks: list[str] = []
    if any(_is_dynamic_transaction(transaction) for transaction in model.transactions):
        risks.append("동적 endpoint 또는 wrapper transaction이 있어 API 계약을 별도 확정해야 한다.")
    if any(_looks_dynamic_expression(item.target) for item in model.navigation):
        risks.append("서브화면/팝업 target이 변수 또는 표현식 기반이라 route map을 수동 확정해야 한다.")
    if any(rule.validationType == "custom" for rule in model.validationRules):
        risks.append("custom validation이 있어 FE 구현 전에 업무 규칙을 다시 문서화해야 한다.")
    if model.pageName.lower() in {"new form", "form"}:
        risks.append("페이지 제목이 일반명칭이므로 전환 후 메뉴명/페이지명을 별도로 정제해야 한다.")
    if any(component.componentId.lower() == "form" for component in model.components):
        risks.append("컴포넌트/페이지 식별자 일반화 충돌 가능성이 있어 naming rule 재정의가 필요하다.")
    if any(message.messageType == "component-text" and message.text == message.targetComponentId for message in model.messages):
        risks.append("의미 없는 기본 Text 속성이 남아 있어 화면 문구와 디버그용 기본값을 구분해야 한다.")
    return risks


def _is_dynamic_transaction(transaction: TransactionModel) -> bool:
    if transaction.wrapperFunction:
        return True
    if _looks_dynamic_expression(transaction.url):
        return True
    if any(_looks_dynamic_dataset_reference(item) for item in [*transaction.inputDatasets, *transaction.outputDatasets]):
        return True
    return False


def _looks_dynamic_expression(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if any(token in text for token in ('"', "'", "+", "(", ")", " ")):
        return True
    return bool(re.fullmatch(r"[A-Za-z_]\w*", text)) and "." not in text and "::" not in text and "/" not in text


def _looks_dynamic_dataset_reference(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if text.startswith("ds_"):
        return False
    return _looks_dynamic_expression(text)


def _join_or_none(values) -> str:
    items = [value for value in values if value]
    return ", ".join(items) if items else "없음"


def _take(items: list[str], limit: int = 5) -> str:
    if not items:
        return "없음"
    if len(items) <= limit:
        return ", ".join(items)
    return f"{', '.join(items[:limit])} 외 {len(items) - limit}건"
