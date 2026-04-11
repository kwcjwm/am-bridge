from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from am_bridge.config import CliConfig, resolve_input_path
from am_bridge.backend_trace import trace_backend_dependencies
from am_bridge.models import BackendTraceModel, PageConversionPackage, PageModel, RelatedPageModel
from am_bridge.pipeline import analyze_file
from am_bridge.reporting import (
    join_values,
    limit_text,
    markdown_link,
    render_contents,
    render_csv,
    render_markdown_table,
)


def build_conversion_package(
    input_path: str | Path,
    backend_roots: list[Path] | None = None,
    source_roots: list[Path] | None = None,
    review_path: Path | None = None,
) -> PageConversionPackage:
    resolved_input = Path(input_path).resolve()
    page = analyze_file(resolved_input)
    traces = trace_backend_dependencies(page, backend_roots or [])
    related_pages = _build_related_pages(page, resolved_input, source_roots or [])
    package = PageConversionPackage(
        packageId=f"{page.pageId or resolved_input.stem}-package",
        page=page,
        backendTraces=traces,
        relatedPages=related_pages,
        openQuestions=_build_open_questions(page, traces, related_pages),
        aiHints=_build_ai_hints(page, traces),
        stageNotes=[
            "Treat stage 1 output as evidence plus candidate judgment, not as immutable truth.",
            "Run AI review before stage 2 whenever the page has a dominant grid, dynamic transaction wrappers, or ambiguous backend traces.",
        ],
    )
    if review_path and review_path.exists():
        apply_review_overrides(package, review_path)
    return package


def apply_review_overrides(package: PageConversionPackage, review_path: Path) -> None:
    raw = json.loads(review_path.read_text(encoding="utf-8"))

    if "primaryDatasetId" in raw:
        package.page.primaryDatasetId = raw["primaryDatasetId"]
    if "secondaryDatasetIds" in raw:
        package.page.secondaryDatasetIds = list(raw["secondaryDatasetIds"])
    if "primaryTransactionIds" in raw:
        package.page.primaryTransactionIds = list(raw["primaryTransactionIds"])
    if "interactionPattern" in raw:
        package.page.interactionPattern = raw["interactionPattern"]
    if "mainGridComponentId" in raw:
        package.page.mainGridComponentId = raw["mainGridComponentId"]

    dataset_overrides = raw.get("datasets", {})
    dataset_lookup = {dataset.datasetId: dataset for dataset in package.page.datasets}
    for dataset_id, override in dataset_overrides.items():
        dataset = dataset_lookup.get(dataset_id)
        if dataset is None:
            continue
        if "role" in override:
            dataset.role = override["role"]
        if "primaryUsage" in override:
            dataset.primaryUsage = override["primaryUsage"]
        if "salienceScore" in override:
            dataset.salienceScore = int(override["salienceScore"])
        if "boundComponents" in override:
            dataset.boundComponents = list(override["boundComponents"])
        if "salienceReasons" in override:
            dataset.salienceReasons = list(override["salienceReasons"])

    trace_overrides = raw.get("backendTraces", {})
    trace_lookup = {trace.transactionId: trace for trace in package.backendTraces}
    for transaction_id, override in trace_overrides.items():
        trace = trace_lookup.get(transaction_id)
        if trace is None:
            continue
        for field_name, value in override.items():
            if hasattr(trace, field_name):
                setattr(trace, field_name, value)

    for note in raw.get("reviewNotes", []):
        package.stageNotes.append(f"review-note: {note}")


def build_review_template(package: PageConversionPackage) -> dict:
    return {
        "primaryDatasetId": package.page.primaryDatasetId,
        "secondaryDatasetIds": package.page.secondaryDatasetIds,
        "primaryTransactionIds": package.page.primaryTransactionIds,
        "interactionPattern": package.page.interactionPattern,
        "mainGridComponentId": package.page.mainGridComponentId,
        "datasets": {
            dataset.datasetId: {
                "role": dataset.role,
                "primaryUsage": dataset.primaryUsage,
                "salienceScore": dataset.salienceScore,
                "boundComponents": dataset.boundComponents,
                "salienceReasons": dataset.salienceReasons,
            }
            for dataset in package.page.datasets
        },
        "backendTraces": {
            trace.transactionId: {
                "controllerClass": trace.controllerClass,
                "controllerMethod": trace.controllerMethod,
                "serviceInterface": trace.serviceInterface,
                "serviceImplClass": trace.serviceImplClass,
                "serviceMethod": trace.serviceMethod,
                "daoClass": trace.daoClass,
                "daoMethod": trace.daoMethod,
                "sqlMapId": trace.sqlMapId,
                "sqlMapFile": trace.sqlMapFile,
                "sqlOperation": trace.sqlOperation,
                "tableCandidates": trace.tableCandidates,
                "responseFieldCandidates": trace.responseFieldCandidates,
                "querySummary": trace.querySummary,
            }
            for trace in package.backendTraces
        },
        "reviewNotes": [
            "If the dominant result dataset is wrong, update primaryDatasetId and dataset.primaryUsage before stage 2.",
            "If AI found a better backend chain, override the affected backendTraces entry and rerun stage 1 or continue into stage 2 with that review file.",
        ],
    }


def generate_package_report(
    package: PageConversionPackage,
    registry_dir: str = "",
    artifact_links: dict[str, str] | None = None,
    lang: str = "en",
) -> str:
    return _generate_package_report_v2(
        package,
        registry_dir=registry_dir,
        artifact_links=artifact_links,
        lang=lang,
    )


def generate_analysis_report(
    package: PageConversionPackage,
    registry_dir: str = "",
    artifact_links: dict[str, str] | None = None,
    lang: str = "en",
) -> str:
    return _generate_analysis_report_v2(
        package,
        registry_dir=registry_dir,
        artifact_links=artifact_links,
        lang=lang,
    )


def generate_stage1_registries(package: PageConversionPackage) -> dict[str, str]:
    page = package.page
    return {
        "datasets.csv": render_csv(_dataset_rows(page)),
        "dataset-columns.csv": render_csv(_dataset_column_rows(page)),
        "components.csv": render_csv(_component_rows(page)),
        "bindings.csv": render_csv(_binding_rows(page)),
        "functions.csv": render_csv(_function_rows(page)),
        "events.csv": render_csv(_event_rows(page)),
        "transactions.csv": render_csv(_transaction_rows(page)),
        "backend-traces.csv": render_csv(_backend_trace_rows(package)),
        "navigation.csv": render_csv(_navigation_rows(page)),
        "validation-rules.csv": render_csv(_validation_rows(page)),
        "state-rules.csv": render_csv(_state_rule_rows(page)),
        "messages.csv": render_csv(_message_rows(page)),
        "grid-columns.csv": render_csv(_grid_column_rows(page)),
    }


def _generate_package_report_v2(
    package: PageConversionPackage,
    registry_dir: str = "",
    artifact_links: dict[str, str] | None = None,
    lang: str = "en",
) -> str:
    page = package.page
    sections: list[tuple[str, list[str]]] = [
        (
            _t(lang, "요약", "Executive Summary"),
            [
                f"- {_t(lang, '페이지', 'Page')}: `{page.pageId or 'unknown'}` / `{page.pageName or 'unknown'}`",
                f"- {_t(lang, '상호작용 패턴', 'Interaction pattern')}: `{page.interactionPattern or 'unknown'}`",
                f"- {_t(lang, '주요 업무 결과', 'Primary business result')}: {_t(lang, '데이터셋', 'dataset')} `{page.primaryDatasetId or 'unknown'}` / {_t(lang, '그리드', 'grid')} `{page.mainGridComponentId or 'unknown'}`",
                f"- {_t(lang, '주요 트랜잭션', 'Primary transaction')}: `{join_values(page.primaryTransactionIds, _t(lang, '잠금 없음', 'none locked'))}`",
                f"- {_t(lang, '관련 화면', 'Related screens')}: `{len(package.relatedPages)}` {_t(lang, '건 감지,', 'detected,')} `{sum(1 for item in package.relatedPages if item.resolutionStatus != 'resolved')}` {_t(lang, '건 미해결', 'unresolved')}",
            ],
        ),
        (
            _t(lang, "핵심 판단", "Key Decisions"),
            [
                f"- `{page.primaryDatasetId or 'unknown'}` {_t(lang, '를 대표 결과 데이터셋으로 본다. review override가 있으면 그 값을 따른다.', 'remains the main result dataset unless review overrides change it.')}",
                f"- `{page.interactionPattern or 'unknown'}` {_t(lang, '패턴을 기준으로 주요 결과 흐름을 먼저 보존한다.', 'interaction pattern should be preserved before UI redesign.')}",
                f"- {_t(lang, 'popup/subview 대상은 현재 화면 내부 조각이 아니라 별도 화면으로 취급한다.', 'Treat popup/subview targets as separate screens, not inline fragments of the current page.')}",
                f"- {_t(lang, '`review.json`에 보정사항을 남기고, 기술 보정만 대화에 두지 않는다.', 'Use `review.json` for corrections; do not carry technical fixes only in chat.')}",
            ],
        ),
    ]

    flow_rows = _main_flow_rows(package)
    if flow_rows:
        sections.append(
            (
                f"{_t(lang, '주요 사용자 흐름', 'Main User Flows')} ({len(flow_rows)})",
                render_markdown_table(
                    [
                        (_t(lang, "구분", "Flow"), "flow"),
                        (_t(lang, "트리거", "Trigger"), "trigger"),
                        (_t(lang, "트랜잭션", "Transaction"), "transactions"),
                        (_t(lang, "화면 이동", "Navigation"), "navigation"),
                        (_t(lang, "요약", "Summary"), "summary"),
                    ],
                    flow_rows,
                ),
            )
        )

    trace_rows = _backend_trace_summary_rows(package)
    if trace_rows:
        sections.append(
            (
                f"{_t(lang, '백엔드 추적 요약', 'Backend Trace Summary')} ({len(trace_rows)})",
                render_markdown_table(
                    [
                        (_t(lang, "트랜잭션", "Transaction"), "transactionId"),
                        (_t(lang, "경로", "Route"), "url"),
                        (_t(lang, "컨트롤러", "Controller"), "controller"),
                        (_t(lang, "SQL Map", "SQL Map"), "sqlMapId"),
                        (_t(lang, "테이블", "Tables"), "tables"),
                    ],
                    trace_rows,
                ),
            )
        )

    sections.append(
        (
            f"{_t(lang, '리스크 / 미해결 이슈', 'Risks / Open Questions')} ({len(package.openQuestions)})",
            [f"- {item}" for item in package.openQuestions] or [f"- {_t(lang, '없음', 'None')}"],
        )
    )
    sections.append(
        (
            _t(lang, "산출물 링크", "Artifact Index"),
            _artifact_index_lines(
                registry_dir=registry_dir,
                registry_files=list(generate_stage1_registries(package).keys()),
                artifact_links=artifact_links,
                lang=lang,
            ),
        )
    )
    sections.append(
        (
            _t(lang, "리뷰 가이드", "Review Guidance"),
            [
                f"- {_t(lang, '다음 단계 생성 전, 대표 데이터셋과 대표 그리드를 먼저 검증한다.', 'Validate the primary dataset and dominant grid before downstream generation.')}",
                f"- {_t(lang, '미해결 관련 화면과 동적 wrapper 트랜잭션은 stage1 안정판으로 보기 전에 먼저 정리한다.', 'Resolve unresolved related screens and dynamic wrapper transactions before treating stage 1 as stable.')}",
                f"- {_t(lang, '기술 보정은 `review.json`에 남겨 다음 실행에서 재사용되게 한다.', 'Keep technical corrections in `review.json` so the next run can reuse them.')}",
            ],
        )
    )
    return _compose_report(_t(lang, "Stage 1 전환 패키지", "Stage 1 - Conversion Package"), sections)


def _generate_analysis_report_v2(
    package: PageConversionPackage,
    registry_dir: str = "",
    artifact_links: dict[str, str] | None = None,
    lang: str = "en",
) -> str:
    page = package.page
    unresolved_related = [item for item in package.relatedPages if item.resolutionStatus != "resolved"]
    sections: list[tuple[str, list[str]]] = [
        (
            _t(lang, "요약", "Executive Summary"),
            [
                f"- {_t(lang, '이 화면은', 'This page behaves as a')} `{page.interactionPattern or 'unknown'}` {_t(lang, '패턴이며 중심 데이터셋은', 'centered on')} `{page.primaryDatasetId or 'unknown'}` {_t(lang, '이다.', '.')}",
                f"- {_t(lang, '대표 가시 영역은', 'Main visible result area is')} `{page.mainGridComponentId or 'unknown'}` {_t(lang, '이고 주요 트랜잭션은', 'and primary transaction is')} `{join_values(page.primaryTransactionIds, _t(lang, '추론 없음', 'none inferred'))}`{'' if lang == 'ko' else '.'}",
                f"- {_t(lang, '백엔드 추적', 'Backend traces resolved')}: `{len(package.backendTraces)}` / {_t(lang, '미해결 관련 화면', 'unresolved related screens')}: `{len(unresolved_related)}`",
                f"- {_t(lang, '원본 파일', 'Source file')}: `{page.legacy.sourceFile or 'unknown'}`",
            ],
        ),
        (_t(lang, "화면 해석", "Screen Story"), _screen_story_lines(package, lang)),
    ]

    dataset_rows = _dataset_summary_rows(page)
    if dataset_rows:
        sections.append(
            (
                f"{_t(lang, '주요 데이터 모델', 'Primary Data Model')} ({len(dataset_rows)})",
                render_markdown_table(
                    [
                        (_t(lang, "Dataset", "Dataset"), "datasetId"),
                        (_t(lang, "역할", "Role"), "role"),
                        (_t(lang, "사용 방식", "Usage"), "primaryUsage"),
                        (_t(lang, "컬럼 수", "Columns"), "columnCount"),
                        (_t(lang, "바인딩 컴포넌트", "Bound Components"), "boundComponents"),
                        (_t(lang, "중요도", "Salience"), "salienceScore"),
                    ],
                    dataset_rows,
                ),
            )
        )

    action_rows = _action_summary_rows(package)
    if action_rows:
        sections.append(
            (
                f"{_t(lang, '행동 / 이벤트 흐름', 'Action And Event Flow')} ({len(action_rows)})",
                render_markdown_table(
                    [
                        (_t(lang, "핸들러", "Handler"), "functionName"),
                        (_t(lang, "트리거", "Trigger"), "trigger"),
                        (_t(lang, "트랜잭션", "Transactions"), "transactions"),
                        (_t(lang, "읽기 ds", "Reads"), "readsDatasets"),
                        (_t(lang, "쓰기 ds", "Writes"), "writesDatasets"),
                        (_t(lang, "요약", "Summary"), "summary"),
                    ],
                    action_rows,
                ),
            )
        )

    trace_rows = _backend_trace_summary_rows(package)
    if trace_rows:
        sections.append(
            (
                f"{_t(lang, '백엔드 추적 요약', 'Backend Trace Summary')} ({len(trace_rows)})",
                render_markdown_table(
                    [
                        (_t(lang, "트랜잭션", "Transaction"), "transactionId"),
                        (_t(lang, "컨트롤러", "Controller"), "controller"),
                        (_t(lang, "서비스", "Service"), "service"),
                        (_t(lang, "DAO", "DAO"), "dao"),
                        (_t(lang, "SQL Map", "SQL Map"), "sqlMapId"),
                        (_t(lang, "테이블", "Tables"), "tables"),
                    ],
                    trace_rows,
                ),
            )
        )

    if package.relatedPages:
        sections.append(
            (
                f"{_t(lang, '관련 화면', 'Related Screens')} ({len(package.relatedPages)})",
                render_markdown_table(
                    [
                        (_t(lang, "유형", "Type"), "navigationType"),
                        (_t(lang, "대상", "Target"), "target"),
                        (_t(lang, "트리거", "Trigger"), "triggerFunction"),
                        (_t(lang, "상태", "Status"), "resolutionStatus"),
                        (_t(lang, "해석 결과", "Resolved Page"), "pageId"),
                    ],
                    _related_screen_rows(package),
                ),
            )
        )

    implication_lines = [f"- {item}" for item in package.aiHints]
    implication_lines.extend(f"- {item}" for item in package.stageNotes if item)
    sections.append((_t(lang, "전환 시사점", "Migration Implications"), implication_lines or [f"- {_t(lang, '없음', 'None')}"]))
    sections.append(
        (
            _t(lang, "근거 링크", "Evidence Registry Links"),
            _artifact_index_lines(
                registry_dir=registry_dir,
                registry_files=list(generate_stage1_registries(package).keys()),
                artifact_links=artifact_links,
                lang=lang,
            ),
        )
    )
    return _compose_report(_t(lang, "상세 레거시 분석 보고서", "Detailed Legacy Analysis Report"), sections)


def _compose_report(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]
    lines.extend(render_contents([section_title for section_title, _body in sections]))
    for section_title, body in sections:
        lines.append(f"## {section_title}")
        lines.append("")
        lines.extend(body or ["- None"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _artifact_index_lines(
    registry_dir: str,
    registry_files: list[str],
    artifact_links: dict[str, str] | None = None,
    lang: str = "en",
) -> list[str]:
    lines: list[str] = []
    for label, target in (artifact_links or {}).items():
        lines.append(f"- {label}: {markdown_link(label, target)}")
    if registry_dir:
        lines.append(f"- {_t(lang, '레지스트리 디렉토리', 'Registry directory')}: {markdown_link(registry_dir, registry_dir)}")
        for file_name in registry_files:
            lines.append(f"- {_t(lang, '레지스트리', 'Registry')}: {markdown_link(file_name, f'{registry_dir}/{file_name}')}")
    return lines or [f"- {_t(lang, '기록된 sidecar 산출물이 없습니다.', 'No sidecar artifacts recorded.')}"]


def _dataset_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "datasetId": dataset.datasetId,
            "role": dataset.role,
            "primaryUsage": dataset.primaryUsage,
            "salienceScore": dataset.salienceScore,
            "boundComponents": join_values(dataset.boundComponents),
            "columnCount": len(dataset.columns),
            "columns": join_values([column.name for column in dataset.columns]),
            "salienceReasons": join_values(dataset.salienceReasons),
        }
        for dataset in sorted(page.datasets, key=lambda item: (-item.salienceScore, item.datasetId))
    ]


def _dataset_column_rows(page: PageModel) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dataset in page.datasets:
        for column in dataset.columns:
            rows.append(
                {
                    "datasetId": dataset.datasetId,
                    "columnName": column.name,
                    "type": column.type,
                    "size": column.size,
                    "required": column.required,
                    "semanticType": column.semanticType,
                    "notes": column.notes,
                }
            )
    return rows


def _component_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "componentId": component.componentId,
            "componentType": component.componentType,
            "label": _component_label(page, component),
            "parentId": component.parentId,
            "layoutGroup": component.layoutGroup,
            "events": join_values(component.events),
            "sourceRefs": join_values(component.sourceRefs),
        }
        for component in page.components
    ]


def _binding_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "bindingId": binding.bindingId,
            "componentId": binding.componentId,
            "datasetId": binding.datasetId,
            "columnName": binding.columnName,
            "bindingType": binding.bindingType,
            "direction": binding.direction,
            "sourceRefs": join_values(binding.sourceRefs),
        }
        for binding in page.bindings
    ]


def _function_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "functionName": function.functionName,
            "functionType": function.functionType,
            "parameters": join_values(function.parameters),
            "callsFunctions": join_values(function.callsFunctions),
            "callsTransactions": join_values(function.callsTransactions),
            "readsDatasets": join_values(function.readsDatasets),
            "writesDatasets": join_values(function.writesDatasets),
            "controlsComponents": join_values(function.controlsComponents),
            "platformCalls": join_values(function.platformCalls),
        }
        for function in page.functions
    ]


def _event_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "eventId": event.eventId,
            "sourceComponentId": event.sourceComponentId,
            "eventName": event.eventName,
            "handlerFunction": event.handlerFunction,
            "eventType": event.eventType,
            "triggerCondition": event.triggerCondition,
            "effects": join_values(event.effects),
        }
        for event in page.events
    ]


def _transaction_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "transactionId": item.transactionId,
            "serviceId": item.serviceId,
            "url": item.url,
            "inputDatasets": join_values(item.inputDatasets),
            "outputDatasets": join_values(item.outputDatasets),
            "parameters": item.parameters,
            "callbackFunction": item.callbackFunction,
            "wrapperFunction": item.wrapperFunction,
            "apiCandidate": item.apiCandidate,
        }
        for item in page.transactions
    ]


def _backend_trace_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    return [
        {
            "transactionId": trace.transactionId,
            "url": trace.url,
            "requestMapping": trace.requestMapping,
            "controller": _join_nonempty(trace.controllerClass, trace.controllerMethod),
            "service": _join_nonempty(trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod),
            "dao": _join_nonempty(trace.daoClass, trace.daoMethod),
            "sqlMapId": trace.sqlMapId,
            "sqlMapFile": trace.sqlMapFile,
            "tables": join_values(trace.tableCandidates),
            "responseFields": join_values(trace.responseFieldCandidates),
            "querySummary": trace.querySummary,
        }
        for trace in package.backendTraces
    ]


def _navigation_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "navigationId": item.navigationId,
            "triggerFunction": item.triggerFunction,
            "navigationType": item.navigationType,
            "target": item.target,
            "parameterBindings": join_values(item.parameterBindings),
            "returnHandling": item.returnHandling,
        }
        for item in page.navigation
    ]


def _validation_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "ruleId": item.ruleId,
            "targetField": item.targetField,
            "validationType": item.validationType,
            "triggerTiming": item.triggerTiming,
            "sourceFunction": item.sourceFunction,
            "expression": item.expression,
            "message": item.message,
        }
        for item in page.validationRules
    ]


def _state_rule_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "ruleId": item.ruleId,
            "targetComponentId": item.targetComponentId,
            "stateProperty": item.stateProperty,
            "triggerCondition": item.triggerCondition,
            "sourceFunction": item.sourceFunction,
            "expression": item.expression,
            "targetValue": item.targetValue,
        }
        for item in page.stateRules
    ]


def _message_rows(page: PageModel) -> list[dict[str, Any]]:
    return [
        {
            "messageId": item.messageId,
            "sourceType": item.sourceType,
            "messageType": item.messageType,
            "text": item.text,
            "sourceFunction": item.sourceFunction,
            "targetComponentId": item.targetComponentId,
            "i18nKeyCandidate": item.i18nKeyCandidate,
        }
        for item in page.messages
    ]


def _grid_column_rows(page: PageModel) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component in page.components:
        grid_meta = component.properties.get("gridMeta", {})
        for band_name in ("headColumns", "bodyColumns"):
            for column in grid_meta.get(band_name, []):
                rows.append(
                    {
                        "componentId": component.componentId,
                        "band": column.get("band", band_name.replace("Columns", "")),
                        "col": column.get("col", ""),
                        "columnName": column.get("columnName", ""),
                        "display": column.get("display", ""),
                        "text": column.get("text", ""),
                    }
                )
    return rows


def _dataset_summary_rows(page: PageModel) -> list[dict[str, Any]]:
    rows = _dataset_rows(page)
    for row in rows:
        if row["datasetId"] == page.primaryDatasetId:
            row["datasetId"] = f"{row['datasetId']} [PRIMARY]"
    return rows


def _main_flow_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    page = package.page
    navigation_by_function = {item.triggerFunction: item for item in page.navigation}
    event_by_handler = {item.handlerFunction: item for item in page.events if item.handlerFunction}
    rows: list[dict[str, Any]] = []
    for function in page.functions:
        if function.functionType != "event-handler":
            continue
        event = event_by_handler.get(function.functionName)
        navigation = navigation_by_function.get(function.functionName)
        summary_bits: list[str] = []
        if function.callsTransactions:
            summary_bits.append(f"calls {join_values(function.callsTransactions)}")
        if navigation is not None:
            summary_bits.append(f"{navigation.navigationType} -> {navigation.target}")
        if function.controlsComponents:
            summary_bits.append(f"controls {join_values(function.controlsComponents)}")
        rows.append(
            {
                "flow": "Initial load" if function.functionName == page.legacy.initialEvent else "User action",
                "trigger": _trigger_label(page, event.sourceComponentId if event else "") or function.functionName,
                "transactions": join_values(function.callsTransactions),
                "navigation": navigation.navigationType if navigation is not None else "none",
                "summary": "; ".join(summary_bits) or "manual review required",
            }
        )
    return rows


def _action_summary_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    page = package.page
    event_by_handler = {item.handlerFunction: item for item in page.events if item.handlerFunction}
    navigation_by_function = {item.triggerFunction: item for item in page.navigation}
    rows: list[dict[str, Any]] = []
    for function in page.functions:
        if function.functionType != "event-handler":
            continue
        event = event_by_handler.get(function.functionName)
        navigation = navigation_by_function.get(function.functionName)
        summary = (
            f"{navigation.navigationType} -> {navigation.target}"
            if navigation is not None
            else limit_text(join_values(function.controlsComponents, "no direct UI control"), 80)
        )
        rows.append(
            {
                "functionName": function.functionName,
                "trigger": _trigger_label(page, event.sourceComponentId if event else "") or function.functionName,
                "transactions": join_values(function.callsTransactions),
                "readsDatasets": join_values(function.readsDatasets),
                "writesDatasets": join_values(function.writesDatasets),
                "summary": summary,
            }
        )
    return rows


def _backend_trace_summary_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    return [
        {
            "transactionId": trace.transactionId,
            "url": limit_text(trace.url or "unknown", 70),
            "controller": _join_nonempty(trace.controllerClass, trace.controllerMethod),
            "service": _join_nonempty(trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod),
            "dao": _join_nonempty(trace.daoClass, trace.daoMethod),
            "sqlMapId": trace.sqlMapId or "unknown",
            "tables": join_values(trace.tableCandidates),
        }
        for trace in package.backendTraces
    ]


def _related_screen_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    return [
        {
            "navigationType": item.navigationType,
            "target": item.target or item.navigationId,
            "triggerFunction": item.triggerFunction or "unknown",
            "resolutionStatus": item.resolutionStatus or "unknown",
            "pageId": item.pageId or "unresolved",
        }
        for item in package.relatedPages
    ]


def _screen_story_lines(package: PageConversionPackage, lang: str = "en") -> list[str]:
    page = package.page
    return [
        (
            f"- {_t(lang, '이 페이지는', 'This page opens as')} "
            f"`{page.pageType or 'unknown'}` "
            f"{_t(lang, '유형이며', 'and centers the user on')} "
            f"`{page.mainGridComponentId or 'unknown'}` "
            f"{_t(lang, '영역과', 'backed by')} "
            f"`{page.primaryDatasetId or 'unknown'}`."
        ),
        (
            f"- {_t(lang, '초기 이벤트는', 'Initial event is')} "
            f"`{page.legacy.initialEvent or 'unknown'}` "
            f"{_t(lang, '이며 preload 또는 lookup 성격인지 검토해야 한다.', 'and should be reviewed for preload or lookup behavior.')}"
        ),
        (
            f"- {_t(lang, '주요 가시 액션은', 'Primary visible actions detected')}: "
            f"{join_values([item['trigger'] for item in _main_flow_rows(package)], _t(lang, '추론 없음', 'none inferred'))}."
        ),
        f"- {_t(lang, '관련 화면 이동 수', 'Related navigation count')}: `{len(package.relatedPages)}`.",
    ]


def _t(lang: str, ko: str, en: str) -> str:
    return ko if lang == "ko" else en


def _trigger_label(page: PageModel, component_id: str) -> str:
    if not component_id:
        return ""
    component = next((item for item in page.components if item.componentId == component_id), None)
    if component is None:
        return component_id
    return _component_label(page, component)


def _component_label(page: PageModel, component: Any) -> str:
    direct = str(component.properties.get("Text") or component.properties.get("Caption") or "").strip()
    if direct:
        return direct

    target_left = _safe_int(component.properties.get("Left"))
    target_top = _safe_int(component.properties.get("Top"))
    for other in page.components:
        if other.parentId != component.parentId or other.componentType not in {"Static", "Label"}:
            continue
        other_text = str(other.properties.get("Text") or other.properties.get("Caption") or "").strip()
        if not other_text:
            continue
        other_left = _safe_int(other.properties.get("Left"))
        other_top = _safe_int(other.properties.get("Top"))
        if other_left <= target_left and abs(other_top - target_top) <= 24:
            return other_text
    return component.componentId


def _safe_int(value: Any) -> int:
    try:
        return int(str(value or 0))
    except (TypeError, ValueError):
        return 0


def _build_open_questions(
    page: PageModel,
    traces: list[BackendTraceModel],
    related_pages: list[RelatedPageModel],
) -> list[str]:
    questions: list[str] = []
    if not page.primaryDatasetId:
        questions.append("No primaryDatasetId was inferred. Force an AI review on dataset salience.")
    if page.mainGridComponentId and not any(dataset.primaryUsage == "main-grid" for dataset in page.datasets):
        questions.append("A grid exists but no dataset was classified as main-grid.")
    for transaction in page.transactions:
        if transaction.url and not _looks_static_url(transaction.url):
            questions.append(
                f"{transaction.transactionId} uses a dynamic or wrapper URL. Confirm the final endpoint contract manually."
            )
    for transaction_id in page.primaryTransactionIds:
        if not any(trace.transactionId == transaction_id and trace.controllerMethod for trace in traces):
            questions.append(
                f"{transaction_id} has no resolved backend controller trace from configured backendRoots."
            )
    for trace in traces:
        if trace.controllerMethod and not trace.sqlMapId:
            questions.append(
                f"{trace.transactionId} resolved controller/service layers but still has no SQL map. Review DAO/sql trace manually."
            )
    for related in related_pages:
        if related.resolutionStatus != "resolved":
            questions.append(
                f"Related screen target {related.target or related.navigationId} could not be resolved automatically. Confirm whether it should be treated as a separate page."
            )
    return sorted(dict.fromkeys(questions))


def _build_ai_hints(page: PageModel, traces: list[BackendTraceModel]) -> list[str]:
    hints: list[str] = []
    if page.primaryDatasetId:
        primary_dataset = next(
            (dataset for dataset in page.datasets if dataset.datasetId == page.primaryDatasetId),
            None,
        )
        if primary_dataset is not None:
            hints.append(
                f"Treat {primary_dataset.datasetId} as the primary business dataset unless review overrides say otherwise."
            )
            if primary_dataset.salienceReasons:
                hints.append(
                    f"Primary dataset reasons: {', '.join(primary_dataset.salienceReasons)}"
                )

    search_dataset = next(
        (dataset for dataset in page.datasets if dataset.primaryUsage == 'search-form'),
        None,
    )
    if search_dataset is not None:
        hints.append(
            f"Treat {search_dataset.datasetId} as a request/search dataset, not as a peer to the primary result dataset."
        )

    if traces:
        trace = _find_primary_trace(page, traces)
        if trace.controllerMethod:
            hints.append(
                f"Resolved backend chain begins at {trace.controllerClass}.{trace.controllerMethod}."
            )
    if page.navigation:
        hints.append(
            "Treat popup/subview navigation targets as related screens. Do not merge them into the current page implementation by default."
        )
    return hints


def _build_related_pages(
    page: PageModel,
    input_path: Path,
    source_roots: list[Path],
) -> list[RelatedPageModel]:
    config = CliConfig(sourceRoots=source_roots)
    related_pages: list[RelatedPageModel] = []
    seen: set[tuple[str, str]] = set()

    for navigation in page.navigation:
        key = (navigation.navigationType, navigation.target)
        if key in seen:
            continue
        seen.add(key)

        resolved_path = _resolve_navigation_target(navigation.target, input_path, config)
        related = RelatedPageModel(
            navigationId=navigation.navigationId,
            navigationType=navigation.navigationType,
            triggerFunction=navigation.triggerFunction,
            target=navigation.target,
            resolvedPath=str(resolved_path) if resolved_path else "",
            resolutionStatus="unresolved",
        )

        if resolved_path is not None:
            try:
                related_page = analyze_file(resolved_path)
                related.pageId = related_page.pageId
                related.pageName = related_page.pageName
                related.pageType = related_page.pageType
                related.resolutionStatus = "resolved"
            except Exception:
                related.resolutionStatus = "path-resolved-analysis-failed"

        related_pages.append(related)

    return related_pages


def _resolve_navigation_target(target: str, input_path: Path, config: CliConfig) -> Path | None:
    if not target:
        return None

    candidates: list[str] = [target]
    if "::" in target:
        _prefix, suffix = target.split("::", 1)
        candidates.append(suffix)
        candidates.append(target.replace("::", "/"))
    if target.endswith(".xml"):
        candidates.append(Path(target).name)

    for candidate in dict.fromkeys(candidates):
        try:
            return resolve_input_path(candidate, config, cwd=input_path.parent)
        except (FileNotFoundError, ValueError):
            continue
    return None


def _find_primary_trace(page: PageModel, traces: list[BackendTraceModel]) -> BackendTraceModel:
    for transaction_id in page.primaryTransactionIds:
        trace = next((item for item in traces if item.transactionId == transaction_id), None)
        if trace is not None:
            return trace
    return traces[0]


def _looks_static_url(url: str) -> bool:
    stripped = url.strip()
    return bool(stripped) and all(token not in stripped for token in ('"', "'", "+", "svc::"))


def _join(values: list[str]) -> str:
    items = [item for item in values if item]
    return ", ".join(items) if items else "none"


def _join_nonempty(first: str, second: str) -> str:
    return ".".join(item for item in [first, second] if item) or "unknown"
