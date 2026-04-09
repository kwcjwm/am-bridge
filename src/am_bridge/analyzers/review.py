from __future__ import annotations

import re

from am_bridge.models import PageModel, ReviewWorkflowModel
from am_bridge.script_utils import extract_functions
from am_bridge.source import PageSource


class ReviewWorkflowAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        script_functions = extract_functions(source.script_text)
        script_lookup = {function.name: function for function in script_functions}
        event_map = {
            event.handlerFunction: event.sourceComponentId
            for event in model.events
            if event.eventType == "user-action"
        }
        component_lookup = {component.componentId: component for component in model.components}

        workflow_counter = 0
        for dataset in model.datasets:
            if not _is_review_dataset(dataset):
                continue

            actions = []
            states = _collect_states(dataset, script_functions)
            roles: set[str] = set()

            for function_name, component_id in event_map.items():
                script_function = script_lookup.get(function_name)
                if script_function is None:
                    continue
                if not _is_review_action(script_function.name, script_function.body):
                    continue

                component = component_lookup.get(component_id)
                action_name = (
                    str(component.properties.get("Text", "")).strip() if component is not None else ""
                ) or function_name
                action_type = _infer_action_type(script_function.name, script_function.body)
                actions.append(
                    {
                        "actionName": action_name,
                        "actionType": action_type,
                        "handlerFunction": function_name,
                        "triggerComponentId": component_id,
                    }
                )
                roles.update(_extract_roles(script_function.body))

            workflow_counter += 1
            model.reviewWorkflows.append(
                ReviewWorkflowModel(
                    workflowId=f"REVIEW-{workflow_counter:04d}",
                    workflowType="vision-review" if model.imageVisionViews else "review",
                    sourceDatasetId=dataset.datasetId,
                    states=sorted(states),
                    actions=actions,
                    roles=sorted(roles),
                    approvalIntegration=model.platform.approvalRequired,
                    auditRequired=model.platform.approvalRequired or bool(roles),
                )
            )


def _is_review_dataset(dataset) -> bool:
    haystack = " ".join(
        [
            dataset.datasetId.lower(),
            *(column.name.lower() for column in dataset.columns),
        ]
    )
    return any(
        token in haystack
        for token in ("review", "judge", "defect", "inspection", "queue", "confidence")
    )


def _is_review_action(function_name: str, body: str) -> bool:
    lowered = f"{function_name} {body}".lower()
    return any(token in lowered for token in ("review", "judge", "approve", "reject", "defect"))


def _infer_action_type(function_name: str, body: str) -> str:
    lowered = f"{function_name} {body}".lower()
    if any(token in lowered for token in ("approve", "ok", "pass", "confirm")):
        return "approve"
    if any(token in lowered for token in ("reject", "ng", "fail", "rework")):
        return "reject"
    if "review" in lowered:
        return "review"
    return "action"


def _extract_roles(body: str) -> set[str]:
    return set(re.findall(r'"(ROLE_[A-Z0-9_]+|PERM_[A-Z0-9_]+|AUTH_[A-Z0-9_]+)"', body))


def _collect_states(dataset, script_functions) -> set[str]:
    states: set[str] = set()
    for record in dataset.defaultRecords:
        for key, value in record.items():
            lowered_key = key.lower()
            if any(token in lowered_key for token in ("status", "state", "judge", "review")):
                text = str(value).strip()
                if text:
                    states.add(text)

    for script_function in script_functions:
        if not _is_review_action(script_function.name, script_function.body):
            continue
        for match in re.finditer(r'"([A-Z][A-Z0-9_]+)"', script_function.body):
            token = match.group(1)
            if token in {"APPROVED", "REJECTED", "PENDING", "REVIEWING", "WAIT", "OK", "NG"}:
                states.add(token)
    return states
