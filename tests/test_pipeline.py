from pathlib import Path

from am_bridge.pipeline import analyze_file


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "basic_page.xml"
OI_VISION_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "oi_vision_page.xml"
VALIDATION_HEAVY_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "validation_heavy_page.xml"
POPUP_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "popup_page.xml"
COMPLEX_GRID_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "complex_grid_page.xml"
PLATFORM_HEAVY_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "platform_heavy_page.xml"


def test_pipeline_extracts_core_structures() -> None:
    model = analyze_file(FIXTURE_PATH)

    assert model.pageId == "MainForm"
    assert model.pageType == "main"
    assert len(model.datasets) == 3
    assert len(model.components) >= 3

    dataset_ids = {dataset.datasetId for dataset in model.datasets}
    assert {"ds_search", "ds_result", "ds_code"} <= dataset_ids

    component_ids = {component.componentId for component in model.components}
    assert {"ComboStatus", "ButtonSearch", "ButtonApproval", "Grid0"} <= component_ids

    binding_pairs = {
        (binding.componentId, binding.datasetId, binding.columnName)
        for binding in model.bindings
    }
    assert ("Grid0", "ds_result", "equipmentId") in binding_pairs
    assert ("Grid0", "ds_result", "status") in binding_pairs
    assert ("ComboStatus", "ds_code", "code") in binding_pairs
    assert ("ComboStatus", "ds_code", "name") in binding_pairs

    function_names = {function.functionName for function in model.functions}
    assert {
        "form_OnLoadCompleted",
        "fnLoadCodes",
        "fnSearch",
        "ComboStatus_OnChanged",
        "fnOpenApproval",
        "fnCallback",
    } <= function_names

    transaction_urls = {transaction.url for transaction in model.transactions}
    assert {"/api/common/codes", "/api/equipment/status"} <= transaction_urls

    event_names = {
        (event.sourceComponentId, event.eventName, event.handlerFunction)
        for event in model.events
    }
    assert ("MainForm", "OnLoadCompleted", "form_OnLoadCompleted") in event_names
    assert ("ButtonSearch", "OnClick", "fnSearch") in event_names
    assert ("ComboStatus", "OnChanged", "ComboStatus_OnChanged") in event_names
    assert ("ButtonApproval", "OnClick", "fnOpenApproval") in event_names


def test_function_model_captures_calls_and_dataset_usage() -> None:
    model = analyze_file(FIXTURE_PATH)
    function_lookup = {function.functionName: function for function in model.functions}

    search_function = function_lookup["fnSearch"]
    assert "TX-FNSEARCH-1" in search_function.callsTransactions
    assert "ComboStatus" in search_function.controlsComponents

    change_function = function_lookup["ComboStatus_OnChanged"]
    assert "ds_search" in change_function.writesDatasets


def test_second_wave_extracts_grid_platform_and_navigation() -> None:
    model = analyze_file(FIXTURE_PATH)

    grid = next(component for component in model.components if component.componentId == "Grid0")
    assert "gridMeta" in grid.properties
    assert grid.properties["gridMeta"]["columnCount"] == 2
    assert len(grid.properties["gridMeta"]["headColumns"]) == 2

    assert model.platform.approvalRequired is True
    assert "approval" in model.platform.sharedComponentUsage

    approval_button = next(
        component for component in model.components if component.componentId == "ButtonApproval"
    )
    assert isinstance(approval_button.platformDependency, list)
    assert "approval" in approval_button.platformDependency

    assert any(item.navigationType == "popup" for item in model.navigation)


def test_page_conversion_spec_generator() -> None:
    from am_bridge.generators import generate_page_conversion_spec

    model = analyze_file(FIXTURE_PATH)
    spec = generate_page_conversion_spec(model)

    assert "# 페이지 전환 명세" in spec
    assert "페이지 ID: MainForm" in spec
    assert "## 기존 화면 구조(아스키 와이어프레임)" in spec
    assert "ASCII 와이어프레임" in spec
    assert "PAGE MainForm" in spec
    assert "[ROW 01]" in spec
    assert "Grid / ds_result" in spec
    assert "## 함수 호출 연계" in spec
    assert "[FUNC] fnSearch(" in spec
    assert "-> [TX] TX-FNSEARCH-1 / /api/equipment/status" in spec
    assert "결재: 필요" in spec
    assert "popup:DefApp::approval.xml" in spec
    assert "## 함수별 슈도코드" in spec
    assert "## R&R 정의" in spec


def test_popup_fixture_captures_popup_type_and_subview_navigation() -> None:
    model = analyze_file(POPUP_FIXTURE_PATH)

    assert model.pageId == "LotHistoryPopup"
    assert model.pageType == "popup"
    assert any(item.url == "/api/lot/history" for item in model.transactions)
    assert any(
        item.navigationType == "subview" and item.target == "Frame::history-detail.xml"
        for item in model.navigation
    )


def test_complex_grid_fixture_captures_summary_and_editable_grid() -> None:
    model = analyze_file(COMPLEX_GRID_FIXTURE_PATH)

    grid = next(component for component in model.components if component.componentId == "GridMain")
    grid_meta = grid.properties["gridMeta"]
    assert grid_meta["columnCount"] == 3
    assert grid_meta["hasSummary"] is True
    assert grid_meta["editable"] is True
    assert len(grid_meta["summaryColumns"]) == 2

    binding_pairs = {
        (binding.componentId, binding.datasetId, binding.columnName, binding.bindingType)
        for binding in model.bindings
    }
    assert ("GridMain", "ds_result", "selected", "grid-cell") in binding_pairs
    assert ("GridMain", "ds_result", "equipmentId", "grid-cell") in binding_pairs
    assert ("GridMain", "ds_result", "qty", "grid-cell") in binding_pairs


def test_platform_heavy_fixture_normalizes_platform_dependency_array() -> None:
    model = analyze_file(PLATFORM_HEAVY_FIXTURE_PATH)

    dependency_map = {
        component.componentId: component.platformDependency
        for component in model.components
        if component.componentId.startswith("Button")
    }

    assert dependency_map["ButtonApproval"] == ["approval"]
    assert dependency_map["ButtonMail"] == ["mail"]
    assert dependency_map["ButtonPermission"] == ["permission"]
    assert dependency_map["ButtonAuth"] == ["auth"]

    assert model.platform.sharedComponentUsage == ["approval", "auth", "mail", "permission"]
    assert model.platform.approvalRequired is True
    assert model.platform.mailIntegration is True
    assert model.platform.permissionKey == "PAGE:PlatformHeavyForm"
    assert model.platform.menuKey == "MENU:PlatformHeavyForm"


def test_third_wave_extracts_realtime_chart_vision_alarm_command_review() -> None:
    model = analyze_file(OI_VISION_FIXTURE_PATH)

    realtime_sources = {(item.sourceType, item.sourceName) for item in model.realtimeSubscriptions}
    assert ("polling", "/api/alarm/stream") in realtime_sources
    assert ("mqtt", "/topic/alarm") in realtime_sources
    assert ("mqtt", "/topic/vision/review") in realtime_sources

    alarm_polling = next(
        item for item in model.realtimeSubscriptions if item.sourceName == "/api/alarm/stream"
    )
    assert alarm_polling.lifecycleStart == "form_OnLoadCompleted"
    assert alarm_polling.lifecycleEnd == "form_OnClose"
    assert "ds_alarm" in alarm_polling.targetDatasets

    chart = next(item for item in model.charts if item.chartId == "ChartTrend")
    assert chart.chartType == "line"
    assert chart.datasetId == "ds_chart"
    assert chart.refreshMode == "realtime"
    assert len(chart.series) == 2

    viewer = next(item for item in model.imageVisionViews if item.viewerId == "ImageViewerMain")
    assert viewer.viewerType == "image-review"
    assert viewer.imageSource["mode"] == "dataset-field"
    assert viewer.resultDatasetId == "ds_reviewQueue"
    assert {"bbox", "label"} <= set(viewer.overlayTypes)
    assert {"zoom", "pan", "roi"} <= set(viewer.interactions)

    alarm = next(item for item in model.alarmEvents if item.eventStreamId == "ALARM:ds_alarm")
    assert alarm.sourceType in {"polling", "mqtt"}
    assert alarm.severityField == "severity"
    assert alarm.ackFunction == "fnAckAlarm"
    assert alarm.clearFunction == "fnClearAlarm"
    assert alarm.refreshMode == "realtime"

    command = next(item for item in model.commandActions if item.triggerComponentId == "ButtonStartEquipment")
    assert command.commandTarget == "equipment.start"
    assert command.requiredRole == "ROLE_OPERATOR"
    assert command.confirmationRequired is True
    assert command.auditRequired is True
    assert command.successCallback == "fnCommandSuccess"
    assert command.failureCallback == "fnCommandFailure"

    workflow = next(item for item in model.reviewWorkflows if item.sourceDatasetId == "ds_reviewQueue")
    assert workflow.workflowType == "vision-review"
    assert workflow.approvalIntegration is True
    assert workflow.auditRequired is True
    assert {"APPROVED", "REJECTED", "PENDING", "WAIT"} <= set(workflow.states)
    assert {"ROLE_REVIEWER"} <= set(workflow.roles)
    action_types = {action["actionType"] for action in workflow.actions}
    assert {"approve", "reject"} <= action_types


def test_page_conversion_spec_generator_includes_oi_vision_details() -> None:
    from am_bridge.generators import generate_page_conversion_spec

    model = analyze_file(OI_VISION_FIXTURE_PATH)
    spec = generate_page_conversion_spec(model)

    assert "## OI / Vision 특화" in spec
    assert "실시간 구독: polling:/api/alarm/stream" in spec
    assert "차트: ChartTrend(line/ds_chart)" in spec
    assert "이미지 / 비전 뷰: ImageViewerMain(image-review/ds_reviewQueue)" in spec
    assert "알람 스트림: ALARM:ds_alarm(realtime/fnAckAlarm)" in spec
    assert "제어 명령: 설비 시작(equipment.start)" in spec
    assert "리뷰 워크플로: REVIEW-0001(vision-review/ds_reviewQueue)" in spec


def test_fourth_wave_extracts_style_state_validation_and_messages() -> None:
    model = analyze_file(VALIDATION_HEAVY_FIXTURE_PATH)

    style_pairs = {(style.componentId, style.property, style.rawValue) for style in model.styles}
    assert ("StaticLotId", "text-color", "#222222") in style_pairs
    assert ("EditLotId", "background-color", "#ffffff") in style_pairs
    assert ("EditLotId", "class", "input-required") in style_pairs
    assert ("ButtonSave", "background-color", "#007acc") in style_pairs

    edit_lot = next(component for component in model.components if component.componentId == "EditLotId")
    assert edit_lot.styleKey == "input-required"

    state_rules = {
        (rule.targetComponentId, rule.stateProperty, rule.sourceFunction, rule.targetValue)
        for rule in model.stateRules
    }
    assert ("ButtonSave", "Enable", "form_OnLoadCompleted", False) in state_rules
    assert ("ButtonSave", "Enable", "EditLotId_OnChanged", True) in state_rules
    assert ("DivDetail", "Visible", "fnToggleDetail", False) in state_rules

    validation_rules = {
        (rule.targetField, rule.validationType, rule.triggerTiming, rule.message)
        for rule in model.validationRules
    }
    assert ("EditLotId", "required", "save", "LOT ID는 필수입니다.") in validation_rules
    assert ("EditQty", "number", "save", "수량은 숫자여야 합니다.") in validation_rules
    assert ("EditRemark", "length", "save", "비고는 100자 이하여야 합니다.") in validation_rules

    messages = {(message.messageType, message.text, message.targetComponentId) for message in model.messages}
    assert ("label", "LOT ID", "StaticLotId") in messages
    assert ("action-label", "저장", "ButtonSave") in messages
    assert ("alert", "LOT ID는 필수입니다.", "") in messages
    assert ("confirm", "저장하시겠습니까?", "") in messages
    assert ("status-text", "입력 완료", "StaticStatus") in messages

    assert "LOT ID는 필수입니다." in model.notes


def test_page_conversion_spec_generator_includes_ui_rule_summary() -> None:
    from am_bridge.generators import generate_page_conversion_spec

    model = analyze_file(VALIDATION_HEAVY_FIXTURE_PATH)
    spec = generate_page_conversion_spec(model)

    assert "## UI 규칙 요약" in spec
    assert "- 스타일: 총 13건" in spec
    assert "input-required" in spec
    assert "- 상태 규칙: 총 3건 / 대상: ButtonSave.Enable, DivDetail.Visible" in spec
    assert "- 검증 규칙: 총 3건 / 유형: length, number, required" in spec
    assert "- 메시지: 총 9건 / 유형: action-label, alert, confirm, label, status-text" in spec
