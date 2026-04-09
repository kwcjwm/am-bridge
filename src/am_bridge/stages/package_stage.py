from __future__ import annotations

import json
from pathlib import Path

from am_bridge.config import CliConfig, resolve_input_path
from am_bridge.backend_trace import trace_backend_dependencies
from am_bridge.generators import generate_page_conversion_spec
from am_bridge.models import BackendTraceModel, PageConversionPackage, PageModel, RelatedPageModel
from am_bridge.pipeline import analyze_file


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


def generate_package_report(package: PageConversionPackage) -> str:
    page = package.page
    lines = [
        "# Stage 1 - Conversion Package",
        "",
        "## Page Summary",
        "",
        f"- pageId: {page.pageId or 'unknown'}",
        f"- pageName: {page.pageName or 'unknown'}",
        f"- interactionPattern: {page.interactionPattern or 'unknown'}",
        f"- mainGridComponentId: {page.mainGridComponentId or 'unknown'}",
        f"- primaryDatasetId: {page.primaryDatasetId or 'unknown'}",
        f"- primaryTransactionIds: {_join(page.primaryTransactionIds)}",
        "",
        "## Dataset Salience",
        "",
    ]

    for dataset in sorted(page.datasets, key=lambda item: (-item.salienceScore, item.datasetId)):
        marker = "PRIMARY" if dataset.datasetId == page.primaryDatasetId else "secondary"
        lines.extend(
            [
                f"### {dataset.datasetId} [{marker}]",
                f"- role: {dataset.role or 'unknown'}",
                f"- primaryUsage: {dataset.primaryUsage or 'unknown'}",
                f"- salienceScore: {dataset.salienceScore}",
                f"- boundComponents: {_join(dataset.boundComponents)}",
                f"- reasons: {_join(dataset.salienceReasons)}",
                "",
            ]
        )

    lines.extend(["## Backend Trace", ""])
    if not package.backendTraces:
        lines.extend(["- No backend trace resolved from configured backendRoots.", ""])
    else:
        for trace in package.backendTraces:
            lines.extend(
                [
                    f"### {trace.transactionId}",
                    f"- url: {trace.url or 'unknown'}",
                    f"- controller: {_join_nonempty(trace.controllerClass, trace.controllerMethod)}",
                    f"- service: {_join_nonempty(trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod)}",
                    f"- dao: {_join_nonempty(trace.daoClass, trace.daoMethod)}",
                    f"- sqlMapId: {trace.sqlMapId or 'unknown'}",
                    f"- sqlMapFile: {trace.sqlMapFile or 'unknown'}",
                    f"- tables: {_join(trace.tableCandidates)}",
                    f"- responseFields: {_join(trace.responseFieldCandidates)}",
                    f"- querySummary: {trace.querySummary or 'unknown'}",
                    "",
                ]
            )

    lines.extend(["## Related Screens", ""])
    if package.relatedPages:
        for related in package.relatedPages:
            lines.extend(
                [
                    f"### {related.target or related.navigationId}",
                    f"- navigationType: {related.navigationType or 'unknown'}",
                    f"- triggerFunction: {related.triggerFunction or 'unknown'}",
                    f"- resolutionStatus: {related.resolutionStatus or 'unknown'}",
                    f"- relatedPageId: {related.pageId or 'unknown'}",
                    f"- resolvedPath: {related.resolvedPath or 'unknown'}",
                    "",
                ]
            )
    else:
        lines.extend(["- No popup/subview target found.", ""])

    lines.extend(
        [
            "## AI Review Loop",
            "",
            "- Review the primary dataset choice first.",
            "- If a large result grid exists, its bound dataset should usually dominate search/code/view-state datasets.",
            "- Save corrections into the review JSON, then rerun stage 1 or continue to stage 2 with the override file.",
            "",
            "## Open Questions",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in package.openQuestions] if package.openQuestions else ["- None"])
    lines.extend(["", "## AI Hints", ""])
    lines.extend([f"- {item}" for item in package.aiHints] if package.aiHints else ["- None"])
    lines.extend(["", "## Legacy Page Spec Snapshot", "", generate_page_conversion_spec(page)])
    return "\n".join(lines)


def generate_analysis_report(package: PageConversionPackage) -> str:
    page = package.page
    lines = [
        "# Detailed Legacy Analysis Report",
        "",
        "## Page Identity",
        "",
        f"- pageId: {page.pageId or 'unknown'}",
        f"- pageName: {page.pageName or 'unknown'}",
        f"- pageType: {page.pageType or 'unknown'}",
        f"- sourceFile: {page.legacy.sourceFile or 'unknown'}",
        f"- interactionPattern: {page.interactionPattern or 'unknown'}",
        "",
        "## Page Boundary",
        "",
        f"- primaryDatasetId: {page.primaryDatasetId or 'unknown'}",
        f"- mainGridComponentId: {page.mainGridComponentId or 'unknown'}",
        f"- primaryTransactionIds: {_join(page.primaryTransactionIds)}",
        "",
        "## Frontend Integrated Analysis",
        "",
        "### Datasets",
        "",
    ]

    for dataset in sorted(page.datasets, key=lambda item: (-item.salienceScore, item.datasetId)):
        lines.extend(
            [
                f"#### {dataset.datasetId}",
                f"- role: {dataset.role or 'unknown'}",
                f"- primaryUsage: {dataset.primaryUsage or 'unknown'}",
                f"- boundComponents: {_join(dataset.boundComponents)}",
                f"- columns: {_join([column.name for column in dataset.columns])}",
                f"- salienceScore: {dataset.salienceScore}",
                "",
            ]
        )

    lines.extend(["### Components", ""])
    for component in page.components:
        if component.componentType not in {"Grid", "Combo", "Button", "Div", "Edit", "MaskEdit", "Calendar", "Static"}:
            continue
        lines.extend(
            [
                f"#### {component.componentId}",
                f"- componentType: {component.componentType}",
                f"- layoutGroup: {component.layoutGroup or 'unknown'}",
                f"- events: {_join(component.events)}",
                "",
            ]
        )

    lines.extend(["### User Actions", ""])
    for function in page.functions:
        if function.functionType != "event-handler":
            continue
        lines.extend(
            [
                f"#### {function.functionName}",
                f"- transactions: {_join(function.callsTransactions)}",
                f"- controls: {_join(function.controlsComponents)}",
                f"- readsDatasets: {_join(function.readsDatasets)}",
                f"- writesDatasets: {_join(function.writesDatasets)}",
                "",
            ]
        )

    lines.extend(["## Backend Integrated Analysis", ""])
    if package.backendTraces:
        for trace in package.backendTraces:
            lines.extend(
                [
                    f"### {trace.transactionId}",
                    f"- legacyUrl: {trace.url or 'unknown'}",
                    f"- controller: {_join_nonempty(trace.controllerClass, trace.controllerMethod)}",
                    f"- service: {_join_nonempty(trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod)}",
                    f"- dao: {_join_nonempty(trace.daoClass, trace.daoMethod)}",
                    f"- sqlMapId: {trace.sqlMapId or 'unknown'}",
                    f"- tables: {_join(trace.tableCandidates)}",
                    f"- responseFields: {_join(trace.responseFieldCandidates)}",
                    f"- querySummary: {trace.querySummary or 'unknown'}",
                    "",
                ]
            )
    else:
        lines.extend(["- No backend trace resolved.", ""])

    lines.extend(["## Related Screens", ""])
    if package.relatedPages:
        for related in package.relatedPages:
            lines.extend(
                [
                    f"### {related.target or related.navigationId}",
                    f"- relation: {related.navigationType or 'unknown'}",
                    f"- triggerFunction: {related.triggerFunction or 'unknown'}",
                    f"- resolutionStatus: {related.resolutionStatus or 'unknown'}",
                    f"- resolvedPath: {related.resolvedPath or 'unknown'}",
                    f"- relatedPageId: {related.pageId or 'unknown'}",
                    f"- relatedPageName: {related.pageName or 'unknown'}",
                    f"- relatedPageType: {related.pageType or 'unknown'}",
                    "",
                ]
            )
    else:
        lines.extend(["- No popup/subview target found.", ""])

    lines.extend(
        [
            "## Handoff Notes",
            "",
            "- Treat popup or subview targets as separate screens, not as inline sections of the current page.",
            "- Use stage 2 Vue config JSON as the implementation contract for frontend generation.",
            "- Keep ambiguous wrapper transactions in open questions until review.json resolves them.",
        ]
    )
    return "\n".join(lines)


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
