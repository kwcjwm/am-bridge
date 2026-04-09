from __future__ import annotations

from am_bridge.models import EventModel, FunctionModel, PageModel, TransactionModel
from am_bridge.script_utils import (
    collect_component_usage,
    collect_dataset_usage,
    collect_function_calls,
    collect_platform_calls,
    extract_functions,
    find_named_calls,
    infer_effects,
    infer_event_type,
    infer_function_type,
    make_transaction_id,
    parse_dataset_mapping,
    unquote,
)
from am_bridge.source import PageSource, get_attr


class EventFunctionAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        functions = extract_functions(source.script_text)
        function_names = {item.name for item in functions}
        component_ids = {component.componentId for component in model.components}

        for script_function in functions:
            transaction_ids = [
                make_transaction_id(script_function.name, index)
                for index, _ in enumerate(find_named_calls(script_function.body, "transaction"), start=1)
            ]
            reads, writes = collect_dataset_usage(script_function.body)

            model.functions.append(
                FunctionModel(
                    functionName=script_function.name,
                    functionType=infer_function_type(script_function.name),
                    parameters=script_function.params,
                    callsFunctions=collect_function_calls(script_function.body, function_names),
                    callsTransactions=transaction_ids,
                    readsDatasets=reads,
                    writesDatasets=writes,
                    controlsComponents=collect_component_usage(script_function.body, component_ids),
                    platformCalls=collect_platform_calls(script_function.body),
                    sourceRefs=[str(source.path)],
                )
            )

        event_counter = 0
        if source.form is None:
            return

        for element in source.form.iter():
            source_component_id = get_attr(element, "Id") or get_attr(source.form, "Id")
            for key, value in element.attrib.items():
                if not key.lower().startswith("on"):
                    continue
                event_counter += 1
                script_function = next((item for item in functions if item.name == value), None)
                transaction_ids = []
                effects = []
                if script_function is not None:
                    transaction_ids = [
                        make_transaction_id(script_function.name, index)
                        for index, _ in enumerate(
                            find_named_calls(script_function.body, "transaction"), start=1
                        )
                    ]
                    effects = infer_effects(script_function.body, transaction_ids)

                model.events.append(
                    EventModel(
                        eventId=f"EVT-{event_counter:04d}",
                        sourceComponentId=source_component_id,
                        eventName=key,
                        handlerFunction=value,
                        eventType=infer_event_type(key, source_component_id),
                        triggerCondition="",
                        effects=effects,
                    )
                )


class TransactionAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        functions = extract_functions(source.script_text)

        for script_function in functions:
            calls = find_named_calls(script_function.body, "transaction")
            for index, args in enumerate(calls, start=1):
                padded = args + [""] * (6 - len(args))
                service_id, url, input_ds, output_ds, params, callback = padded[:6]
                model.transactions.append(
                    TransactionModel(
                        transactionId=make_transaction_id(script_function.name, index),
                        serviceId=unquote(service_id),
                        url=unquote(url),
                        inputDatasets=parse_dataset_mapping(input_ds),
                        outputDatasets=parse_dataset_mapping(output_ds),
                        parameters=unquote(params),
                        callbackFunction=unquote(callback),
                        wrapperFunction=script_function.name if script_function.name.lower().startswith("fncm") else "",
                        apiCandidate=unquote(url),
                        sourceRefs=[str(source.path)],
                    )
                )

