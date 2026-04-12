from __future__ import annotations

from typing import Any

from am_bridge.models import ConversionPlanModel, PageConversionPackage, VuePageConfigModel
from am_bridge.reporting import join_values, limit_text, markdown_link, render_contents, render_markdown_table


PAGE_ARTIFACT_LABELS: dict[str, str] = {
    "page_spec": "Page spec",
    "package_json": "Stage 1 package JSON",
    "package_report": "Stage 1 package report",
    "analysis_report": "Detailed legacy analysis report",
    "review_json": "Review override file",
    "plan_json": "Stage 2 plan JSON",
    "plan_report": "Stage 2 plan report",
    "vue_config_json": "Vue contract JSON",
    "pm_checklist": "PM test checklist",
    "starter_dir": "Starter directory",
    "starter_bundle": "Starter bundle metadata",
}


def build_page_report_hub(
    package: PageConversionPackage,
    artifact_links: dict[str, str],
    available_stages: set[str],
    plan: ConversionPlanModel | None = None,
    vue_config: VuePageConfigModel | None = None,
) -> dict[str, str]:
    content = _render_page_hub(package, artifact_links, available_stages, plan, vue_config)
    return {
        "README.md": content,
        "README.en.md": content,
        "translate-to-korean.md": _render_translation_guide(package),
    }


def build_stage1_hub_docs(
    package: PageConversionPackage,
    compact_specs: list[tuple[str, str, str]],
) -> dict[str, str]:
    overview = _render_stage1_overview(package, compact_specs)
    datasets = _render_stage1_datasets_doc(package)
    components = _render_stage1_components_doc(package)
    actions = _render_stage1_actions_doc(package)
    backend = _render_stage1_backend_doc(package)
    navigation = _render_stage1_navigation_doc(package)
    validation = _render_stage1_validation_doc(package)
    return {
        "README.md": overview,
        "README.en.md": overview,
        "sections/datasets.md": datasets,
        "sections/datasets.en.md": datasets,
        "sections/components.md": components,
        "sections/components.en.md": components,
        "sections/actions.md": actions,
        "sections/actions.en.md": actions,
        "sections/backend.md": backend,
        "sections/backend.en.md": backend,
        "sections/navigation.md": navigation,
        "sections/navigation.en.md": navigation,
        "sections/validation.md": validation,
        "sections/validation.en.md": validation,
    }


def build_stage2_hub_docs(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    compact_specs: list[tuple[str, str, str]],
) -> dict[str, str]:
    overview = _render_stage2_overview(package, plan, vue_config, compact_specs)
    ui_contract = _render_stage2_ui_contract_doc(plan, vue_config)
    actions = _render_stage2_actions_doc(vue_config)
    endpoints = _render_stage2_endpoints_doc(vue_config)
    files = _render_stage2_files_doc(plan)
    verification = _render_stage2_verification_doc(package, plan, vue_config)
    return {
        "README.md": overview,
        "README.en.md": overview,
        "sections/ui-contract.md": ui_contract,
        "sections/ui-contract.en.md": ui_contract,
        "sections/actions.md": actions,
        "sections/actions.en.md": actions,
        "sections/endpoints.md": endpoints,
        "sections/endpoints.en.md": endpoints,
        "sections/files.md": files,
        "sections/files.en.md": files,
        "sections/verification.md": verification,
        "sections/verification.en.md": verification,
    }


def _render_translation_guide(package: PageConversionPackage) -> str:
    page = package.page
    lines = [
        f"# Translate Report Pack To Korean - {page.pageId or 'legacy-page'}",
        "",
        "Use this guide after the English report pack has been reviewed.",
        "",
        "## Rules",
        "",
        "- Treat the English Markdown as the canonical source of truth.",
        "- Preserve dataset IDs, transaction IDs, endpoint names, component IDs, and file paths in backticks.",
        "- Translate explanation text and business meaning, not technical identifiers.",
        "- Do not edit the English originals unless explicitly asked.",
        "- Default to one Korean main summary document, not a mirrored Korean report tree.",
        "- Keep drill-down links pointed at the English canonical docs unless a Korean counterpart is explicitly required.",
        "",
        "## Suggested Prompt For Internal AI",
        "",
        "```text",
        f"Read the English canonical report set for `{page.pageId or 'legacy-page'}` and produce a Korean delivery version.",
        "Requirements:",
        "1. Use the English main report as the primary source.",
        "2. Keep technical IDs, dataset IDs, transaction IDs, endpoint IDs, component IDs, and file paths in backticks.",
        "3. Produce one Korean main summary document unless a wider Korean scope is explicitly requested.",
        "4. Keep links pointed at the English canonical docs unless a Korean counterpart is explicitly required and named in advance.",
        "5. Before writing files, list the exact Korean output files and confirm that none overwrite the English originals.",
        "6. Separate layout/signoff items from behavior/API/SQL lock items.",
        "7. Call out unresolved risks and manual review points clearly.",
        "8. If more Korean detail is needed, add it as a short appendix in the same Korean main summary document.",
        "```",
        "",
    ]
    return "\n".join(lines)


def _render_doc(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]
    lines.extend(render_contents([section_title for section_title, _ in sections]))
    for section_title, body in sections:
        lines.append(f"## {section_title}")
        lines.append("")
        lines.extend(body or ["- None"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _artifact_lines(artifact_links: dict[str, str]) -> list[str]:
    return [f"- {markdown_link(PAGE_ARTIFACT_LABELS.get(key, key), target)}" for key, target in artifact_links.items()] or ["- None"]


def _detail_lines(label: str, links: list[tuple[str, str]]) -> list[str]:
    return [f"- {label}: {', '.join(markdown_link(name, path) for name, path in links)}"]


def _snapshot_lines(
    intro: list[str],
    columns: list[tuple[str, str]],
    rows: list[dict[str, Any]],
    detail_links: list[tuple[str, str]],
) -> list[str]:
    return [*intro, "", *render_markdown_table(columns, rows), "", *_detail_lines("Full detail", detail_links)]


def _render_page_hub(
    package: PageConversionPackage,
    artifact_links: dict[str, str],
    available_stages: set[str],
    plan: ConversionPlanModel | None,
    vue_config: VuePageConfigModel | None,
) -> str:
    page = package.page
    sections = [
        (
            "Executive Snapshot",
            [
                "- This is the canonical English main report for the page.",
                "- Read this page first. Use CSV and section docs only for drill-down detail.",
                "",
                *render_markdown_table(
                    [("Field", "field"), ("Value", "value")],
                    [
                        {"field": "Page name", "value": page.pageName or "unknown"},
                        {"field": "Interaction pattern", "value": page.interactionPattern or "unknown"},
                        {"field": "Primary dataset", "value": _backtick(page.primaryDatasetId)},
                        {"field": "Main grid", "value": _backtick(page.mainGridComponentId)},
                        {"field": "Primary transactions", "value": _backtick_join(page.primaryTransactionIds)},
                        {"field": "Route", "value": _backtick(plan.route) if plan and plan.route else "not locked yet"},
                        {"field": "Vue page name", "value": _backtick(plan.vuePageName) if plan and plan.vuePageName else "not locked yet"},
                    ],
                ),
                "",
                f"- Stage 1: generated",
                f"- Stage 2: {'generated' if 'stage2' in available_stages else 'not generated yet'}",
                f"- Stage 3: {'generated' if 'stage3' in available_stages else 'not generated yet'}",
            ],
        ),
        ("Recommended Reading Order", _page_reading_order(available_stages)),
        ("UI Shell Snapshot", _ui_shell_snapshot_lines(page, vue_config, "stage2" if "stage2" in available_stages else "stage1")),
        ("Dataset Snapshot", _dataset_snapshot_lines(page, "stage1")),
        ("Action / Transaction Flow", _action_snapshot_lines(page, "stage1")),
        ("Backend / Endpoint Snapshot", _backend_endpoint_snapshot_lines(package, vue_config, available_stages)),
        ("Risks / Review Focus", _risk_snapshot_lines(package, vue_config)),
        ("Drill-down Index", _drill_down_lines(available_stages)),
        ("Primary Artifacts", _artifact_lines(artifact_links)),
        ("Language", [f"- {markdown_link('English canonical', 'README.md')}", f"- {markdown_link('Compatibility mirror', 'README.en.md')}", f"- {markdown_link('Korean translation guide', 'translate-to-korean.md')}"]),
    ]
    return _render_doc(f"Page Report Hub - {page.pageId or 'legacy-page'}", sections)


def _render_stage1_overview(package: PageConversionPackage, compact_specs: list[tuple[str, str, str]]) -> str:
    page = package.page
    sections = [
        (
            "Executive Snapshot",
            [
                "- Stage 1 is the evidence and restoration pass for the legacy page.",
                "- This overview keeps the most important Stage 1 signals inline and points to detailed drill-down artifacts.",
                "",
                *render_markdown_table(
                    [("Field", "field"), ("Value", "value")],
                    [
                        {"field": "Page name", "value": page.pageName or "unknown"},
                        {"field": "Primary dataset", "value": _backtick(page.primaryDatasetId)},
                        {"field": "Main grid", "value": _backtick(page.mainGridComponentId)},
                        {"field": "Primary transactions", "value": _backtick_join(page.primaryTransactionIds)},
                        {"field": "Backend trace count", "value": str(len(package.backendTraces))},
                        {"field": "Related screen count", "value": str(len(package.relatedPages))},
                    ],
                ),
            ],
        ),
        ("Reading Order", _stage1_reading_order()),
        ("Dataset Snapshot", _dataset_snapshot_lines(page, "")),
        ("Action Snapshot", _action_snapshot_lines(page, "")),
        ("Backend Snapshot", _stage1_backend_snapshot_lines(package, "")),
        ("Validation Snapshot", _validation_snapshot_lines(page, "")),
        ("Detailed Table Index", [*[
            f"- {markdown_link(name, name)}: {en}" for name, _ko, en in compact_specs
        ], f"- {markdown_link('tables.md', 'tables.md')}: CSV-oriented index for the Stage 1 root directory.", f"- {markdown_link('translate-to-korean.md', '../translate-to-korean.md')}: derived Korean summary guidance."]),
    ]
    return _render_doc(f"Stage 1 Analysis Guide - {page.pageId or 'legacy-page'}", sections)


def _render_stage2_overview(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    compact_specs: list[tuple[str, str, str]],
) -> str:
    sections = [
        (
            "Executive Snapshot",
            [
                "- Stage 2 locks the implementation contract after Stage 1 review.",
                "- The sections below show the contract inline before you open CSV or deep section docs.",
                "",
                *render_markdown_table(
                    [("Field", "field"), ("Value", "value")],
                    [
                        {"field": "Route", "value": _backtick(plan.route or "unknown")},
                        {"field": "Vue page name", "value": _backtick(plan.vuePageName or "unknown")},
                        {"field": "Primary dataset", "value": _backtick(package.page.primaryDatasetId)},
                        {"field": "Search control count", "value": str(len(vue_config.searchControls))},
                        {"field": "Action count", "value": str(len(vue_config.actions))},
                        {"field": "Endpoint count", "value": str(len(vue_config.endpoints))},
                    ],
                ),
            ],
        ),
        ("Reading Order", _stage2_reading_order()),
        ("UI Contract Snapshot", _ui_shell_snapshot_lines(package.page, vue_config, "")),
        ("Action Contract Snapshot", _stage2_action_snapshot_lines(vue_config, "")),
        ("Endpoint Contract Snapshot", _stage2_endpoint_snapshot_lines(vue_config, "")),
        ("File Blueprint Snapshot", _file_blueprint_snapshot_lines(plan, "")),
        ("Verification Snapshot", _verification_snapshot_lines(package, plan, vue_config, "")),
        ("Detailed Table Index", [*[
            f"- {markdown_link(name, name)}: {en}" for name, _ko, en in compact_specs
        ], f"- {markdown_link('tables.md', 'tables.md')}: CSV-oriented index for the Stage 2 root directory.", f"- {markdown_link('ai-prompts.md', 'ai-prompts.md')}: prompt pack for internal AI follow-up."]),
    ]
    return _render_doc(f"Stage 2 Plan Guide - {plan.pageId or 'legacy-page'}", sections)


def _render_stage1_section_doc(
    title: str,
    page_id: str,
    intro: list[str],
    quick_links: list[tuple[str, str]],
    columns: list[tuple[str, str]],
    rows: list[dict[str, Any]],
) -> str:
    return _render_doc(
        f"{title} - {page_id or 'legacy-page'}",
        [
            ("What This Document Does", intro),
            ("Quick Links", _detail_lines("Detail", quick_links)),
            ("Summary", render_markdown_table(columns, rows)),
        ],
    )


def _render_stage2_section_doc(
    title: str,
    page_id: str,
    intro: list[str],
    quick_links: list[tuple[str, str]],
    sections: list[tuple[str, list[str]]],
) -> str:
    return _render_doc(f"{title} - {page_id or 'legacy-page'}", [("What This Document Does", intro), ("Quick Links", _detail_lines("Detail", quick_links)), *sections])


def _render_stage1_datasets_doc(package: PageConversionPackage) -> str:
    page = package.page
    return _render_stage1_section_doc(
        "Stage 1 Dataset Analysis",
        page.pageId,
        ["- Confirms the dominant datasets, their role, and their main bindings.", "- Use the linked CSV files when you need full columns or binding-level detail."],
        [("datasets.csv", "../datasets.csv"), ("dataset-columns.csv", "../registries/dataset-columns.csv"), ("bindings.csv", "../registries/bindings.csv"), ("components", "components.md")],
        [("Dataset", "dataset"), ("Role", "role"), ("Usage", "usage"), ("Bound components", "components"), ("Columns", "columns"), ("Salience", "salience")],
        _dataset_rows(page),
    )


def _render_stage1_components_doc(package: PageConversionPackage) -> str:
    page = package.page
    return _render_stage1_section_doc(
        "Stage 1 Components And Layout",
        page.pageId,
        ["- Reviews where buttons, inputs, grids, and containers are placed.", "- Use this first when UI Shell signoff pressure is stronger than behavior lock pressure."],
        [("components.csv", "../components.csv"), ("bindings.csv", "../registries/bindings.csv"), ("grid-columns.csv", "../registries/grid-columns.csv")],
        [("Component", "component"), ("Type", "type"), ("Group", "group"), ("Parent", "parent"), ("Events", "events"), ("Platform dependency", "platform")],
        _component_rows(page),
    )


def _render_stage1_actions_doc(package: PageConversionPackage) -> str:
    page = package.page
    return _render_stage1_section_doc(
        "Stage 1 Actions And Events",
        page.pageId,
        ["- Reviews which handlers touch datasets, transactions, and related screens.", "- If the flow is wrong here, the Stage 2 action contract will drift too."],
        [("user-actions.csv", "../user-actions.csv"), ("functions.csv", "../registries/functions.csv"), ("events.csv", "../registries/events.csv"), ("transactions.csv", "../registries/transactions.csv")],
        [("Handler", "handler"), ("Transactions", "transactions"), ("Reads", "reads"), ("Writes", "writes"), ("Controls", "controls"), ("Calls", "calls")],
        _action_rows(page),
    )


def _render_stage1_backend_doc(package: PageConversionPackage) -> str:
    return _render_stage1_section_doc(
        "Stage 1 Backend Trace",
        package.page.pageId,
        ["- Traces each transaction into controller, service, DAO, and SQL evidence.", "- Read this together with dataset analysis before locking DB or API contracts."],
        [("backend-traces.csv", "../backend-traces.csv"), ("transactions.csv", "../registries/transactions.csv")],
        [("Transaction", "transaction"), ("URL", "url"), ("Controller", "controller"), ("Service", "service"), ("DAO", "dao"), ("SQL Map", "sql"), ("Tables", "tables")],
        _backend_rows(package),
    )


def _render_stage1_navigation_doc(package: PageConversionPackage) -> str:
    return _render_stage1_section_doc(
        "Stage 1 Related Screens",
        package.page.pageId,
        ["- Reviews popups, subviews, and page-to-page navigation that leave the current page.", "- Resolve unresolved targets before collapsing them into the current page implementation."],
        [("related-pages.csv", "../related-pages.csv"), ("navigation.csv", "../registries/navigation.csv")],
        [("Type", "type"), ("Trigger", "trigger"), ("Target", "target"), ("Resolved page", "page"), ("Status", "status")],
        _navigation_rows(package),
    )


def _render_stage1_validation_doc(package: PageConversionPackage) -> str:
    page = package.page
    return _render_stage1_section_doc(
        "Stage 1 Validation And Messages",
        page.pageId,
        ["- Reviews validation, state rules, and user-facing message evidence.", "- Read this with action analysis when error messaging or disable/enable logic matters."],
        [("validation-rules.csv", "../validation-rules.csv"), ("state-rules.csv", "../registries/state-rules.csv"), ("messages.csv", "../registries/messages.csv")],
        [("Rule", "rule"), ("Field", "field"), ("Type", "type"), ("Timing", "timing"), ("Source", "source"), ("Message", "message")],
        _validation_rows(page),
    )


def _render_stage2_ui_contract_doc(plan: ConversionPlanModel, vue_config: VuePageConfigModel) -> str:
    return _render_stage2_section_doc(
        "Stage 2 UI Contract",
        plan.pageId,
        ["- Reviews the post-conversion page shell and binding contract.", "- Use this to confirm customer-facing control placement before deeper behavior review."],
        [("search-controls.csv", "../search-controls.csv"), ("grids.csv", "../grids.csv"), ("grid-columns.csv", "../grid-columns.csv")],
        [("Search / Command Controls", render_markdown_table([("Component", "component"), ("Label", "label"), ("Dataset", "dataset"), ("Role", "role"), ("Events", "events")], _search_control_rows(vue_config))), ("Grid Contract", render_markdown_table([("Grid", "grid"), ("Dataset", "dataset"), ("Layout", "layout"), ("Columns", "columns"), ("Headers", "headers")], _grid_rows(vue_config)))],
    )


def _render_stage2_actions_doc(vue_config: VuePageConfigModel) -> str:
    return _render_stage2_section_doc(
        "Stage 2 Action Contract",
        vue_config.pageId,
        ["- Reviews which UI triggers connect to transactions, datasets, and navigation.", "- This is the locked action contract after the Stage 1 review pass."],
        [("actions.csv", "../actions.csv"), ("related-pages.csv", "../related-pages.csv")],
        [("Action Summary", render_markdown_table([("Function", "function"), ("Kind", "kind"), ("Source", "source"), ("Transactions", "transactions"), ("Reads", "reads"), ("Writes", "writes"), ("Navigation", "navigation")], _stage2_action_rows(vue_config)))],
    )


def _render_stage2_endpoints_doc(vue_config: VuePageConfigModel) -> str:
    return _render_stage2_section_doc(
        "Stage 2 Endpoint Contract",
        vue_config.pageId,
        ["- Reviews endpoint contract rows with input/output datasets and backend chain evidence.", "- Use this as the pre/post MyBatis conversion comparison reference."],
        [("endpoints.csv", "../endpoints.csv"), ("related-pages.csv", "../related-pages.csv")],
        [("Endpoint Summary", render_markdown_table([("Transaction", "transaction"), ("URL", "url"), ("Input datasets", "inputs"), ("Output datasets", "outputs"), ("Controller", "controller"), ("Service", "service"), ("DAO", "dao"), ("SQL Map", "sql")], _endpoint_rows(vue_config)))],
    )


def _render_stage2_files_doc(plan: ConversionPlanModel) -> str:
    return _render_stage2_section_doc(
        "Stage 2 File Blueprints",
        plan.pageId,
        ["- Explains which frontend and backend files are planned and why.", "- Use this as the minimum file split reference even if responsibilities shift later."],
        [("file-blueprints.csv", "../file-blueprints.csv"), ("registry copy", "../registries/file-blueprints.csv")],
        [("File Blueprint Summary", render_markdown_table([("Kind", "kind"), ("Path", "path"), ("Purpose", "purpose"), ("Summary", "summary")], _file_rows(plan)))],
    )


def _render_stage2_verification_doc(package: PageConversionPackage, plan: ConversionPlanModel, vue_config: VuePageConfigModel) -> str:
    return _render_stage2_section_doc(
        "Stage 2 Verification And Checklist",
        plan.pageId,
        ["- Explains what must be verified after Stage 2 decisions are locked.", "- Shows PM review focus alongside internal verification items."],
        [("verification-checks.csv", "../registries/verification-checks.csv"), ("execution-steps.csv", "../registries/execution-steps.csv"), ("ai-prompts.md", "../ai-prompts.md")],
        [("Verification Snapshot", _verification_snapshot_lines(package, plan, vue_config, ""))],
    )


def _ui_shell_snapshot_lines(page: Any, vue_config: VuePageConfigModel | None, base_path: str) -> list[str]:
    control_rows = _search_control_rows(vue_config)[:6] if vue_config else _stage1_shell_rows(page)[:6]
    grid_rows = _grid_rows(vue_config)[:3] if vue_config else _stage1_grid_rows(page)[:2]
    detail_links = [("UI contract", _path(base_path, "sections/ui-contract.md")), ("search-controls.csv", _path(base_path, "search-controls.csv")), ("grids.csv", _path(base_path, "grids.csv"))] if vue_config else [("components", _path(base_path, "sections/components.md")), ("components.csv", _path(base_path, "components.csv"))]
    return ["- This section is for early structure signoff. It does not imply behavior/API/SQL lock by itself.", "- Focus here when the main risk is moved buttons, missing sections, or changed popup entry points.", "", "**Key controls**", "", *render_markdown_table([("Component", "component"), ("Label", "label"), ("Dataset", "dataset"), ("Role", "role"), ("Events", "events")], control_rows), "", "**Grid anchors**", "", *render_markdown_table([("Grid", "grid"), ("Dataset", "dataset"), ("Layout", "layout"), ("Columns", "columns"), ("Headers", "headers")], grid_rows), "", *_detail_lines("Full detail", detail_links)]


def _dataset_snapshot_lines(page: Any, base_path: str) -> list[str]:
    rows = _dataset_rows(page)
    return _snapshot_lines(["- The primary dataset is always shown first, followed by the highest-salience datasets.", f"- Showing {min(len(rows), 5)} of {len(rows)} datasets inline."], [("Dataset", "dataset"), ("Role", "role"), ("Usage", "usage"), ("Bound components", "components"), ("Columns", "columns"), ("Salience", "salience")], rows[:5], [("Dataset analysis", _path(base_path, "sections/datasets.md")), ("datasets.csv", _path(base_path, "datasets.csv")), ("dataset-columns.csv", _path(base_path, "registries/dataset-columns.csv")), ("bindings.csv", _path(base_path, "registries/bindings.csv"))])


def _action_snapshot_lines(page: Any, base_path: str) -> list[str]:
    rows = _action_rows(page)
    return _snapshot_lines(["- Prioritized handlers are the ones that call transactions, write datasets, or navigate away from the page.", f"- Showing {min(len(rows), 5)} of {len(rows)} handlers inline."], [("Handler", "handler"), ("Transactions", "transactions"), ("Reads", "reads"), ("Writes", "writes"), ("Controls", "controls"), ("Calls", "calls")], rows[:5], [("Action analysis", _path(base_path, "sections/actions.md")), ("user-actions.csv", _path(base_path, "user-actions.csv")), ("functions.csv", _path(base_path, "registries/functions.csv")), ("events.csv", _path(base_path, "registries/events.csv"))])


def _stage1_backend_snapshot_lines(package: PageConversionPackage, base_path: str) -> list[str]:
    rows = _backend_rows(package)
    return _snapshot_lines(["- Primary transactions and unresolved chains are surfaced first.", f"- Showing {min(len(rows), 5)} of {len(rows)} backend traces inline."], [("Transaction", "transaction"), ("URL", "url"), ("Controller", "controller"), ("Service", "service"), ("DAO", "dao"), ("SQL Map", "sql"), ("Tables", "tables")], rows[:5], [("Backend trace", _path(base_path, "sections/backend.md")), ("backend-traces.csv", _path(base_path, "backend-traces.csv")), ("transactions.csv", _path(base_path, "registries/transactions.csv"))])


def _backend_endpoint_snapshot_lines(package: PageConversionPackage, vue_config: VuePageConfigModel | None, available_stages: set[str]) -> list[str]:
    if vue_config and "stage2" in available_stages:
        return _stage2_endpoint_snapshot_lines(vue_config, "stage2")
    return _stage1_backend_snapshot_lines(package, "stage1")


def _validation_snapshot_lines(page: Any, base_path: str) -> list[str]:
    rows = _validation_rows(page)
    return _snapshot_lines(["- Validation rows surface fields with user-facing messages or non-trivial timing.", f"- Showing {min(len(rows), 5)} of {len(rows)} validation rules inline."], [("Rule", "rule"), ("Field", "field"), ("Type", "type"), ("Timing", "timing"), ("Source", "source"), ("Message", "message")], rows[:5], [("Validation detail", _path(base_path, "sections/validation.md")), ("validation-rules.csv", _path(base_path, "validation-rules.csv")), ("messages.csv", _path(base_path, "registries/messages.csv"))])


def _stage2_action_snapshot_lines(vue_config: VuePageConfigModel, base_path: str) -> list[str]:
    rows = _stage2_action_rows(vue_config)
    return _snapshot_lines(["- Action contracts below show which UI triggers touch transactions, datasets, and navigation.", f"- Showing {min(len(rows), 5)} of {len(rows)} actions inline."], [("Function", "function"), ("Kind", "kind"), ("Source", "source"), ("Transactions", "transactions"), ("Reads", "reads"), ("Writes", "writes"), ("Navigation", "navigation")], rows[:5], [("Action contract", _path(base_path, "sections/actions.md")), ("actions.csv", _path(base_path, "actions.csv")), ("related-pages.csv", _path(base_path, "related-pages.csv"))])


def _stage2_endpoint_snapshot_lines(vue_config: VuePageConfigModel, base_path: str) -> list[str]:
    rows = _endpoint_rows(vue_config)
    return _snapshot_lines(["- Primary transactions and unresolved endpoint chains stay visible here.", f"- Showing {min(len(rows), 5)} of {len(rows)} endpoint rows inline."], [("Transaction", "transaction"), ("URL", "url"), ("Input datasets", "inputs"), ("Output datasets", "outputs"), ("Controller", "controller"), ("Service", "service"), ("DAO", "dao"), ("SQL Map", "sql")], rows[:5], [("Endpoint contract", _path(base_path, "sections/endpoints.md")), ("endpoints.csv", _path(base_path, "endpoints.csv")), ("related-pages.csv", _path(base_path, "related-pages.csv"))])


def _file_blueprint_snapshot_lines(plan: ConversionPlanModel, base_path: str) -> list[str]:
    rows = _file_rows(plan)
    return _snapshot_lines(["- Keep this file split visible even when later R&R adjustments move implementation ownership.", f"- Showing {min(len(rows), 6)} of {len(rows)} planned files inline."], [("Kind", "kind"), ("Path", "path"), ("Purpose", "purpose"), ("Summary", "summary")], rows[:6], [("File blueprints", _path(base_path, "sections/files.md")), ("file-blueprints.csv", _path(base_path, "file-blueprints.csv"))])


def _verification_snapshot_lines(package: PageConversionPackage, plan: ConversionPlanModel, vue_config: VuePageConfigModel, base_path: str) -> list[str]:
    checks = [{"check": limit_text(item, 100)} for item in plan.verificationChecks[:6]]
    pm_rows = [{"item": "Confirm the primary dataset and main grid", "detail": f"{_backtick(package.page.primaryDatasetId)} / {_backtick(package.page.mainGridComponentId)}"}, {"item": "Confirm the primary transactions", "detail": _backtick_join(package.page.primaryTransactionIds)}, {"item": "Confirm action and endpoint counts", "detail": f"action={len(vue_config.actions)}, endpoint={len(vue_config.endpoints)}"}]
    return ["- Use this section as the short acceptance view before opening the full PM checklist or verification registries.", "", "**Verification checks**", "", *render_markdown_table([("Check", "check")], checks), "", "**PM review focus**", "", *render_markdown_table([("Item", "item"), ("Detail", "detail")], pm_rows), "", *_detail_lines("Full detail", [("Verification detail", _path(base_path, "sections/verification.md")), ("verification-checks.csv", _path(base_path, "registries/verification-checks.csv")), ("execution-steps.csv", _path(base_path, "registries/execution-steps.csv"))])]


def _risk_snapshot_lines(package: PageConversionPackage, vue_config: VuePageConfigModel | None) -> list[str]:
    unresolved_related = sum(1 for item in package.relatedPages if (item.resolutionStatus or "").lower() != "resolved")
    unknown_backend = sum(1 for item in package.backendTraces if not (item.controllerClass or item.serviceImplClass or item.daoClass or item.sqlMapId))
    unknown_endpoints = sum(1 for item in (vue_config.endpoints if vue_config else []) if not (item.get("controller") or item.get("service") or item.get("dao") or item.get("sqlMapId")))
    rows = [{"area": "Related screens", "detail": f"{unresolved_related} unresolved navigation targets"}, {"area": "Backend traces", "detail": f"{unknown_backend} traces without controller/service/DAO/sqlMap evidence"}, {"area": "Stage 2 endpoints", "detail": f"{unknown_endpoints} endpoint rows still have unknown backend chain" if vue_config else "not locked yet"}, {"area": "Validation", "detail": f"{len(package.page.validationRules)} validation rules need PM review"}, {"area": "Open questions", "detail": str(len(package.openQuestions))}]
    lines = ["- Keep unresolved or weakly-supported items visible here instead of burying them in deep links.", "", *render_markdown_table([("Area", "area"), ("Detail", "detail")], rows)]
    if package.openQuestions:
        lines.extend(["", "**Open questions**", "", *[f"- {item}" for item in package.openQuestions[:6]]])
    return lines


def _drill_down_lines(available_stages: set[str]) -> list[str]:
    lines = [f"- Datasets: {markdown_link('Stage 1 dataset guide', 'stage1/sections/datasets.md')} | {markdown_link('datasets.csv', 'stage1/datasets.csv')}", f"- Components / layout: {markdown_link('Stage 1 component guide', 'stage1/sections/components.md')} | {markdown_link('components.csv', 'stage1/components.csv')}", f"- Actions / events: {markdown_link('Stage 1 action guide', 'stage1/sections/actions.md')} | {markdown_link('user-actions.csv', 'stage1/user-actions.csv')}", f"- Backend traces: {markdown_link('Stage 1 backend guide', 'stage1/sections/backend.md')} | {markdown_link('backend-traces.csv', 'stage1/backend-traces.csv')}", f"- Validation: {markdown_link('Stage 1 validation guide', 'stage1/sections/validation.md')} | {markdown_link('validation-rules.csv', 'stage1/validation-rules.csv')}"]
    if "stage2" in available_stages:
        lines.extend([f"- UI contract: {markdown_link('Stage 2 UI guide', 'stage2/sections/ui-contract.md')} | {markdown_link('search-controls.csv', 'stage2/search-controls.csv')} | {markdown_link('grids.csv', 'stage2/grids.csv')}", f"- Action contract: {markdown_link('Stage 2 action guide', 'stage2/sections/actions.md')} | {markdown_link('actions.csv', 'stage2/actions.csv')}", f"- Endpoint contract: {markdown_link('Stage 2 endpoint guide', 'stage2/sections/endpoints.md')} | {markdown_link('endpoints.csv', 'stage2/endpoints.csv')}", f"- Files / verification: {markdown_link('Stage 2 files', 'stage2/sections/files.md')} | {markdown_link('Stage 2 verification', 'stage2/sections/verification.md')} | {markdown_link('file-blueprints.csv', 'stage2/file-blueprints.csv')}"])
    return lines


def _page_reading_order(available_stages: set[str]) -> list[str]:
    order = [f"1. {markdown_link('Stage 1 overview', 'stage1/README.md')}", f"2. {markdown_link('Stage 1 dataset guide', 'stage1/sections/datasets.md')}", f"3. {markdown_link('Stage 1 action guide', 'stage1/sections/actions.md')}", f"4. {markdown_link('Stage 1 backend guide', 'stage1/sections/backend.md')}"]
    if "stage2" in available_stages:
        order.extend([f"5. {markdown_link('Stage 2 overview', 'stage2/README.md')}", f"6. {markdown_link('Stage 2 UI guide', 'stage2/sections/ui-contract.md')}", f"7. {markdown_link('Stage 2 endpoint guide', 'stage2/sections/endpoints.md')}", f"8. {markdown_link('Stage 2 verification guide', 'stage2/sections/verification.md')}"])
    return order


def _stage1_reading_order() -> list[str]:
    return [f"1. {markdown_link('Dataset analysis', 'sections/datasets.md')}", f"2. {markdown_link('Backend trace', 'sections/backend.md')}", f"3. {markdown_link('Action analysis', 'sections/actions.md')}", f"4. {markdown_link('Related screens', 'sections/navigation.md')}", f"5. {markdown_link('Validation and messages', 'sections/validation.md')}"]


def _stage2_reading_order() -> list[str]:
    return [f"1. {markdown_link('UI contract', 'sections/ui-contract.md')}", f"2. {markdown_link('Action contract', 'sections/actions.md')}", f"3. {markdown_link('Endpoint contract', 'sections/endpoints.md')}", f"4. {markdown_link('File blueprints', 'sections/files.md')}", f"5. {markdown_link('Verification and checklist', 'sections/verification.md')}"]


def _dataset_rows(page: Any) -> list[dict[str, Any]]:
    items = sorted(page.datasets, key=lambda item: (item.datasetId != page.primaryDatasetId, -item.salienceScore, item.datasetId))
    return [{"dataset": _mark_primary(item.datasetId, item.datasetId == page.primaryDatasetId), "role": item.role or "unknown", "usage": item.primaryUsage or "unknown", "components": join_values(item.boundComponents[:3], "none"), "columns": len(item.columns), "salience": item.salienceScore} for item in items]


def _component_rows(page: Any) -> list[dict[str, Any]]:
    return [{"component": item.componentId, "type": item.componentType, "group": item.layoutGroup or "unknown", "parent": item.parentId or "root", "events": join_values(item.events, "none"), "platform": join_values(item.platformDependency, "none")} for item in page.components]


def _action_rows(page: Any) -> list[dict[str, Any]]:
    items = [item for item in page.functions if item.functionType == "event-handler"]
    items.sort(key=lambda item: (-len(item.callsTransactions), -len(item.writesDatasets), -len(item.readsDatasets), -len(item.controlsComponents), item.functionName))
    return [{"handler": item.functionName, "transactions": _backtick_join(item.callsTransactions), "reads": _backtick_join(item.readsDatasets), "writes": _backtick_join(item.writesDatasets), "controls": _backtick_join(item.controlsComponents), "calls": _backtick_join(item.callsFunctions)} for item in items]


def _backend_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    primary = set(package.page.primaryTransactionIds)
    items = list(package.backendTraces)
    items.sort(key=lambda item: (item.transactionId not in primary, bool(item.controllerClass or item.serviceImplClass or item.daoClass or item.sqlMapId), item.transactionId))
    return [{"transaction": _backtick(item.transactionId), "url": item.url or "unknown", "controller": _join_pair(item.controllerClass, item.controllerMethod), "service": _join_pair(item.serviceImplClass or item.serviceInterface, item.serviceMethod), "dao": _join_pair(item.daoClass, item.daoMethod), "sql": item.sqlMapId or "unknown", "tables": join_values(item.tableCandidates[:3], "none")} for item in items]


def _navigation_rows(package: PageConversionPackage) -> list[dict[str, Any]]:
    return [{"type": item.navigationType or "unknown", "trigger": item.triggerFunction or "unknown", "target": item.target or item.navigationId or "unknown", "page": item.pageId or item.pageName or "unresolved", "status": item.resolutionStatus or "unknown"} for item in package.relatedPages]


def _validation_rows(page: Any) -> list[dict[str, Any]]:
    items = list(page.validationRules)
    items.sort(key=lambda item: (not bool(item.message), item.targetField or "", item.ruleId))
    return [{"rule": item.ruleId, "field": item.targetField or "unknown", "type": item.validationType or "unknown", "timing": item.triggerTiming or "unknown", "source": item.sourceFunction or "unknown", "message": limit_text(item.message or item.expression or "unknown", 80)} for item in items]


def _search_control_rows(vue_config: VuePageConfigModel | None) -> list[dict[str, Any]]:
    if not vue_config:
        return []
    return [{"component": item.get("componentId", "") or "unknown", "label": item.get("label", "") or item.get("componentId", "") or "unknown", "dataset": item.get("datasetId", "") or "none", "role": item.get("controlRole", "") or "unknown", "events": join_values(item.get("events", [])[:3], "none")} for item in vue_config.searchControls]


def _grid_rows(vue_config: VuePageConfigModel | None) -> list[dict[str, Any]]:
    if not vue_config:
        return []
    return [{"grid": item.get("componentId", "") or "unknown", "dataset": item.get("datasetId", "") or "unknown", "layout": item.get("layoutGroup", "") or "unknown", "columns": len(item.get("bodyColumns", [])), "headers": limit_text(join_values(item.get("headerTexts", [])[:4], "none"), 60)} for item in vue_config.grids]


def _stage1_shell_rows(page: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(page.components, key=lambda comp: (comp.componentId != page.mainGridComponentId, comp.layoutGroup or "", comp.componentId)):
        if item.componentType.lower() not in {"button", "grid", "edit", "combo", "textarea", "tab"}:
            continue
        rows.append({"component": item.componentId, "label": item.properties.get("text", "") or item.componentId, "dataset": "n/a", "role": item.layoutGroup or item.componentType, "events": join_values(item.events[:3], "none")})
    return rows


def _stage1_grid_rows(page: Any) -> list[dict[str, Any]]:
    rows = [{"grid": item.componentId, "dataset": page.primaryDatasetId or "unknown", "layout": item.layoutGroup or "unknown", "columns": "n/a", "headers": limit_text(str(item.properties.get("format", "") or "see grid-columns.csv"), 60)} for item in page.components if item.componentType.lower() == "grid"]
    return rows or [{"grid": page.mainGridComponentId or "unknown", "dataset": page.primaryDatasetId or "unknown", "layout": "unknown", "columns": "n/a", "headers": "see grid-columns.csv"}]


def _stage2_action_rows(vue_config: VuePageConfigModel) -> list[dict[str, Any]]:
    rows = [{"function": item.get("functionName", "") or "unknown", "kind": item.get("actionKind", "") or "unknown", "source": item.get("sourceComponentLabel", "") or item.get("sourceComponentId", "") or "unknown", "transactions": _backtick_join(item.get("transactions", [])), "reads": _backtick_join(item.get("readsDatasets", [])), "writes": _backtick_join(item.get("writesDatasets", [])), "navigation": _backtick_join([nav.get("pageId") or nav.get("target") or "unresolved" for nav in item.get("navigationTargets", [])])} for item in vue_config.actions]
    rows.sort(key=lambda item: ("none" in item["transactions"], "none" in item["writes"], item["function"]))
    return rows


def _endpoint_rows(vue_config: VuePageConfigModel) -> list[dict[str, Any]]:
    rows = [{"transaction": _backtick(item.get("transactionId", "") or "unknown"), "url": item.get("url", "") or "unknown", "inputs": _backtick_join(item.get("inputDatasets", [])), "outputs": _backtick_join(item.get("outputDatasets", [])), "controller": item.get("controller", "") or "unknown", "service": item.get("service", "") or "unknown", "dao": item.get("dao", "") or "unknown", "sql": item.get("sqlMapId", "") or "unknown"} for item in vue_config.endpoints]
    rows.sort(key=lambda item: (item["controller"] != "unknown" and item["service"] != "unknown" and item["dao"] != "unknown" and item["sql"] != "unknown", item["transaction"]))
    return rows


def _file_rows(plan: ConversionPlanModel) -> list[dict[str, Any]]:
    rows = [{"kind": "frontend", "path": file.path, "purpose": file.purpose, "summary": limit_text(file.summary, 80)} for file in plan.frontendFiles] + [{"kind": "backend", "path": file.path, "purpose": file.purpose, "summary": limit_text(file.summary, 80)} for file in plan.backendFiles]
    rows.sort(key=lambda item: (item["kind"], item["path"]))
    return rows


def _mark_primary(value: str, is_primary: bool) -> str:
    return f"{value} [PRIMARY]" if is_primary and value else value or "unknown"


def _join_pair(first: str, second: str) -> str:
    parts = [item for item in [first, second] if item]
    return ".".join(parts) if parts else "unknown"


def _backtick(value: str | None) -> str:
    return f"`{value}`" if value else "unknown"


def _backtick_join(values: list[str]) -> str:
    items = [f"`{item}`" for item in values if item]
    return ", ".join(items) if items else "none"


def _path(base_path: str, relative_path: str) -> str:
    return f"{base_path}/{relative_path}" if base_path else relative_path
