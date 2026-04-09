from __future__ import annotations

import re

from am_bridge.models import PageModel, RealtimeSubscriptionModel
from am_bridge.script_utils import extract_functions, find_named_calls, unquote
from am_bridge.source import PageSource


class RealtimeAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        script_functions = extract_functions(source.script_text)
        function_lookup = {function.functionName: function for function in model.functions}
        transaction_lookup = {
            transaction.transactionId: transaction for transaction in model.transactions
        }
        lifecycle_end = _resolve_lifecycle_end(model, script_functions)

        subscription_counter = 0
        seen: set[tuple[str, str, str, str]] = set()

        for script_function in script_functions:
            lifecycle_start = _resolve_lifecycle_start(script_function.name, model)

            for args in find_named_calls(script_function.body, "setInterval"):
                handler_name = _normalize_handler(args[0] if args else "")
                interval = _parse_interval(args[1] if len(args) > 1 else "")
                source_name = _derive_polling_source_name(handler_name, function_lookup, transaction_lookup)
                key = ("polling", source_name, handler_name, script_function.name)
                if key in seen:
                    continue
                seen.add(key)
                subscription_counter += 1

                target_datasets, target_components = _resolve_targets(
                    handler_name,
                    model,
                    function_lookup,
                    transaction_lookup,
                )
                model.realtimeSubscriptions.append(
                    RealtimeSubscriptionModel(
                        subscriptionId=f"RT-{subscription_counter:04d}",
                        sourceType="polling",
                        sourceName=source_name,
                        trigger=script_function.name,
                        lifecycleStart=lifecycle_start,
                        lifecycleEnd=lifecycle_end,
                        refreshIntervalMs=interval,
                        targetComponents=target_components,
                        targetDatasets=target_datasets,
                        errorPolicy=_infer_error_policy(script_function.body),
                    )
                )

            for call_name, source_type in (
                ("mqttSubscribe", "mqtt"),
                ("stompSubscribe", "stomp"),
                ("signalRSubscribe", "signalr"),
                ("subscribeTopic", "pubsub"),
                ("openSocket", "websocket"),
                ("connectSocket", "websocket"),
                ("registerHeartbeat", "heartbeat"),
            ):
                for args in find_named_calls(script_function.body, call_name):
                    source_name = unquote(args[0]) if args else ""
                    handler_name = _normalize_handler(args[1] if len(args) > 1 else "")
                    interval = _parse_interval(args[2] if len(args) > 2 else "")
                    key = (source_type, source_name, handler_name, script_function.name)
                    if key in seen:
                        continue
                    seen.add(key)
                    subscription_counter += 1

                    target_datasets, target_components = _resolve_targets(
                        handler_name,
                        model,
                        function_lookup,
                        transaction_lookup,
                    )
                    model.realtimeSubscriptions.append(
                        RealtimeSubscriptionModel(
                            subscriptionId=f"RT-{subscription_counter:04d}",
                            sourceType=source_type,
                            sourceName=source_name,
                            trigger=script_function.name,
                            lifecycleStart=lifecycle_start,
                            lifecycleEnd=lifecycle_end,
                            refreshIntervalMs=interval,
                            targetComponents=target_components,
                            targetDatasets=target_datasets,
                            errorPolicy=_infer_error_policy(
                                f"{script_function.body}\n{_function_body(handler_name, script_functions)}"
                            ),
                        )
                    )


def _resolve_lifecycle_start(function_name: str, model: PageModel) -> str:
    events_by_handler = {event.handlerFunction: event for event in model.events}
    reverse_calls: dict[str, set[str]] = {}
    for function in model.functions:
        for called in function.callsFunctions:
            reverse_calls.setdefault(called, set()).add(function.functionName)

    queue = [function_name]
    visited: set[str] = set()
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        event = events_by_handler.get(current)
        if event is not None and event.eventType == "lifecycle":
            return current

        for caller in sorted(reverse_calls.get(current, set())):
            queue.append(caller)

    event = events_by_handler.get(function_name)
    return event.handlerFunction if event is not None else ""


def _resolve_lifecycle_end(model: PageModel, script_functions) -> str:
    for event in model.events:
        lowered = f"{event.eventName} {event.handlerFunction}".lower()
        if any(token in lowered for token in ("close", "unload", "destroy")):
            return event.handlerFunction

    for script_function in script_functions:
        lowered = f"{script_function.name} {script_function.body}".lower()
        if any(token in lowered for token in ("clearinterval", "unsubscribe", "disconnect")):
            return script_function.name
    return ""


def _normalize_handler(raw_value: str) -> str:
    value = unquote(raw_value).strip()
    if not value or value.startswith("function"):
        return ""
    match = re.match(r"([A-Za-z_]\w*)$", value)
    return match.group(1) if match else ""


def _parse_interval(raw_value: str) -> int | None:
    match = re.search(r"(\d+)", raw_value or "")
    return int(match.group(1)) if match else None


def _derive_polling_source_name(
    handler_name: str,
    function_lookup,
    transaction_lookup,
) -> str:
    function = function_lookup.get(handler_name)
    if function is None:
        return handler_name

    for transaction_id in function.callsTransactions:
        transaction = transaction_lookup.get(transaction_id)
        if transaction is not None and transaction.url:
            return transaction.url

    return handler_name or "polling"


def _resolve_targets(handler_name: str, model: PageModel, function_lookup, transaction_lookup):
    target_datasets: set[str] = set()
    target_components: set[str] = set()

    function = function_lookup.get(handler_name)
    if function is not None:
        target_datasets.update(function.readsDatasets)
        target_datasets.update(function.writesDatasets)
        target_components.update(function.controlsComponents)

        for transaction_id in function.callsTransactions:
            transaction = transaction_lookup.get(transaction_id)
            if transaction is None:
                continue
            target_datasets.update(transaction.inputDatasets)
            target_datasets.update(transaction.outputDatasets)

    for component in model.components:
        dataset_candidates = {
            str(component.properties.get("BindDataset", "")),
            str(component.properties.get("InnerDataset", "")),
            str(component.properties.get("Dataset", "")),
            str(component.properties.get("ResultDataset", "")),
            str(component.properties.get("ImageDataset", "")),
        }
        if target_datasets & {candidate for candidate in dataset_candidates if candidate}:
            target_components.add(component.componentId)

    return sorted(target_datasets), sorted(target_components)


def _infer_error_policy(body: str) -> str:
    lowered = body.lower()
    if any(token in lowered for token in ("reconnect", "retry")):
        return "retry"
    if "alert(" in lowered:
        return "alert"
    if any(token in lowered for token in ("ignore", "silent")):
        return "ignore"
    return "callback-handling"


def _function_body(function_name: str, script_functions) -> str:
    for script_function in script_functions:
        if script_function.name == function_name:
            return script_function.body
    return ""
