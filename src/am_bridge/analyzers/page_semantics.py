from __future__ import annotations

import re
from collections import defaultdict

from am_bridge.models import BindingModel, ComponentModel, DatasetModel, PageModel, TransactionModel
from am_bridge.source import PageSource


INPUT_COMPONENT_TYPES = {
    "combo",
    "edit",
    "maskedit",
    "calendar",
    "radio",
    "checkbox",
    "textarea",
}

GRID_COMPONENT_TYPES = {"grid"}
CODE_DATASET_HINT = re.compile(r"(code|combo|lookup|list|common)", re.IGNORECASE)
SEARCH_DATASET_HINT = re.compile(r"(search|input|param|condition|filter|criteria)", re.IGNORECASE)
VIEW_DATASET_HINT = re.compile(r"(screen|view|url|menu|state|voinfo|param|temp|tmp)", re.IGNORECASE)


class PageSemanticsAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        if not model.datasets:
            return

        bindings_by_dataset: dict[str, list[BindingModel]] = defaultdict(list)
        functions_reading: dict[str, int] = defaultdict(int)
        functions_writing: dict[str, int] = defaultdict(int)
        tx_inputs: dict[str, list[TransactionModel]] = defaultdict(list)
        tx_outputs: dict[str, list[TransactionModel]] = defaultdict(list)

        for binding in model.bindings:
            if binding.datasetId:
                bindings_by_dataset[binding.datasetId].append(binding)

        for function in model.functions:
            for dataset_id in function.readsDatasets:
                functions_reading[dataset_id] += 1
            for dataset_id in function.writesDatasets:
                functions_writing[dataset_id] += 1

        for transaction in model.transactions:
            for dataset_id in transaction.inputDatasets:
                tx_inputs[dataset_id].append(transaction)
            for dataset_id in transaction.outputDatasets:
                tx_outputs[dataset_id].append(transaction)

        main_grid = _pick_main_grid(model.components)
        model.mainGridComponentId = main_grid.componentId if main_grid else ""

        for dataset in model.datasets:
            score = 0
            reasons: list[str] = []
            bindings = bindings_by_dataset.get(dataset.datasetId, [])
            bound_component_ids = sorted({binding.componentId for binding in bindings if binding.componentId})
            dataset.boundComponents = bound_component_ids

            grid_components = _bound_components_of_type(bindings, model.components, GRID_COMPONENT_TYPES)
            input_components = _bound_components_of_type(bindings, model.components, INPUT_COMPONENT_TYPES)
            code_bindings = [binding for binding in bindings if binding.bindingType in {"inner-dataset", "code-data", "display-data"}]
            input_transactions = tx_inputs.get(dataset.datasetId, [])
            output_transactions = tx_outputs.get(dataset.datasetId, [])
            read_count = functions_reading.get(dataset.datasetId, 0)
            write_count = functions_writing.get(dataset.datasetId, 0)

            usage = dataset.primaryUsage or dataset.role or "unknown"

            if main_grid and any(component.componentId == main_grid.componentId for component in grid_components):
                score += 120
                reasons.append(f"largest-grid:{main_grid.componentId}")
                usage = "main-grid"
            elif grid_components:
                score += 70
                reasons.append(f"grid-bound:{','.join(component.componentId for component in grid_components)}")
                usage = "grid-support"

            if output_transactions:
                score += 35 * len(output_transactions)
                reasons.append(
                    "transaction-output:" + ",".join(item.transactionId for item in output_transactions)
                )
                if usage in {"unknown", "request"}:
                    usage = "transaction-result"

            if input_transactions:
                score += 18 * len(input_transactions)
                reasons.append(
                    "transaction-input:" + ",".join(item.transactionId for item in input_transactions)
                )
                if usage in {"unknown", "view-state"}:
                    usage = "search-form"

            if input_components:
                score += 16
                reasons.append(
                    "input-bound:" + ",".join(component.componentId for component in input_components)
                )
                if usage in {"unknown", "transaction-result"}:
                    usage = "search-form"

            if write_count:
                score += min(12, 4 * write_count)
                reasons.append(f"script-write:{write_count}")
                if usage == "unknown":
                    usage = "working-state"

            if read_count:
                score += min(8, 2 * read_count)
                reasons.append(f"script-read:{read_count}")

            if len(dataset.columns) >= 4:
                score += 12
                reasons.append(f"wide-schema:{len(dataset.columns)}")
            elif len(dataset.columns) >= 2:
                score += 4
                reasons.append(f"schema:{len(dataset.columns)}")

            if dataset.defaultRecords:
                score += 4
                reasons.append(f"default-records:{len(dataset.defaultRecords)}")

            lowered_id = dataset.datasetId.lower()
            if code_bindings or CODE_DATASET_HINT.search(lowered_id):
                score -= 30
                reasons.append("code-lookup-signal")
                usage = "code-lookup"

            if VIEW_DATASET_HINT.search(lowered_id) and not output_transactions and not grid_components:
                score -= 18
                reasons.append("view-state-signal")
                if usage in {"unknown", "working-state", "search-form"}:
                    usage = "view-state"

            if SEARCH_DATASET_HINT.search(lowered_id) and not grid_components:
                score += 8
                reasons.append("search-id-signal")
                if usage in {"unknown", "working-state"}:
                    usage = "search-form"

            score = max(score, 0)
            dataset.salienceScore = score
            dataset.salienceReasons = reasons
            dataset.primaryUsage = _normalize_usage(usage)
            dataset.role = _normalize_dataset_role(dataset.role, dataset.primaryUsage)

        ordered = sorted(
            model.datasets,
            key=lambda item: (item.salienceScore, _dataset_role_rank(item.primaryUsage), item.datasetId),
            reverse=True,
        )

        if ordered and ordered[0].salienceScore > 0:
            model.primaryDatasetId = ordered[0].datasetId
            model.secondaryDatasetIds = [
                item.datasetId
                for item in ordered[1:]
                if item.salienceScore > 0
            ]
        else:
            model.primaryDatasetId = ""
            model.secondaryDatasetIds = []

        model.primaryTransactionIds = _infer_primary_transactions(model)
        model.interactionPattern = _infer_interaction_pattern(model)


def _pick_main_grid(components: list[ComponentModel]) -> ComponentModel | None:
    grids = [component for component in components if component.componentType.lower() in GRID_COMPONENT_TYPES]
    if not grids:
        return None
    return max(
        grids,
        key=lambda item: (_component_area(item), _component_metric(item, "Top"), item.componentId),
    )


def _bound_components_of_type(
    bindings: list[BindingModel],
    components: list[ComponentModel],
    target_types: set[str],
) -> list[ComponentModel]:
    lookup = {component.componentId: component for component in components}
    matched: list[ComponentModel] = []
    for binding in bindings:
        component = lookup.get(binding.componentId)
        if component and component.componentType.lower() in target_types:
            matched.append(component)
    return matched


def _component_metric(component: ComponentModel, key: str) -> int:
    raw_value = component.properties.get(key, "0")
    try:
        return int(str(raw_value).strip())
    except ValueError:
        return 0


def _component_area(component: ComponentModel) -> int:
    return max(_component_metric(component, "Width"), 0) * max(_component_metric(component, "Height"), 0)


def _normalize_usage(value: str) -> str:
    if value in {
        "main-grid",
        "grid-support",
        "transaction-result",
        "search-form",
        "code-lookup",
        "view-state",
        "working-state",
    }:
        return value
    return "unknown"


def _normalize_dataset_role(existing_role: str, primary_usage: str) -> str:
    if primary_usage in {"main-grid", "grid-support", "transaction-result"}:
        return "response"
    if primary_usage == "search-form":
        return "request"
    if primary_usage == "code-lookup":
        return "code"
    if primary_usage in {"view-state", "working-state"}:
        return "view-state"
    return existing_role or "unknown"


def _dataset_role_rank(primary_usage: str) -> int:
    order = {
        "main-grid": 6,
        "transaction-result": 5,
        "search-form": 4,
        "grid-support": 3,
        "working-state": 2,
        "view-state": 1,
        "code-lookup": 0,
    }
    return order.get(primary_usage, -1)


def _infer_primary_transactions(model: PageModel) -> list[str]:
    primary_dataset = model.primaryDatasetId
    if not primary_dataset:
        return []
    matched = [
        transaction.transactionId
        for transaction in model.transactions
        if primary_dataset in transaction.outputDatasets
    ]
    if matched:
        return matched
    return [
        transaction.transactionId
        for transaction in model.transactions
        if primary_dataset in transaction.inputDatasets
    ]


def _infer_interaction_pattern(model: PageModel) -> str:
    has_search_form = any(dataset.primaryUsage == "search-form" for dataset in model.datasets)
    has_grid = bool(model.mainGridComponentId)
    has_subview = any(item.navigationType == "subview" for item in model.navigation)
    has_popup = any(item.navigationType == "popup" for item in model.navigation)
    has_realtime = bool(model.realtimeSubscriptions)

    if has_search_form and has_grid and has_subview:
        return "search-grid-detail"
    if has_search_form and has_grid and has_popup:
        return "search-grid-popup"
    if has_search_form and has_grid and has_realtime:
        return "search-grid-monitor"
    if has_search_form and has_grid:
        return "search-grid"
    if has_grid and has_realtime:
        return "monitor-grid"
    if has_grid:
        return "grid-page"
    if has_popup:
        return "popup-driven"
    return "form-page"
