from __future__ import annotations

import re

from am_bridge.models import CommandActionModel, PageModel
from am_bridge.script_utils import extract_functions, find_named_calls, unquote
from am_bridge.source import PageSource


class CommandActionAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        script_functions = extract_functions(source.script_text)
        event_map = {event.handlerFunction: event.sourceComponentId for event in model.events}
        component_lookup = {component.componentId: component for component in model.components}

        action_counter = 0
        for script_function in script_functions:
            if script_function.name not in event_map:
                continue
            if not _is_command_function(script_function.name, script_function.body):
                continue

            command_call = _extract_command_call(script_function.body)
            command_target = unquote(command_call[0]) if command_call else _infer_command_target(script_function)
            required_role = _extract_required_role(script_function.body, command_call)
            success_callback = unquote(command_call[2]) if len(command_call) > 2 else ""
            failure_callback = unquote(command_call[3]) if len(command_call) > 3 else ""
            trigger_component_id = event_map[script_function.name]
            trigger_component = component_lookup.get(trigger_component_id)
            action_counter += 1

            model.commandActions.append(
                CommandActionModel(
                    actionId=f"CMD-{action_counter:04d}",
                    actionName=_derive_action_name(script_function.name, trigger_component),
                    triggerComponentId=trigger_component_id,
                    commandTarget=command_target,
                    requiredRole=required_role,
                    confirmationRequired="confirm(" in script_function.body.lower(),
                    auditRequired=_requires_audit(script_function.body, required_role),
                    successCallback=success_callback,
                    failureCallback=failure_callback,
                )
            )


def _is_command_function(function_name: str, body: str) -> bool:
    lowered = f"{function_name} {body}".lower()
    if any(token in lowered for token in ("reviewapprove", "reviewreject", "alarmack", "alarmclear")):
        return False
    return any(
        token in lowered
        for token in (
            "commandexecute",
            "sendcommand",
            "controlcommand",
            "controlequipment",
            "equipment.start",
            "equipment.stop",
            "equipment.reset",
            " hold",
            " resume",
            " recipe",
        )
    )


def _extract_command_call(body: str) -> list[str]:
    for call_name in (
        "commandExecute",
        "sendCommand",
        "controlCommand",
        "controlEquipment",
        "issueCommand",
    ):
        calls = find_named_calls(body, call_name)
        if calls:
            return calls[0]
    return []


def _infer_command_target(script_function) -> str:
    lowered = script_function.name.lower()
    for token in ("start", "stop", "reset", "hold", "resume", "unlock", "lock"):
        if token in lowered:
            return f"equipment.{token}"
    return script_function.name


def _extract_required_role(body: str, command_call: list[str]) -> str:
    if len(command_call) > 1:
        candidate = unquote(command_call[1])
        if candidate.upper().startswith(("ROLE_", "PERM_", "AUTH_")):
            return candidate

    match = re.search(r'"(ROLE_[A-Z0-9_]+|PERM_[A-Z0-9_]+|AUTH_[A-Z0-9_]+)"', body)
    if match:
        return match.group(1)
    return ""


def _derive_action_name(function_name: str, trigger_component) -> str:
    if trigger_component is not None:
        text = str(trigger_component.properties.get("Text", "")).strip()
        if text:
            return text
    return function_name


def _requires_audit(body: str, required_role: str) -> bool:
    lowered = body.lower()
    return bool(
        required_role
        or "confirm(" in lowered
        or "approval" in lowered
        or "audit" in lowered
        or "log" in lowered
    )
