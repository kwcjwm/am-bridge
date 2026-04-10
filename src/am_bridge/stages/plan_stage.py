from __future__ import annotations

import re
from typing import Any

from am_bridge.models import (
    ConversionPlanModel,
    FileBlueprintModel,
    PageConversionPackage,
    VuePageConfigModel,
)
from am_bridge.reporting import join_values, markdown_link, render_contents, render_csv, render_markdown_table


def build_conversion_plan(package: PageConversionPackage) -> ConversionPlanModel:
    page = package.page
    vue_page_name = derive_vue_page_name(page.pageId)
    route = derive_route(page.pageId)
    domain_slug = slug(page.pageId or "legacy-page")
    stage2_contract = _build_stage2_contract(package)

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
            path=f"backend/src/main/java/com/example/am/{domain_slug}/mapper/{vue_page_name}Mapper.java",
            purpose="mybatis mapper",
            summary="Mapper interface for primary page queries and inferred lookup datasets.",
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
        "review": build_review_prompt(package, stage2_contract),
        "frontend": build_frontend_prompt(package, frontend_files, stage2_contract),
        "backend": build_backend_prompt(package, backend_files, stage2_contract),
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
    stage2_contract = _build_stage2_contract(package)
    primary_endpoint = next(
        (
            item
            for item in stage2_contract["endpoints"]
            if item.get("transactionId") in page.primaryTransactionIds
        ),
        stage2_contract["endpoints"][0] if stage2_contract["endpoints"] else {},
    )

    return VuePageConfigModel(
        pageId=page.pageId,
        pageName=page.pageName,
        legacySourceFile=page.legacy.sourceFile,
        legacyTitle=page.legacy.title,
        initialEvent=page.legacy.initialEvent,
        pageType=page.pageType,
        vuePageName=plan.vuePageName,
        route=plan.route,
        interactionPattern=page.interactionPattern,
        primaryDatasetId=page.primaryDatasetId,
        mainGridComponentId=page.mainGridComponentId,
        primaryTransactionIds=page.primaryTransactionIds,
        datasets=stage2_contract["datasets"],
        bindings=[
            {
                "componentId": item.componentId,
                "datasetId": item.datasetId,
                "columnName": item.columnName,
                "bindingType": item.bindingType,
                "direction": item.direction,
                "sourceRefs": item.sourceRefs,
            }
            for item in page.bindings
        ],
        grids=stage2_contract["grids"],
        searchControls=stage2_contract["searchControls"],
        actions=stage2_contract["actions"],
        endpoints=stage2_contract["endpoints"],
        primaryEndpoint=primary_endpoint,
        backendTraces=stage2_contract["endpoints"],
        navigation=[
            {
                "navigationId": item.navigationId,
                "triggerFunction": item.triggerFunction,
                "navigationType": item.navigationType,
                "target": item.target,
                "parameterBindings": item.parameterBindings,
                "returnHandling": item.returnHandling,
            }
            for item in page.navigation
        ],
        relatedPages=stage2_contract["relatedPages"],
        stateRules=stage2_contract["stateRules"],
        validationRules=stage2_contract["validationRules"],
        messages=stage2_contract["messages"],
        frontendFiles=[item.path for item in plan.frontendFiles],
        backendFiles=[item.path for item in plan.backendFiles],
        verificationChecks=plan.verificationChecks,
    )


def generate_plan_report(
    plan: ConversionPlanModel,
    package: PageConversionPackage,
    registry_dir: str = "",
    prompt_pack_path: str = "",
    artifact_links: dict[str, str] | None = None,
) -> str:
    return _generate_plan_report_v2(
        plan,
        package,
        registry_dir=registry_dir,
        prompt_pack_path=prompt_pack_path,
        artifact_links=artifact_links,
    )


def generate_plan_registries(plan: ConversionPlanModel, package: PageConversionPackage) -> dict[str, str]:
    return {
        "file-blueprints.csv": render_csv(_file_blueprint_rows(plan)),
        "verification-checks.csv": render_csv(_verification_rows(plan)),
        "related-screens.csv": render_csv(_related_screen_rows(package)),
        "execution-steps.csv": render_csv(_execution_step_rows(plan)),
    }


def generate_plan_prompt_pack(plan: ConversionPlanModel) -> str:
    lines = [f"# AI Prompt Pack - {plan.pageId or 'legacy-page'}", ""]
    for key, value in plan.aiPrompts.items():
        lines.extend([f"## {key}", "", "```text", value, "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def _generate_plan_report_v2(
    plan: ConversionPlanModel,
    package: PageConversionPackage,
    registry_dir: str = "",
    prompt_pack_path: str = "",
    artifact_links: dict[str, str] | None = None,
) -> str:
    sections: list[tuple[str, list[str]]] = [
        (
            "Target Architecture Summary",
            [
                f"- Package: `{plan.packageId}`",
                f"- Target route: `{plan.route}`",
                f"- Vue page name: `{plan.vuePageName}`",
                f"- Interaction pattern: `{plan.interactionPattern or 'unknown'}`",
                f"- Frontend files: `{len(plan.frontendFiles)}` / backend files: `{len(plan.backendFiles)}`",
            ],
        ),
        (
            "Locked Assumptions",
            [
                f"- Primary dataset remains `{package.page.primaryDatasetId or 'unknown'}` unless review overrides change it.",
                f"- Primary transactions locked for this page: `{join_values(package.page.primaryTransactionIds, 'none locked')}`.",
                "- Popup/subview targets stay separated from the current page implementation.",
                "- Shared platform behaviors are not reimplemented locally without explicit approval.",
            ],
        ),
        (
            "Implementation Scope",
            render_markdown_table(
                [
                    ("Layer", "layer"),
                    ("Count", "count"),
                    ("Representative Files", "examples"),
                ],
                _implementation_scope_rows(plan),
            ),
        ),
        (
            "File Blueprint Summary",
            render_markdown_table(
                [
                    ("Path", "path"),
                    ("Purpose", "purpose"),
                    ("Summary", "summary"),
                ],
                _file_blueprint_rows(plan),
            ),
        ),
        (
            "Execution Sequence",
            [f"1. {item}" for item in plan.executionSteps],
        ),
        (
            "Verification Strategy",
            [f"- {item}" for item in plan.verificationChecks],
        ),
        (
            f"Manual Decisions Pending ({len(package.openQuestions)})",
            [f"- {item}" for item in package.openQuestions] or ["- None"],
        ),
    ]

    if package.relatedPages:
        sections.append(
            (
                f"Related Screens ({len(package.relatedPages)})",
                render_markdown_table(
                    [
                        ("Type", "type"),
                        ("Target", "target"),
                        ("Resolved Page", "pageId"),
                        ("Status", "status"),
                    ],
                    _related_screen_rows(package),
                ),
            )
        )

    sections.append(
        (
            "Evidence Registry Links",
            _plan_artifact_index_lines(
                registry_dir=registry_dir,
                registry_files=list(generate_plan_registries(plan, package).keys()),
                prompt_pack_path=prompt_pack_path,
                artifact_links=artifact_links,
            ),
        )
    )

    lines = ["# Stage 2 - Conversion Plan", ""]
    lines.extend(render_contents([section_title for section_title, _body in sections]))
    for section_title, body in sections:
        lines.append(f"## {section_title}")
        lines.append("")
        lines.extend(body or ["- None"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _implementation_scope_rows(plan: ConversionPlanModel) -> list[dict[str, str]]:
    return [
        {
            "layer": "Frontend",
            "count": str(len(plan.frontendFiles)),
            "examples": join_values([item.path for item in plan.frontendFiles[:3]], "none"),
        },
        {
            "layer": "Backend",
            "count": str(len(plan.backendFiles)),
            "examples": join_values([item.path for item in plan.backendFiles[:3]], "none"),
        },
    ]


def _file_blueprint_rows(plan: ConversionPlanModel) -> list[dict[str, str]]:
    return [
        {
            "path": item.path,
            "purpose": item.purpose,
            "summary": item.summary,
        }
        for item in [*plan.frontendFiles, *plan.backendFiles]
    ]


def _verification_rows(plan: ConversionPlanModel) -> list[dict[str, str]]:
    return [{"check": item} for item in plan.verificationChecks]


def _execution_step_rows(plan: ConversionPlanModel) -> list[dict[str, str]]:
    return [{"step": str(index + 1), "description": item} for index, item in enumerate(plan.executionSteps)]


def _related_screen_rows(package: PageConversionPackage) -> list[dict[str, str]]:
    return [
        {
            "type": item.navigationType or "unknown",
            "target": item.target or item.navigationId,
            "pageId": item.pageId or "unresolved",
            "status": item.resolutionStatus or "unknown",
        }
        for item in package.relatedPages
    ]


def _plan_artifact_index_lines(
    registry_dir: str,
    registry_files: list[str],
    prompt_pack_path: str,
    artifact_links: dict[str, str] | None = None,
) -> list[str]:
    lines: list[str] = []
    for label, target in (artifact_links or {}).items():
        lines.append(f"- {label}: {markdown_link(label, target)}")
    if prompt_pack_path:
        lines.append(f"- Prompt pack: {markdown_link(prompt_pack_path, prompt_pack_path)}")
    if registry_dir:
        lines.append(f"- Registry directory: {markdown_link(registry_dir, registry_dir)}")
        for file_name in registry_files:
            lines.append(f"- Registry: {markdown_link(file_name, f'{registry_dir}/{file_name}')}")
    return lines or ["- No sidecar artifacts recorded."]


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


def build_review_prompt(
    package: PageConversionPackage,
    stage2_contract: dict[str, list[dict[str, Any]]],
) -> str:
    page = package.page
    primary_actions = [
        item["functionName"]
        for item in stage2_contract["actions"]
        if item.get("transactions") or item.get("navigationTargets")
    ]
    return (
        f"Review page {page.pageId}. Confirm whether primaryDatasetId={page.primaryDatasetId or 'unknown'} "
        f"really represents the dominant business result. Distinguish result/search/code/view-state datasets, "
        f"correct backend traces if needed, and write corrections into the review JSON before stage 2. "
        f"Validate the stage2 contract for actions {', '.join(primary_actions) or 'none captured'}, "
        f"search controls {_summarize_search_controls(stage2_contract['searchControls'])}, "
        f"and related navigation {_summarize_related_pages(stage2_contract['relatedPages'])}."
    )


def build_frontend_prompt(
    package: PageConversionPackage,
    files: list[FileBlueprintModel],
    stage2_contract: dict[str, list[dict[str, Any]]],
) -> str:
    page = package.page
    grid_summary = _summarize_grids(stage2_contract["grids"])
    search_summary = _summarize_search_controls(stage2_contract["searchControls"])
    action_summary = _summarize_actions(stage2_contract["actions"])
    rule_summary = _summarize_rule_contract(
        stage2_contract["validationRules"],
        stage2_contract["stateRules"],
        stage2_contract["messages"],
    )
    navigation_summary = _summarize_related_pages(stage2_contract["relatedPages"])
    return (
        f"Using the stage 1 package, stage 2 plan, and Vue page config for {page.pageId}, implement the frontend files "
        f"({', '.join(item.path for item in files)}). Preserve the interaction pattern {page.interactionPattern or 'unknown'}, "
        f"treat {page.primaryDatasetId or 'the primary dataset'} as the main business result, and keep platform features out of local reimplementation. "
        f"Build the search area from {search_summary}. Render the main data grid using {grid_summary}. "
        f"Implement action flows {action_summary}. Respect validation/state/message rules: {rule_summary}. "
        f"Keep related-screen handling explicit: {navigation_summary}."
    )


def build_backend_prompt(
    package: PageConversionPackage,
    files: list[FileBlueprintModel],
    stage2_contract: dict[str, list[dict[str, Any]]],
) -> str:
    page = package.page
    primary_trace = _find_primary_trace(package)
    backend_hint = (
        f"Map the legacy route {primary_trace.url} through {primary_trace.controllerClass}.{primary_trace.controllerMethod}"
        if primary_trace and primary_trace.controllerMethod
        else "Map the primary legacy transactions into Spring Boot endpoints"
    )
    endpoint_summary = _summarize_endpoints(stage2_contract["endpoints"])
    action_summary = _summarize_actions(stage2_contract["actions"])
    return (
        f"Using the stage 1 package, stage 2 plan, and Vue page config for {page.pageId}, implement the backend files "
        f"({', '.join(item.path for item in files)}). {backend_hint}. Preserve business behavior, but expose cleaner Spring Boot request/response DTOs. "
        f"Honor endpoint contracts {endpoint_summary}. Align request parameters, callbacks, and button/onload flows with {action_summary}."
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


def _build_stage2_contract(package: PageConversionPackage) -> dict[str, list[dict[str, Any]]]:
    page = package.page
    component_by_id = {item.componentId: item for item in page.components if item.componentId}
    event_by_handler = _group_by(page.events, lambda item: item.handlerFunction)
    validations_by_target = _group_by(page.validationRules, lambda item: item.targetField)
    validations_by_source = _group_by(page.validationRules, lambda item: item.sourceFunction)
    state_rules_by_source = _group_by(page.stateRules, lambda item: item.sourceFunction)
    messages_by_source = _group_by(page.messages, lambda item: item.sourceFunction)
    navigation_by_trigger = _group_by(page.navigation, lambda item: item.triggerFunction)

    datasets = [
        {
            "datasetId": dataset.datasetId,
            "role": dataset.role,
            "primaryUsage": dataset.primaryUsage,
            "columns": [column.name for column in dataset.columns],
            "columnMeta": [
                {
                    "name": column.name,
                    "type": column.type,
                    "size": column.size,
                    "required": column.required,
                    "semanticType": column.semanticType,
                    "notes": column.notes,
                }
                for column in dataset.columns
            ],
            "defaultRecords": dataset.defaultRecords,
            "usageContexts": dataset.usageContexts,
            "boundComponents": dataset.boundComponents,
            "salienceScore": dataset.salienceScore,
            "salienceReasons": dataset.salienceReasons,
            "sourceRefs": dataset.sourceRefs,
        }
        for dataset in page.datasets
    ]

    grids: list[dict[str, Any]] = []
    search_controls: list[dict[str, Any]] = []
    for component in page.components:
        if component.componentType == "Grid":
            grids.append(_build_grid_contract(page, component))
        elif component.layoutGroup == "search-panel" or component.componentType in {
            "Button",
            "Combo",
            "Edit",
            "MaskEdit",
            "Calendar",
        }:
            search_controls.append(
                _build_search_control_contract(page, component, validations_by_target)
            )

    related_pages = [
        _build_related_page_contract(package, item, component_by_id, event_by_handler)
        for item in package.relatedPages
    ]
    related_pages_by_trigger = _group_by(related_pages, lambda item: item.get("triggerFunction", ""))
    endpoints = [_build_endpoint_contract(package, transaction) for transaction in page.transactions]

    actions = [
        _build_action_contract(
            package,
            function,
            event_by_handler,
            validations_by_source,
            state_rules_by_source,
            messages_by_source,
            navigation_by_trigger,
            related_pages_by_trigger,
            component_by_id,
            endpoints,
        )
        for function in page.functions
        if function.functionType == "event-handler"
    ]

    state_rules = [
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

    validation_rules = [
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

    messages = [
        {
            "messageId": item.messageId,
            "sourceType": item.sourceType,
            "messageType": item.messageType,
            "text": item.text,
            "sourceFunction": item.sourceFunction,
            "targetComponentId": item.targetComponentId,
            "i18nKeyCandidate": item.i18nKeyCandidate,
            "sourceRefs": item.sourceRefs,
        }
        for item in page.messages
    ]

    return {
        "datasets": datasets,
        "grids": grids,
        "searchControls": search_controls,
        "actions": actions,
        "endpoints": endpoints,
        "relatedPages": related_pages,
        "stateRules": state_rules,
        "validationRules": validation_rules,
        "messages": messages,
    }


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


def _group_by(items: list[Any], key) -> dict[str, list[Any]]:
    groups: dict[str, list[Any]] = {}
    for item in items:
        group_key = str(key(item) or "")
        groups.setdefault(group_key, []).append(item)
    return groups


def _build_grid_contract(page, component) -> dict[str, Any]:
    grid_meta = component.properties.get("gridMeta", {})
    body_columns = [_normalize_grid_column(item) for item in grid_meta.get("bodyColumns", [])]
    head_columns = [_normalize_grid_column(item) for item in grid_meta.get("headColumns", [])]
    dataset_id = _extract_component_dataset(component)
    return {
        "componentId": component.componentId,
        "componentType": component.componentType,
        "layoutGroup": component.layoutGroup,
        "datasetId": dataset_id,
        "events": component.events,
        "columns": [item["columnName"] for item in body_columns if item.get("columnName")],
        "headerColumns": head_columns,
        "bodyColumns": body_columns,
        "headerTexts": [item["text"] for item in head_columns if item.get("text")],
        "datasetColumns": _dataset_column_names(page, dataset_id),
        "bindings": _bindings_for_component(page, component.componentId),
        "layout": _component_layout(component),
        "sourceRefs": component.sourceRefs,
    }


def _build_search_control_contract(
    page,
    component,
    validations_by_target: dict[str, list[Any]],
) -> dict[str, Any]:
    dataset_id = _extract_component_dataset(component)
    bindings = _bindings_for_component(page, component.componentId)
    bound_column = _infer_component_bound_column(component, bindings)
    handler_names = [
        str(component.properties.get(event_name, "") or "")
        for event_name in component.events
        if component.properties.get(event_name)
    ]
    return {
        "componentId": component.componentId,
        "componentType": component.componentType,
        "layoutGroup": component.layoutGroup,
        "datasetId": dataset_id,
        "events": component.events,
        "controlRole": _classify_search_control(component),
        "label": _infer_component_label(page, component),
        "text": _component_text(component),
        "boundColumn": bound_column,
        "requestFieldCandidate": bound_column,
        "bindingType": bindings[0]["bindingType"] if len(bindings) == 1 else "",
        "bindings": bindings,
        "datasetBinding": {
            "datasetId": dataset_id,
            "codeColumn": str(component.properties.get("CodeColumn", "") or ""),
            "displayColumn": str(component.properties.get("DataColumn", "") or ""),
            "valueColumn": bound_column,
        },
        "codeColumn": str(component.properties.get("CodeColumn", "") or ""),
        "dataColumn": str(component.properties.get("DataColumn", "") or ""),
        "innerDataset": str(component.properties.get("InnerDataset", "") or ""),
        "triggerActions": [item for item in handler_names if item],
        "validationRules": [
            {
                "ruleId": item.ruleId,
                "validationType": item.validationType,
                "triggerTiming": item.triggerTiming,
                "expression": item.expression,
                "message": item.message,
                "sourceFunction": item.sourceFunction,
            }
            for item in validations_by_target.get(component.componentId, [])
        ],
        "layout": _component_layout(component),
        "sourceRefs": component.sourceRefs,
    }


def _build_related_page_contract(
    package: PageConversionPackage,
    item,
    component_by_id: dict[str, Any],
    event_by_handler: dict[str, list[Any]],
) -> dict[str, Any]:
    navigation = next(
        (entry for entry in package.page.navigation if entry.navigationId == item.navigationId),
        None,
    )
    trigger_component = _resolve_trigger_component(
        item.triggerFunction,
        event_by_handler,
        component_by_id,
    )
    return {
        "navigationId": item.navigationId,
        "navigationType": item.navigationType,
        "triggerFunction": item.triggerFunction,
        "triggerComponentId": trigger_component.componentId if trigger_component else "",
        "triggerComponentLabel": _component_label_or_id(trigger_component),
        "target": item.target,
        "resolvedPath": item.resolvedPath,
        "pageId": item.pageId,
        "pageName": item.pageName,
        "pageType": item.pageType,
        "resolutionStatus": item.resolutionStatus,
        "parameterBindings": navigation.parameterBindings if navigation else [],
        "returnHandling": navigation.returnHandling if navigation else "",
    }


def _build_endpoint_contract(package: PageConversionPackage, transaction) -> dict[str, Any]:
    trace = next(
        (item for item in package.backendTraces if item.transactionId == transaction.transactionId),
        None,
    )
    return {
        "transactionId": transaction.transactionId,
        "serviceId": transaction.serviceId,
        "url": transaction.url,
        "inputDatasets": transaction.inputDatasets,
        "outputDatasets": transaction.outputDatasets,
        "parameters": transaction.parameters,
        "callbackFunction": transaction.callbackFunction,
        "wrapperFunction": transaction.wrapperFunction,
        "apiCandidate": transaction.apiCandidate,
        "controller": _trace_field(package, transaction.transactionId, "controller"),
        "service": _trace_field(package, transaction.transactionId, "service"),
        "dao": _trace_field(package, transaction.transactionId, "dao"),
        "sqlMapId": _trace_field(package, transaction.transactionId, "sqlMapId"),
        "requestMapping": trace.requestMapping if trace else "",
        "controllerClass": trace.controllerClass if trace else "",
        "controllerMethod": trace.controllerMethod if trace else "",
        "controllerMethodSignature": trace.controllerMethodSignature if trace else "",
        "requestDtoType": trace.requestDtoType if trace else "",
        "responseCarrierType": trace.responseCarrierType if trace else "",
        "serviceBeanName": trace.serviceBeanName if trace else "",
        "serviceInterface": trace.serviceInterface if trace else "",
        "serviceImplClass": trace.serviceImplClass if trace else "",
        "serviceMethod": trace.serviceMethod if trace else "",
        "daoClass": trace.daoClass if trace else "",
        "daoMethod": trace.daoMethod if trace else "",
        "sqlMapFile": trace.sqlMapFile if trace else "",
        "sqlOperation": trace.sqlOperation if trace else "",
        "tableCandidates": trace.tableCandidates if trace else [],
        "responseFieldCandidates": trace.responseFieldCandidates if trace else [],
        "querySummary": trace.querySummary if trace else "",
        "sourceRefs": list(dict.fromkeys(transaction.sourceRefs + (trace.sourceRefs if trace else []))),
    }


def _build_action_contract(
    package: PageConversionPackage,
    function,
    event_by_handler: dict[str, list[Any]],
    validations_by_source: dict[str, list[Any]],
    state_rules_by_source: dict[str, list[Any]],
    messages_by_source: dict[str, list[Any]],
    navigation_by_trigger: dict[str, list[Any]],
    related_pages_by_trigger: dict[str, list[dict[str, Any]]],
    component_by_id: dict[str, Any],
    endpoints: list[dict[str, Any]],
) -> dict[str, Any]:
    related_events = event_by_handler.get(function.functionName, [])
    trigger_component = _resolve_trigger_component(
        function.functionName,
        event_by_handler,
        component_by_id,
    )
    endpoint_map = {item["transactionId"]: item for item in endpoints}
    return {
        "functionName": function.functionName,
        "functionType": function.functionType,
        "parameters": function.parameters,
        "transactions": function.callsTransactions,
        "controlsComponents": function.controlsComponents,
        "readsDatasets": function.readsDatasets,
        "writesDatasets": function.writesDatasets,
        "callsFunctions": function.callsFunctions,
        "platformCalls": function.platformCalls,
        "sourceRefs": function.sourceRefs,
        "sourceComponentId": trigger_component.componentId if trigger_component else "",
        "sourceComponentLabel": _component_label_or_id(trigger_component),
        "eventName": related_events[0].eventName if related_events else "",
        "eventType": related_events[0].eventType if related_events else "",
        "triggerCondition": related_events[0].triggerCondition if related_events else "",
        "effects": [effect for item in related_events for effect in item.effects],
        "actionKind": _infer_action_kind(function.functionName, related_events, trigger_component),
        "transactionBindings": [
            endpoint_map[transaction_id]
            for transaction_id in function.callsTransactions
            if transaction_id in endpoint_map
        ],
        "validationRules": [
            {
                "ruleId": item.ruleId,
                "targetField": item.targetField,
                "validationType": item.validationType,
                "triggerTiming": item.triggerTiming,
                "expression": item.expression,
                "message": item.message,
            }
            for item in validations_by_source.get(function.functionName, [])
        ],
        "stateRules": [
            {
                "ruleId": item.ruleId,
                "targetComponentId": item.targetComponentId,
                "stateProperty": item.stateProperty,
                "triggerCondition": item.triggerCondition,
                "expression": item.expression,
                "targetValue": item.targetValue,
            }
            for item in state_rules_by_source.get(function.functionName, [])
        ],
        "messages": [
            {
                "messageId": item.messageId,
                "messageType": item.messageType,
                "text": item.text,
                "targetComponentId": item.targetComponentId,
            }
            for item in messages_by_source.get(function.functionName, [])
        ],
        "navigationTargets": related_pages_by_trigger.get(function.functionName, []),
        "navigationMetadata": [
            {
                "navigationId": item.navigationId,
                "navigationType": item.navigationType,
                "target": item.target,
                "parameterBindings": item.parameterBindings,
                "returnHandling": item.returnHandling,
            }
            for item in navigation_by_trigger.get(function.functionName, [])
        ],
    }


def _normalize_grid_column(column: dict[str, Any]) -> dict[str, Any]:
    return {
        "band": str(column.get("band", "") or ""),
        "col": str(column.get("col", "") or ""),
        "columnName": str(column.get("columnName", "") or ""),
        "display": str(column.get("display", "") or ""),
        "text": str(column.get("text", "") or ""),
    }


def _dataset_column_names(page, dataset_id: str) -> list[str]:
    dataset = next((item for item in page.datasets if item.datasetId == dataset_id), None)
    if dataset is None:
        return []
    return [column.name for column in dataset.columns]


def _bindings_for_component(page, component_id: str) -> list[dict[str, Any]]:
    return [
        {
            "bindingId": item.bindingId,
            "datasetId": item.datasetId,
            "columnName": item.columnName,
            "bindingType": item.bindingType,
            "direction": item.direction,
            "sourceRefs": item.sourceRefs,
        }
        for item in page.bindings
        if item.componentId == component_id
    ]


def _component_layout(component) -> dict[str, str]:
    return {
        "left": str(component.properties.get("Left", "") or ""),
        "top": str(component.properties.get("Top", "") or ""),
        "width": str(component.properties.get("Width", "") or ""),
        "height": str(component.properties.get("Height", "") or ""),
    }


def _component_text(component) -> str:
    for key in ("Text", "Caption", "title"):
        value = component.properties.get(key)
        if value:
            return str(value)
    return ""


def _component_label_or_id(component) -> str:
    if component is None:
        return ""
    return _component_text(component) or component.componentId


def _infer_component_bound_column(component, bindings: list[dict[str, Any]]) -> str:
    for key in ("BindColumn", "CodeColumn", "DataColumn"):
        value = component.properties.get(key)
        if value:
            return str(value)
    for binding in bindings:
        if binding.get("columnName"):
            return str(binding["columnName"])
    return ""


def _classify_search_control(component) -> str:
    if component.componentType == "Button":
        return "action-trigger"
    if component.layoutGroup == "search-panel":
        return "search-input"
    return "input"


def _infer_component_label(page, component) -> str:
    direct_text = _component_text(component)
    if component.componentType == "Button" and direct_text:
        return direct_text

    target_left = _as_float(component.properties.get("Left"))
    target_top = _as_float(component.properties.get("Top"))
    candidates: list[tuple[float, str]] = []
    for other in page.components:
        if other.componentId == component.componentId:
            continue
        if other.parentId != component.parentId:
            continue
        if other.componentType not in {"Static", "Label"}:
            continue
        label = _component_text(other)
        if not label:
            continue
        label_left = _as_float(other.properties.get("Left"))
        label_top = _as_float(other.properties.get("Top"))
        if (
            target_top is not None
            and label_top is not None
            and abs(label_top - target_top) > 12
        ):
            continue
        if (
            target_left is not None
            and label_left is not None
            and label_left > target_left
        ):
            continue
        distance = abs((target_left or 0.0) - (label_left or 0.0)) + abs(
            (target_top or 0.0) - (label_top or 0.0)
        )
        candidates.append((distance, label))
    if candidates:
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]
    return direct_text


def _as_float(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _resolve_trigger_component(
    function_name: str,
    event_by_handler: dict[str, list[Any]],
    component_by_id: dict[str, Any],
):
    related_events = event_by_handler.get(function_name, [])
    for event in related_events:
        if event.sourceComponentId and event.sourceComponentId in component_by_id:
            return component_by_id[event.sourceComponentId]
    return None


def _infer_action_kind(function_name: str, related_events: list[Any], trigger_component) -> str:
    event_name = related_events[0].eventName if related_events else ""
    if event_name == "OnLoadCompleted":
        return "page-load"
    if trigger_component is not None and trigger_component.componentType == "Button":
        return "button-flow"
    if "OnClick" in event_name:
        return "click-flow"
    if function_name.lower().startswith("form_"):
        return "page-flow"
    return "event-handler"


def _summarize_search_controls(search_controls: list[dict[str, Any]]) -> str:
    if not search_controls:
        return "no explicit search controls captured"
    parts = []
    for item in search_controls[:4]:
        label = item.get("label") or item.get("text") or item.get("componentId")
        bound = item.get("requestFieldCandidate") or item.get("datasetBinding", {}).get("codeColumn", "")
        dataset = item.get("datasetId") or "no dataset"
        fragment = f"{label}({item.get('componentId')}, dataset={dataset}"
        if bound:
            fragment += f", field={bound}"
        fragment += ")"
        parts.append(fragment)
    return "; ".join(parts)


def _summarize_grids(grids: list[dict[str, Any]]) -> str:
    if not grids:
        return "no grid contract captured"
    parts = []
    for item in grids[:2]:
        headers = item.get("headerTexts") or item.get("columns", [])
        parts.append(
            f"{item.get('componentId')} -> dataset {item.get('datasetId')}, headers {', '.join(headers[:5]) or 'unresolved'}"
        )
    return "; ".join(parts)


def _summarize_actions(actions: list[dict[str, Any]]) -> str:
    if not actions:
        return "no action handlers captured"
    parts = []
    for item in actions[:4]:
        trigger = item.get("sourceComponentLabel") or item.get("functionName")
        transactions = ", ".join(item.get("transactions", [])) or "no transaction"
        navigation = ", ".join(
            nav.get("pageId") or nav.get("target") or "unresolved"
            for nav in item.get("navigationTargets", [])
        ) or "no navigation"
        parts.append(
            f"{trigger}/{item.get('functionName')} [{item.get('actionKind')}] tx={transactions}; nav={navigation}"
        )
    return "; ".join(parts)


def _summarize_endpoints(endpoints: list[dict[str, Any]]) -> str:
    if not endpoints:
        return "no backend endpoints captured"
    parts = []
    for item in endpoints[:4]:
        params = item.get("parameters") or "no params variable"
        callback = item.get("callbackFunction") or "no callback"
        sql_map_id = item.get("sqlMapId") or "sql map unresolved"
        parts.append(
            f"{item.get('transactionId')} url={item.get('url') or 'unresolved'} params={params} callback={callback} sql={sql_map_id}"
        )
    return "; ".join(parts)


def _summarize_related_pages(related_pages: list[dict[str, Any]]) -> str:
    if not related_pages:
        return "no related-screen navigation captured"
    parts = []
    for item in related_pages[:4]:
        target = item.get("pageId") or item.get("target") or "unresolved"
        params = ", ".join(item.get("parameterBindings", [])) or "no parameter bindings"
        parts.append(
            f"{item.get('triggerFunction') or item.get('navigationType')} -> {target} ({item.get('navigationType')}, params={params})"
        )
    return "; ".join(parts)


def _summarize_rule_contract(
    validation_rules: list[dict[str, Any]],
    state_rules: list[dict[str, Any]],
    messages: list[dict[str, Any]],
) -> str:
    validation_summary = (
        "; ".join(
            f"{item.get('targetField')}:{item.get('message') or item.get('expression')}"
            for item in validation_rules[:3]
        )
        or "no validation rules"
    )
    state_summary = (
        "; ".join(
            f"{item.get('targetComponentId')} {item.get('stateProperty')}={item.get('targetValue')}"
            for item in state_rules[:3]
        )
        or "no state rules"
    )
    message_summary = (
        "; ".join(
            item.get("text") or item.get("messageType") or item.get("messageId")
            for item in messages[:3]
        )
        or "no messages"
    )
    return f"validation[{validation_summary}] state[{state_summary}] messages[{message_summary}]"


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
