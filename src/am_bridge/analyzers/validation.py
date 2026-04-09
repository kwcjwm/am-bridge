from __future__ import annotations

import re

from am_bridge.models import PageModel, ValidationRuleModel
from am_bridge.script_utils import extract_functions, extract_string_literals, find_if_blocks
from am_bridge.source import PageSource


class ValidationRuleAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        component_ids = {component.componentId for component in model.components}
        event_lookup = {event.handlerFunction: event for event in model.events}
        component_lookup = {component.componentId: component for component in model.components}
        rule_counter = 0
        seen: set[tuple[str, str, str, str]] = set()

        for script_function in extract_functions(source.script_text):
            trigger_timing = _infer_trigger_timing(
                script_function.name,
                event_lookup.get(script_function.name),
                component_lookup,
            )
            for block in find_if_blocks(script_function.body):
                validation_type = _infer_validation_type(block.condition, block.body)
                if not validation_type:
                    continue
                target_field = _find_target_field(block.condition, block.body, component_ids)
                if not target_field and validation_type == "custom":
                    continue
                message = _find_validation_message(block.body)
                key = (script_function.name, target_field, validation_type, block.condition)
                if key in seen:
                    continue
                seen.add(key)
                rule_counter += 1
                model.validationRules.append(
                    ValidationRuleModel(
                        ruleId=f"VAL-{rule_counter:04d}",
                        targetField=target_field,
                        validationType=validation_type,
                        triggerTiming=trigger_timing,
                        sourceFunction=script_function.name,
                        expression=block.condition,
                        message=message,
                    )
                )


def _infer_validation_type(condition: str, body: str) -> str:
    lowered = f"{condition} {body}".lower()
    if "confirm(" in lowered:
        return ""
    if not ("return false" in lowered or "alert(" in lowered or "throw" in lowered):
        return ""
    if any(token in lowered for token in ('== ""', "== ''", "trim(", "isnull(", "== null")):
        return "required"
    if re.search(r"!\s*[A-Za-z_]\w*\.Text", condition):
        return "required"
    if "length" in lowered:
        return "length"
    if any(token in lowered for token in ("isnumber", "isnumeric", "nan")):
        return "number"
    if any(token in lowered for token in (".match(", "regex", "pattern")):
        return "pattern"
    if any(token in lowered for token in (">", "<", ">=", "<=")) and any(
        word in lowered for word in ("date", "qty", "amount", "count")
    ):
        return "range"
    return "custom"


def _find_target_field(condition: str, body: str, component_ids: set[str]) -> str:
    haystack = f"{condition} {body}"
    for component_id in sorted(component_ids, key=len, reverse=True):
        if re.search(rf"\b{re.escape(component_id)}\b", haystack):
            return component_id
    dataset_column = re.search(r'"([A-Za-z_]\w*)"', haystack)
    return dataset_column.group(1) if dataset_column else ""


def _find_validation_message(body: str) -> str:
    alert_match = re.search(r"\balert\s*\((.+?)\)\s*;", body, re.DOTALL)
    if not alert_match:
        return ""
    literals = extract_string_literals(alert_match.group(1))
    return " ".join(part.strip() for part in literals if part.strip())


def _infer_trigger_timing(function_name: str, event, component_lookup) -> str:
    lowered = function_name.lower()
    if any(token in lowered for token in ("save", "submit", "register", "update")):
        return "save"
    if any(token in lowered for token in ("search", "query", "retrieve")):
        return "search"
    if event is not None:
        event_name = event.eventName.lower()
        if "changed" in event_name:
            return "change"
        if "focus" in event_name or "blur" in event_name:
            return "blur"
        if "click" in event_name:
            component = component_lookup.get(event.sourceComponentId)
            text = str(component.properties.get("Text", "")).lower() if component is not None else ""
            if any(token in text for token in ("저장", "save", "등록")):
                return "save"
            if any(token in text for token in ("조회", "search")):
                return "search"
            return "click"
    return "custom"
