from __future__ import annotations

import re

from am_bridge.models import (
    ConversionPlanModel,
    FileBlueprintModel,
    PageConversionPackage,
    VuePageConfigModel,
)


def build_conversion_plan(package: PageConversionPackage) -> ConversionPlanModel:
    page = package.page
    vue_page_name = derive_vue_page_name(page.pageId)
    route = derive_route(page.pageId)
    domain_slug = slug(page.pageId or "legacy-page")

    frontend_files = [
        FileBlueprintModel(
            path=f"frontend/src/pages/{domain_slug}/{vue_page_name}.vue",
            purpose="entry page",
            summary="Vue 3 page shell that preserves the legacy interaction flow and platform boundaries.",
        ),
        FileBlueprintModel(
            path=f"frontend/src/composables/use{vue_page_name}.ts",
            purpose="page orchestration",
            summary="Local state, initial load, primary action handlers, and realtime cleanup.",
        ),
        FileBlueprintModel(
            path=f"frontend/src/api/{slug(page.pageId or 'legacy-page')}.ts",
            purpose="api bridge",
            summary="Typed API client for the primary page use case and platform-aware headers.",
        ),
    ]

    backend_files = [
        FileBlueprintModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/web/{vue_page_name}Controller.java",
            purpose="spring controller",
            summary="Spring Boot controller that replaces MiPlatform endpoint contracts with REST-style endpoints.",
        ),
        FileBlueprintModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/service/{vue_page_name}Service.java",
            purpose="service interface",
            summary="Application service boundary for page use cases.",
        ),
        FileBlueprintModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/service/impl/{vue_page_name}ServiceImpl.java",
            purpose="service implementation",
            summary="Service implementation that adapts legacy DAO/query semantics into Spring Boot service logic.",
        ),
        FileBlueprintModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/dto/{vue_page_name}SearchCondition.java",
            purpose="request dto",
            summary="Request DTO inferred from the search-form dataset.",
        ),
        FileBlueprintModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/dto/{vue_page_name}Row.java",
            purpose="response dto",
            summary="Response DTO inferred from the primary result dataset.",
        ),
        FileBlueprintModel(
            path=f"backend/src/main/resources/mapper/{vue_page_name}Mapper.xml",
            purpose="query placeholder",
            summary="Optional MyBatis mapper/XML placeholder when the legacy SQL must be preserved first.",
        ),
    ]

    execution_steps = [
        "Stage 1: run package analysis and write review overrides if the primary dataset or backend trace is wrong.",
        "Stage 2: lock the primary dataset, primary transaction, platform boundaries, and file blueprint ownership.",
        "Stage 2 deliverable: emit a Vue page config JSON that downstream generation can consume directly.",
        "Stage 2 deliverable: emit a PM-facing test checklist so the page can be validated before signoff.",
        "Stage 3: generate starter files and let AI Pro fill business logic using the starter bundle plus review overrides.",
        "Verification: compare the generated page flow against the original datasets, transactions, and popup/subview flows.",
    ]

    verification_checks = [
        "Primary dataset matches the dominant result grid or primary business response.",
        "Search/code/view-state datasets are not treated as equal peers to the primary result dataset.",
        "Each primary transaction has a resolved or manually corrected backend route chain.",
        "Popup/subview targets are treated as separate related screens, not merged silently into the current page.",
        "No shared platform function is reimplemented locally without explicit approval.",
    ]

    ai_prompts = {
        "review": build_review_prompt(package),
        "frontend": build_frontend_prompt(package, frontend_files),
        "backend": build_backend_prompt(package, backend_files),
    }

    return ConversionPlanModel(
        packageId=package.packageId,
        pageId=page.pageId,
        route=route,
        vuePageName=vue_page_name,
        interactionPattern=page.interactionPattern,
        frontendFiles=frontend_files,
        backendFiles=backend_files,
        executionSteps=execution_steps,
        verificationChecks=verification_checks,
        aiPrompts=ai_prompts,
    )


def build_vue_page_config(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
) -> VuePageConfigModel:
    page = package.page

    datasets = [
        {
            "datasetId": dataset.datasetId,
            "role": dataset.role,
            "primaryUsage": dataset.primaryUsage,
            "columns": [column.name for column in dataset.columns],
            "boundComponents": dataset.boundComponents,
        }
        for dataset in page.datasets
    ]

    grids = []
    search_controls = []
    for component in page.components:
        component_summary = {
            "componentId": component.componentId,
            "componentType": component.componentType,
            "layoutGroup": component.layoutGroup,
            "datasetId": _extract_component_dataset(component),
            "events": component.events,
        }
        if component.componentType == "Grid":
            grid_meta = component.properties.get("gridMeta", {})
            component_summary["columns"] = [
                item.get("columnName", "")
                for item in grid_meta.get("bodyColumns", [])
                if item.get("columnName")
            ]
            grids.append(component_summary)
        elif component.layoutGroup == "search-panel" or component.componentType in {
            "Combo",
            "Edit",
            "MaskEdit",
            "Calendar",
        }:
            search_controls.append(component_summary)

    actions = [
        {
            "functionName": function.functionName,
            "transactions": function.callsTransactions,
            "controlsComponents": function.controlsComponents,
            "readsDatasets": function.readsDatasets,
            "writesDatasets": function.writesDatasets,
        }
        for function in page.functions
        if function.functionType == "event-handler"
    ]

    endpoints = [
        {
            "transactionId": transaction.transactionId,
            "url": transaction.url,
            "inputDatasets": transaction.inputDatasets,
            "outputDatasets": transaction.outputDatasets,
            "controller": _trace_field(package, transaction.transactionId, "controller"),
            "service": _trace_field(package, transaction.transactionId, "service"),
            "dao": _trace_field(package, transaction.transactionId, "dao"),
            "sqlMapId": _trace_field(package, transaction.transactionId, "sqlMapId"),
        }
        for transaction in page.transactions
    ]

    related_pages = [
        {
            "navigationType": item.navigationType,
            "triggerFunction": item.triggerFunction,
            "target": item.target,
            "resolvedPath": item.resolvedPath,
            "pageId": item.pageId,
            "pageName": item.pageName,
            "pageType": item.pageType,
            "resolutionStatus": item.resolutionStatus,
        }
        for item in package.relatedPages
    ]

    return VuePageConfigModel(
        pageId=page.pageId,
        pageName=page.pageName,
        legacySourceFile=page.legacy.sourceFile,
        pageType=page.pageType,
        vuePageName=plan.vuePageName,
        route=plan.route,
        interactionPattern=page.interactionPattern,
        primaryDatasetId=page.primaryDatasetId,
        mainGridComponentId=page.mainGridComponentId,
        primaryTransactionIds=page.primaryTransactionIds,
        datasets=datasets,
        grids=grids,
        searchControls=search_controls,
        actions=actions,
        endpoints=endpoints,
        relatedPages=related_pages,
        frontendFiles=[item.path for item in plan.frontendFiles],
        backendFiles=[item.path for item in plan.backendFiles],
        verificationChecks=plan.verificationChecks,
    )


def generate_plan_report(plan: ConversionPlanModel, package: PageConversionPackage) -> str:
    lines = [
        "# Stage 2 - Conversion Plan",
        "",
        f"- packageId: {plan.packageId}",
        f"- pageId: {plan.pageId}",
        f"- route: {plan.route}",
        f"- vuePageName: {plan.vuePageName}",
        f"- interactionPattern: {plan.interactionPattern or 'unknown'}",
        "",
        "## Frontend Files",
        "",
    ]
    lines.extend(
        [f"- {item.path}: {item.summary}" for item in plan.frontendFiles] or ["- None"]
    )
    lines.extend(["", "## Backend Files", ""])
    lines.extend(
        [f"- {item.path}: {item.summary}" for item in plan.backendFiles] or ["- None"]
    )
    lines.extend(["", "## Execution Steps", ""])
    lines.extend([f"- {item}" for item in plan.executionSteps])
    lines.extend(["", "## Verification Checks", ""])
    lines.extend([f"- {item}" for item in plan.verificationChecks])
    if package.relatedPages:
        lines.extend(["", "## Related Screens", ""])
        lines.extend(
            [
                f"- {item.navigationType}:{item.target} -> {item.pageId or 'unresolved'} ({item.resolutionStatus})"
                for item in package.relatedPages
            ]
        )
    lines.extend(["", "## AI Prompts", ""])
    for key, value in plan.aiPrompts.items():
        lines.extend([f"### {key}", "", "```text", value, "```", ""])
    lines.extend(["## Package Hints", ""])
    lines.extend([f"- {item}" for item in package.aiHints] or ["- None"])
    return "\n".join(lines)


def generate_pm_test_checklist(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
) -> str:
    page = package.page
    primary_transactions = page.primaryTransactionIds or [item["transactionId"] for item in vue_config.endpoints]
    related_pages = package.relatedPages
    search_controls = [item["componentId"] for item in vue_config.searchControls if item.get("componentId")]
    main_grid = page.mainGridComponentId or "unconfirmed"
    primary_dataset = page.primaryDatasetId or "unconfirmed"
    secondary_datasets = ", ".join(page.secondaryDatasetIds) or "none locked"

    lines = [
        f"# PM Test Checklist - {page.pageId or 'legacy-page'}",
        "",
        "## Scope",
        "",
        f"- Legacy page: {page.legacy.sourceFile or 'unknown'}",
        f"- Page name: {page.pageName or 'unknown'}",
        f"- Page type: {page.pageType or 'unknown'}",
        f"- Target route: {plan.route}",
        f"- Vue page: {plan.vuePageName}",
        f"- Interaction pattern: {page.interactionPattern or 'unknown'}",
        f"- Primary dataset: {primary_dataset}",
        f"- Secondary datasets: {secondary_datasets}",
        f"- Main grid: {main_grid}",
        f"- Primary transactions: {', '.join(primary_transactions) if primary_transactions else 'none locked'}",
        "",
        "## PM Smoke Checks",
        "",
        "- [ ] The page opens without blocking errors and shows the intended business title/context.",
        f"- [ ] The dominant business area is centered on dataset `{primary_dataset}` and grid/component `{main_grid}`.",
        "- [ ] Search, result, and reference/code datasets are clearly separated in the rendered screen behavior.",
    ]

    if search_controls:
        lines.append(f"- [ ] Search controls are present and usable: {', '.join(search_controls)}.")
    else:
        lines.append("- [ ] Confirm whether the page should have explicit search controls or is load-driven.")

    lines.extend(["", "## Data Retrieval Checks", ""])
    for transaction_id in primary_transactions:
        endpoint = next(
            (item for item in vue_config.endpoints if item["transactionId"] == transaction_id),
            None,
        )
        trace_summary = _describe_endpoint_check(endpoint, package, transaction_id)
        lines.append(f"- [ ] {trace_summary}")
    if not primary_transactions:
        lines.append("- [ ] Confirm the primary business transaction before implementation continues.")

    lines.extend(["", "## Functional Scenario Checks", ""])
    action_lines = _build_action_checklist_items(package, primary_transactions)
    lines.extend(action_lines or ["- [ ] No actionable event handlers were inferred. Confirm manual scenarios with PM."])

    lines.extend(["", "## Backend And Integration Spot Checks", ""])
    backend_lines = _build_backend_checklist_items(package, vue_config, primary_transactions)
    lines.extend(
        backend_lines
        or ["- [ ] Backend chain was not resolved. Confirm controller/service/DAO ownership before coding."]
    )

    lines.extend(["", "## Related Screen Checks", ""])
    if related_pages:
        for related in related_pages:
            if related.resolutionStatus == "resolved":
                lines.append(
                    "- [ ] "
                    f"`{related.triggerFunction or related.navigationType}` opens `{related.pageId or related.target}` "
                    f"from legacy target `{related.target}` as a separate related screen with the expected handoff."
                )
            else:
                lines.append(
                    "- [ ] "
                    f"Clarify unresolved related target `{related.target}` before merging it into any current-page implementation."
                )
    else:
        lines.append("- [ ] Confirm whether this page has popup/subview navigation that still needs to be modeled.")

    lines.extend(["", "## Negative And Regression Checks", ""])
    lines.extend(
        [
            "- [ ] Empty-result and no-data cases behave safely and keep the page usable.",
            "- [ ] Validation and business error messages match the original user flow expectations.",
            "- [ ] Backend failure or timeout cases do not leave the page in an inconsistent state.",
            "- [ ] Shared platform functions were not reimplemented locally without approval.",
        ]
    )

    lines.extend(["", "## Open Questions To Resolve", ""])
    if package.openQuestions:
        lines.extend([f"- [ ] {item}" for item in package.openQuestions])
    else:
        lines.append("- [ ] No unresolved questions are currently recorded. Reconfirm after first implementation pass.")

    lines.extend(["", "## Signoff Guidance", ""])
    lines.extend(
        [
            "- [ ] Lock PM signoff only after stage2 artifacts, Vue config, and this checklist are internally consistent.",
            "- [ ] If a checklist item fails because the analysis looks wrong, update review.json and rerun the relevant stage.",
        ]
    )
    return "\n".join(lines)


def build_review_prompt(package: PageConversionPackage) -> str:
    page = package.page
    return (
        f"Review page {page.pageId}. Confirm whether primaryDatasetId={page.primaryDatasetId or 'unknown'} "
        f"really represents the dominant business result. Distinguish result/search/code/view-state datasets, "
        f"correct backend traces if needed, and write corrections into the review JSON before stage 2."
    )


def build_frontend_prompt(
    package: PageConversionPackage,
    files: list[FileBlueprintModel],
) -> str:
    page = package.page
    return (
        f"Using the stage 1 package, stage 2 plan, and Vue page config for {page.pageId}, implement the frontend files "
        f"({', '.join(item.path for item in files)}). Preserve the interaction pattern {page.interactionPattern or 'unknown'}, "
        f"treat {page.primaryDatasetId or 'the primary dataset'} as the main business result, and keep platform features out of local reimplementation."
    )


def build_backend_prompt(
    package: PageConversionPackage,
    files: list[FileBlueprintModel],
) -> str:
    page = package.page
    primary_trace = _find_primary_trace(package)
    backend_hint = (
        f"Map the legacy route {primary_trace.url} through {primary_trace.controllerClass}.{primary_trace.controllerMethod}"
        if primary_trace and primary_trace.controllerMethod
        else "Map the primary legacy transactions into Spring Boot endpoints"
    )
    return (
        f"Using the stage 1 package, stage 2 plan, and Vue page config for {page.pageId}, implement the backend files "
        f"({', '.join(item.path for item in files)}). {backend_hint}. Preserve business behavior, but expose cleaner Spring Boot request/response DTOs."
    )


def derive_vue_page_name(page_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", " ", page_id or "LegacyPage").strip()
    parts = normalized.split() or ["Legacy", "Page"]
    return "".join(part[:1].upper() + part[1:] for part in parts) + "Page"


def derive_route(page_id: str) -> str:
    kebab = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", page_id or "legacy-page")
    kebab = re.sub(r"[^A-Za-z0-9]+", "-", kebab).strip("-").lower()
    return "/" + (kebab or "legacy-page")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "legacy-page"


def _find_primary_trace(package: PageConversionPackage):
    if not package.backendTraces:
        return None
    for transaction_id in package.page.primaryTransactionIds:
        trace = next(
            (item for item in package.backendTraces if item.transactionId == transaction_id),
            None,
        )
        if trace is not None:
            return trace
    return package.backendTraces[0]


def _extract_component_dataset(component) -> str:
    for key in ("BindDataset", "InnerDataset"):
        value = component.properties.get(key)
        if value:
            return str(value)
    return ""


def _trace_field(package: PageConversionPackage, transaction_id: str, field_name: str) -> str:
    trace = next((item for item in package.backendTraces if item.transactionId == transaction_id), None)
    if trace is None:
        return ""
    if field_name == "controller":
        return ".".join(item for item in [trace.controllerClass, trace.controllerMethod] if item)
    if field_name == "service":
        return ".".join(item for item in [trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod] if item)
    if field_name == "dao":
        return ".".join(item for item in [trace.daoClass, trace.daoMethod] if item)
    return str(getattr(trace, field_name, "") or "")


def _describe_endpoint_check(
    endpoint: dict[str, object] | None,
    package: PageConversionPackage,
    transaction_id: str,
) -> str:
    if endpoint is None:
        return f"`{transaction_id}` is mapped and its result datasets are validated against the legacy behavior."

    outputs = ", ".join(endpoint.get("outputDatasets", [])) or "no output dataset captured"
    controller = endpoint.get("controller") or _trace_field(package, transaction_id, "controller") or "controller unresolved"
    return (
        f"`{transaction_id}` calls `{endpoint.get('url') or 'legacy url unresolved'}` via `{controller}` "
        f"and refreshes `{outputs}`."
    )


def _build_action_checklist_items(
    package: PageConversionPackage,
    primary_transactions: list[str],
) -> list[str]:
    items: list[str] = []
    primary_transaction_set = set(primary_transactions)
    for function in package.page.functions:
        if function.functionType != "event-handler":
            continue
        related_transactions = function.callsTransactions
        if primary_transaction_set and not primary_transaction_set.intersection(related_transactions):
            if not related_transactions and not function.controlsComponents:
                continue
        reads = ", ".join(function.readsDatasets) or "no read dataset captured"
        writes = ", ".join(function.writesDatasets) or "no write dataset captured"
        controls = ", ".join(function.controlsComponents) or "no direct control target captured"
        transactions = ", ".join(related_transactions) or "no direct transaction captured"
        items.append(
            "- [ ] "
            f"`{function.functionName}` behaves as expected. Transactions: {transactions}. "
            f"Reads: {reads}. Writes: {writes}. Controls: {controls}."
        )
    return items


def _build_backend_checklist_items(
    package: PageConversionPackage,
    vue_config: VuePageConfigModel,
    primary_transactions: list[str],
) -> list[str]:
    items: list[str] = []
    preferred = set(primary_transactions)
    endpoints = vue_config.endpoints
    if preferred:
        endpoints = [item for item in endpoints if item["transactionId"] in preferred] or endpoints
    for endpoint in endpoints:
        transaction_id = str(endpoint["transactionId"])
        dao = endpoint.get("dao") or _trace_field(package, transaction_id, "dao") or "DAO unresolved"
        sql_map_id = endpoint.get("sqlMapId") or _trace_field(package, transaction_id, "sqlMapId") or "SQL map unresolved"
        items.append(
            "- [ ] "
            f"`{transaction_id}` keeps the intended backend chain `{endpoint.get('controller') or 'controller unresolved'} -> "
            f"{endpoint.get('service') or 'service unresolved'} -> {dao}` and preserves SQL behavior `{sql_map_id}`."
        )
    return items
