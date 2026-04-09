from __future__ import annotations

import re

from am_bridge.models import AlarmEventModel, PageModel
from am_bridge.script_utils import extract_functions
from am_bridge.source import PageSource


class AlarmEventAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        script_functions = extract_functions(source.script_text)
        function_bodies = {function.name: function.body.lower() for function in script_functions}

        for dataset in model.datasets:
            if not _is_alarm_dataset(dataset.datasetId, [column.name for column in dataset.columns]):
                continue

            target_components = _resolve_target_components(dataset.datasetId, model)
            subscription = _find_alarm_subscription(dataset.datasetId, target_components, model)

            model.alarmEvents.append(
                AlarmEventModel(
                    eventStreamId=f"ALARM:{dataset.datasetId}",
                    sourceType=subscription.sourceType if subscription is not None else "dataset",
                    severityField=_find_first_field(dataset, ("severity", "level", "priority", "prio")),
                    statusField=_find_first_field(
                        dataset,
                        ("status", "state", "alarmstatus", "ack", "confirm"),
                    ),
                    ackFunction=_find_action_function(function_bodies, ("ack",), ("alarm",)),
                    clearFunction=_find_action_function(function_bodies, ("clear", "reset"), ("alarm",)),
                    targetComponents=target_components,
                    refreshMode=_infer_refresh_mode(dataset.datasetId, target_components, model),
                    colorRuleSet=_infer_color_rule_set(dataset),
                )
            )


def _is_alarm_dataset(dataset_id: str, column_names: list[str]) -> bool:
    lowered_id = dataset_id.lower()
    lowered_columns = [column.lower() for column in column_names]

    if any(token in lowered_id for token in ("alarm", "alert")):
        return True

    has_alarm_identity = any(
        any(token in column for token in ("alarmid", "alarm", "alert"))
        for column in lowered_columns
    )
    has_alarm_state = any(
        any(token in column for token in ("severity", "alarmstatus", "ack", "confirm", "level"))
        for column in lowered_columns
    )
    return has_alarm_identity and has_alarm_state


def _resolve_target_components(dataset_id: str, model: PageModel) -> list[str]:
    target_components: list[str] = []
    for component in model.components:
        dataset_candidates = {
            str(component.properties.get("BindDataset", "")),
            str(component.properties.get("InnerDataset", "")),
            str(component.properties.get("Dataset", "")),
            str(component.properties.get("ResultDataset", "")),
        }
        haystack = f"{component.componentId} {component.componentType}".lower()
        if dataset_id in dataset_candidates or any(token in haystack for token in ("alarm", "event", "alert")):
            target_components.append(component.componentId)
    return sorted(set(target_components))


def _find_alarm_subscription(dataset_id: str, target_components: list[str], model: PageModel):
    for subscription in model.realtimeSubscriptions:
        if dataset_id in subscription.targetDatasets:
            return subscription
        if set(target_components) & set(subscription.targetComponents):
            return subscription
        if "alarm" in subscription.sourceName.lower():
            return subscription
    return None


def _find_first_field(dataset, tokens: tuple[str, ...]) -> str:
    for column in dataset.columns:
        lowered = column.name.lower()
        if any(token in lowered for token in tokens):
            return column.name
    return ""


def _find_action_function(
    function_bodies: dict[str, str],
    required_tokens: tuple[str, ...],
    context_tokens: tuple[str, ...],
) -> str:
    for function_name, body in function_bodies.items():
        lowered_name = function_name.lower()
        haystack = f"{lowered_name} {body}"
        if not all(token in haystack for token in context_tokens):
            continue

        if "alarm" in lowered_name and any(token in lowered_name for token in required_tokens):
            return function_name

        if any(f"alarm{token}(" in body for token in required_tokens):
            return function_name

        if any(re.search(rf"\b{re.escape(token)}\b", body) for token in required_tokens):
            return function_name
    return ""


def _infer_refresh_mode(dataset_id: str, target_components: list[str], model: PageModel) -> str:
    subscription = _find_alarm_subscription(dataset_id, target_components, model)
    if subscription is not None:
        return "realtime"

    for transaction in model.transactions:
        if dataset_id in transaction.outputDatasets and "alarm" in transaction.url.lower():
            return "polling"

    return "manual"


def _infer_color_rule_set(dataset) -> str:
    severity_field = _find_first_field(dataset, ("severity", "level", "priority", "prio"))
    if severity_field:
        return f"{severity_field}:critical=red,warning=yellow,normal=green"
    return ""
