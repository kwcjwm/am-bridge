from __future__ import annotations

import csv
from io import StringIO

from am_bridge.models import ConversionPlanModel, PageConversionPackage, VuePageConfigModel
from am_bridge.report_hubs import build_stage1_hub_docs, build_stage2_hub_docs


def build_stage1_report_sidecars(package: PageConversionPackage) -> dict[str, str]:
    page = package.page
    table_specs = [
        (
            "datasets.csv",
            "Dataset-level salience, role, usage, and binding summary.",
            _csv(
                [
                    "datasetId",
                    "role",
                    "primaryUsage",
                    "salienceScore",
                    "boundComponents",
                    "columns",
                    "defaultRecordCount",
                    "salienceReasons",
                ],
                [
                    {
                        "datasetId": dataset.datasetId,
                        "role": dataset.role,
                        "primaryUsage": dataset.primaryUsage,
                        "salienceScore": dataset.salienceScore,
                        "boundComponents": _join(dataset.boundComponents),
                        "columns": _join([column.name for column in dataset.columns]),
                        "defaultRecordCount": len(dataset.defaultRecords),
                        "salienceReasons": _join(dataset.salienceReasons),
                    }
                    for dataset in page.datasets
                ],
            ),
        ),
        (
            "components.csv",
            "UI components with layout grouping and event hints.",
            _csv(
                [
                    "componentId",
                    "componentType",
                    "layoutGroup",
                    "parentId",
                    "containerPath",
                    "events",
                    "platformDependency",
                ],
                [
                    {
                        "componentId": component.componentId,
                        "componentType": component.componentType,
                        "layoutGroup": component.layoutGroup,
                        "parentId": component.parentId,
                        "containerPath": component.containerPath,
                        "events": _join(component.events),
                        "platformDependency": _join(component.platformDependency),
                    }
                    for component in page.components
                ],
            ),
        ),
        (
            "user-actions.csv",
            "Event handlers and their data, control, and transaction touchpoints.",
            _csv(
                [
                    "functionName",
                    "functionType",
                    "transactions",
                    "controlsComponents",
                    "readsDatasets",
                    "writesDatasets",
                    "callsFunctions",
                    "platformCalls",
                ],
                [
                    {
                        "functionName": function.functionName,
                        "functionType": function.functionType,
                        "transactions": _join(function.callsTransactions),
                        "controlsComponents": _join(function.controlsComponents),
                        "readsDatasets": _join(function.readsDatasets),
                        "writesDatasets": _join(function.writesDatasets),
                        "callsFunctions": _join(function.callsFunctions),
                        "platformCalls": _join(function.platformCalls),
                    }
                    for function in page.functions
                    if function.functionType == "event-handler"
                ],
            ),
        ),
        (
            "backend-traces.csv",
            "Resolved controller, service, DAO, and SQL evidence per transaction.",
            _csv(
                [
                    "transactionId",
                    "url",
                    "controllerClass",
                    "controllerMethod",
                    "serviceImplClass",
                    "serviceMethod",
                    "daoClass",
                    "daoMethod",
                    "sqlMapId",
                    "tableCandidates",
                    "responseFieldCandidates",
                    "querySummary",
                ],
                [
                    {
                        "transactionId": trace.transactionId,
                        "url": trace.url,
                        "controllerClass": trace.controllerClass,
                        "controllerMethod": trace.controllerMethod,
                        "serviceImplClass": trace.serviceImplClass,
                        "serviceMethod": trace.serviceMethod,
                        "daoClass": trace.daoClass,
                        "daoMethod": trace.daoMethod,
                        "sqlMapId": trace.sqlMapId,
                        "tableCandidates": _join(trace.tableCandidates),
                        "responseFieldCandidates": _join(trace.responseFieldCandidates),
                        "querySummary": trace.querySummary,
                    }
                    for trace in package.backendTraces
                ],
            ),
        ),
        (
            "related-pages.csv",
            "Resolved or unresolved related screens inferred from navigation flows.",
            _csv(
                [
                    "navigationId",
                    "navigationType",
                    "triggerFunction",
                    "target",
                    "pageId",
                    "pageName",
                    "resolutionStatus",
                ],
                [
                    {
                        "navigationId": related.navigationId,
                        "navigationType": related.navigationType,
                        "triggerFunction": related.triggerFunction,
                        "target": related.target,
                        "pageId": related.pageId,
                        "pageName": related.pageName,
                        "resolutionStatus": related.resolutionStatus,
                    }
                    for related in package.relatedPages
                ],
            ),
        ),
        (
            "validation-rules.csv",
            "Validation rules by field and source function.",
            _csv(
                [
                    "ruleId",
                    "targetField",
                    "validationType",
                    "triggerTiming",
                    "sourceFunction",
                    "message",
                ],
                [
                    {
                        "ruleId": rule.ruleId,
                        "targetField": rule.targetField,
                        "validationType": rule.validationType,
                        "triggerTiming": rule.triggerTiming,
                        "sourceFunction": rule.sourceFunction,
                        "message": rule.message,
                    }
                    for rule in page.validationRules
                ],
            ),
        ),
    ]

    files = _with_readme(table_specs, _render_stage1_readme(package, table_specs))
    files.update(build_stage1_hub_docs(package, [(name, description, description) for name, description, _content in table_specs]))
    return files


def build_stage2_report_sidecars(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
) -> dict[str, str]:
    table_specs = [
        (
            "search-controls.csv",
            "Search and command area controls with binding and validation hints.",
            _csv(
                [
                    "componentId",
                    "componentType",
                    "controlRole",
                    "label",
                    "datasetId",
                    "boundColumn",
                    "requestFieldCandidate",
                    "events",
                    "triggerActions",
                    "validationRuleCount",
                    "validationSummary",
                ],
                [
                    {
                        "componentId": item.get("componentId", ""),
                        "componentType": item.get("componentType", ""),
                        "controlRole": item.get("controlRole", ""),
                        "label": item.get("label", ""),
                        "datasetId": item.get("datasetId", ""),
                        "boundColumn": item.get("boundColumn", ""),
                        "requestFieldCandidate": item.get("requestFieldCandidate", ""),
                        "events": _join(item.get("events", [])),
                        "triggerActions": _join(item.get("triggerActions", [])),
                        "validationRuleCount": len(item.get("validationRules", [])),
                        "validationSummary": _join(
                            [
                                rule.get("message", "") or rule.get("validationType", "")
                                for rule in item.get("validationRules", [])
                            ]
                        ),
                    }
                    for item in vue_config.searchControls
                ],
            ),
        ),
        (
            "grids.csv",
            "Grid-level layout, dataset binding, and header summary.",
            _csv(
                [
                    "componentId",
                    "datasetId",
                    "layoutGroup",
                    "events",
                    "columnCount",
                    "headerTexts",
                    "datasetColumns",
                ],
                [
                    {
                        "componentId": item.get("componentId", ""),
                        "datasetId": item.get("datasetId", ""),
                        "layoutGroup": item.get("layoutGroup", ""),
                        "events": _join(item.get("events", [])),
                        "columnCount": len(item.get("bodyColumns", [])),
                        "headerTexts": _join(item.get("headerTexts", [])),
                        "datasetColumns": _join(item.get("datasetColumns", [])),
                    }
                    for item in vue_config.grids
                ],
            ),
        ),
        (
            "grid-columns.csv",
            "Flattened grid header/body columns for quick visual inspection.",
            _csv(
                [
                    "componentId",
                    "band",
                    "columnOrder",
                    "columnName",
                    "text",
                    "display",
                ],
                [
                    {
                        "componentId": grid.get("componentId", ""),
                        "band": column.get("band", ""),
                        "columnOrder": index,
                        "columnName": column.get("columnName", ""),
                        "text": column.get("text", ""),
                        "display": column.get("display", ""),
                    }
                    for grid in vue_config.grids
                    for index, column in enumerate(
                        [*grid.get("headerColumns", []), *grid.get("bodyColumns", [])],
                        start=1,
                    )
                ],
            ),
        ),
        (
            "actions.csv",
            "Action-level contract including origin control, data touchpoints, and navigation count.",
            _csv(
                [
                    "functionName",
                    "actionKind",
                    "sourceComponentId",
                    "sourceComponentLabel",
                    "eventName",
                    "eventType",
                    "transactions",
                    "controlsComponents",
                    "readsDatasets",
                    "writesDatasets",
                    "navigationCount",
                    "navigationTargets",
                ],
                [
                    {
                        "functionName": item.get("functionName", ""),
                        "actionKind": item.get("actionKind", ""),
                        "sourceComponentId": item.get("sourceComponentId", ""),
                        "sourceComponentLabel": item.get("sourceComponentLabel", ""),
                        "eventName": item.get("eventName", ""),
                        "eventType": item.get("eventType", ""),
                        "transactions": _join(item.get("transactions", [])),
                        "controlsComponents": _join(item.get("controlsComponents", [])),
                        "readsDatasets": _join(item.get("readsDatasets", [])),
                        "writesDatasets": _join(item.get("writesDatasets", [])),
                        "navigationCount": len(item.get("navigationTargets", [])),
                        "navigationTargets": _join(
                            [
                                nav.get("pageId", "") or nav.get("target", "")
                                for nav in item.get("navigationTargets", [])
                            ]
                        ),
                    }
                    for item in vue_config.actions
                ],
            ),
        ),
        (
            "endpoints.csv",
            "Endpoint contract and backend trace summary per transaction.",
            _csv(
                [
                    "transactionId",
                    "serviceId",
                    "url",
                    "inputDatasets",
                    "outputDatasets",
                    "parameters",
                    "callbackFunction",
                    "controller",
                    "service",
                    "dao",
                    "sqlMapId",
                    "tableCandidates",
                    "querySummary",
                ],
                [
                    {
                        "transactionId": item.get("transactionId", ""),
                        "serviceId": item.get("serviceId", ""),
                        "url": item.get("url", ""),
                        "inputDatasets": _join(item.get("inputDatasets", [])),
                        "outputDatasets": _join(item.get("outputDatasets", [])),
                        "parameters": item.get("parameters", ""),
                        "callbackFunction": item.get("callbackFunction", ""),
                        "controller": item.get("controller", ""),
                        "service": item.get("service", ""),
                        "dao": item.get("dao", ""),
                        "sqlMapId": item.get("sqlMapId", ""),
                        "tableCandidates": _join(item.get("tableCandidates", [])),
                        "querySummary": item.get("querySummary", ""),
                    }
                    for item in vue_config.endpoints
                ],
            ),
        ),
        (
            "related-pages.csv",
            "Related screen contract with trigger and handoff metadata.",
            _csv(
                [
                    "navigationId",
                    "navigationType",
                    "triggerFunction",
                    "triggerComponentId",
                    "triggerComponentLabel",
                    "target",
                    "pageId",
                    "pageName",
                    "resolutionStatus",
                    "parameterBindings",
                ],
                [
                    {
                        "navigationId": item.get("navigationId", ""),
                        "navigationType": item.get("navigationType", ""),
                        "triggerFunction": item.get("triggerFunction", ""),
                        "triggerComponentId": item.get("triggerComponentId", ""),
                        "triggerComponentLabel": item.get("triggerComponentLabel", ""),
                        "target": item.get("target", ""),
                        "pageId": item.get("pageId", ""),
                        "pageName": item.get("pageName", ""),
                        "resolutionStatus": item.get("resolutionStatus", ""),
                        "parameterBindings": _join(item.get("parameterBindings", [])),
                    }
                    for item in vue_config.relatedPages
                ],
            ),
        ),
        (
            "file-blueprints.csv",
            "Planned frontend and backend files for the page conversion.",
            _csv(
                ["kind", "path", "purpose", "summary"],
                [
                    {
                        "kind": "frontend",
                        "path": file.path,
                        "purpose": file.purpose,
                        "summary": file.summary,
                    }
                    for file in plan.frontendFiles
                ]
                + [
                    {
                        "kind": "backend",
                        "path": file.path,
                        "purpose": file.purpose,
                        "summary": file.summary,
                    }
                    for file in plan.backendFiles
                ],
            ),
        ),
    ]

    files = _with_readme(table_specs, _render_stage2_readme(package, plan, vue_config, table_specs))
    files.update(
        build_stage2_hub_docs(
            package,
            plan,
            vue_config,
            [(name, description, description) for name, description, _content in table_specs],
        )
    )
    return files


def _with_readme(
    table_specs: list[tuple[str, str, str]],
    readme: str,
) -> dict[str, str]:
    files = {"README.md": readme}
    files.update({name: content for name, _description, content in table_specs})
    return files


def _render_stage1_readme(
    package: PageConversionPackage,
    table_specs: list[tuple[str, str, str]],
) -> str:
    page = package.page
    lines = [
        f"# Stage 1 Report Tables - {page.pageId or 'legacy-page'}",
        "",
        "This directory keeps high-cardinality analysis data in CSV so the human-facing Markdown reports can stay summary-oriented.",
        "Use the CSV files in this root for quick human review, and use `registries/` for the fuller machine-oriented exports.",
        "",
        "## Key Signals",
        "",
        f"- pageName: {page.pageName or 'unknown'}",
        f"- interactionPattern: {page.interactionPattern or 'unknown'}",
        f"- primaryDatasetId: {page.primaryDatasetId or 'unknown'}",
        f"- mainGridComponentId: {page.mainGridComponentId or 'unknown'}",
        f"- primaryTransactionIds: {_join(page.primaryTransactionIds) or 'none'}",
        f"- backendTraceCount: {len(package.backendTraces)}",
        f"- relatedPageCount: {len(package.relatedPages)}",
        "",
        "## Suggested Reading Order",
        "",
        "1. datasets.csv",
        "2. backend-traces.csv",
        "3. user-actions.csv",
        "4. related-pages.csv",
        "",
        "## Table Index",
        "",
    ]
    lines.extend([f"- `{name}`: {description}" for name, description, _content in table_specs])
    return "\n".join(lines)


def _render_stage2_readme(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    table_specs: list[tuple[str, str, str]],
) -> str:
    lines = [
        f"# Stage 2 Report Tables - {plan.pageId or 'legacy-page'}",
        "",
        "This directory keeps repeated implementation-contract data in CSV so the Stage 2 plan Markdown can focus on decisions, scope, and handoff notes.",
        "Use the CSV files in this root for quick human review, and use `registries/` plus `ai-prompts.md` for the fuller handoff pack.",
        "",
        "## Key Signals",
        "",
        f"- route: {plan.route or 'unknown'}",
        f"- vuePageName: {plan.vuePageName or 'unknown'}",
        f"- interactionPattern: {plan.interactionPattern or 'unknown'}",
        f"- primaryDatasetId: {package.page.primaryDatasetId or 'unknown'}",
        f"- mainGridComponentId: {package.page.mainGridComponentId or 'unknown'}",
        f"- searchControlCount: {len(vue_config.searchControls)}",
        f"- actionCount: {len(vue_config.actions)}",
        f"- endpointCount: {len(vue_config.endpoints)}",
        f"- relatedPageCount: {len(package.relatedPages)}",
        "",
        "## Suggested Reading Order",
        "",
        "1. search-controls.csv",
        "2. grids.csv",
        "3. actions.csv",
        "4. endpoints.csv",
        "5. related-pages.csv",
        "",
        "## Table Index",
        "",
    ]
    lines.extend([f"- `{name}`: {description}" for name, description, _content in table_specs])
    return "\n".join(lines)


def _csv(headers: list[str], rows: list[dict[str, object]]) -> str:
    buffer = StringIO()
    buffer.write("\ufeff")
    writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _stringify(row.get(key, "")) for key in headers})
    return buffer.getvalue()


def _join(values: list[object]) -> str:
    items = [_stringify(item) for item in values]
    return " | ".join(item for item in items if item)


def _stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
