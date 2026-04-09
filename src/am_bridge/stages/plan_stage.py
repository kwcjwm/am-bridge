from __future__ import annotations

import re

from am_bridge.models import ConversionPlanModel, FileBlueprintModel, PageConversionPackage


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
        "Stage 3: generate starter files and let AI Pro fill business logic using the starter bundle plus review overrides.",
        "Verification: compare the generated page flow against the original datasets, transactions, and popup/subview flows.",
    ]

    verification_checks = [
        "Primary dataset matches the dominant result grid or primary business response.",
        "Search/code/view-state datasets are not treated as equal peers to the primary result dataset.",
        "Each primary transaction has a resolved or manually corrected backend route chain.",
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
    lines.extend(["", "## AI Prompts", ""])
    for key, value in plan.aiPrompts.items():
        lines.extend([f"### {key}", "", "```text", value, "```", ""])
    lines.extend(["## Package Hints", ""])
    lines.extend([f"- {item}" for item in package.aiHints] or ["- None"])
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
        f"Using the stage 1 package and stage 2 plan for {page.pageId}, implement the frontend files "
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
        f"Using the stage 1 package and stage 2 plan for {page.pageId}, implement the backend files "
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
