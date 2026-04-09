from __future__ import annotations

import re

from am_bridge.models import PageModel, StateRuleModel
from am_bridge.script_utils import extract_functions, find_if_blocks, unquote
from am_bridge.source import PageSource


STATE_PROPERTIES = ("Enable", "Visible", "ReadOnly", "TabStop")
STATE_METHOD_MAP = {
    "setenable": "Enable",
    "set_enable": "Enable",
    "setvisible": "Visible",
    "set_visible": "Visible",
    "setreadonly": "ReadOnly",
    "set_readonly": "ReadOnly",
    "settabstop": "TabStop",
    "set_tabstop": "TabStop",
}


class StateRuleAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        component_lookup = {component.componentId: component for component in model.components}
        state_counter = 0
        seen: set[tuple[str, str, str, str, str]] = set()

        for component in model.components:
            for property_name in STATE_PROPERTIES:
                raw_value = str(component.properties.get(property_name, "")).strip()
                if not raw_value:
                    continue
                state_counter += 1
                key = ("__initial__", component.componentId, property_name, "", raw_value)
                seen.add(key)
                model.stateRules.append(
                    StateRuleModel(
                        ruleId=f"STATE-{state_counter:04d}",
                        targetComponentId=component.componentId,
                        stateProperty=property_name,
                        triggerCondition="",
                        sourceFunction="__initial__",
                        expression=raw_value,
                        targetValue=_coerce_value(raw_value),
                    )
                )

        for script_function in extract_functions(source.script_text):
            blocks = find_if_blocks(script_function.body)
            conditional_ranges = [(block.start, block.end) for block in blocks]

            for block in blocks:
                for component_id, state_property, expression in _extract_state_assignments(
                    block.body,
                    set(component_lookup),
                ):
                    key = (
                        script_function.name,
                        component_id,
                        state_property,
                        block.condition,
                        expression,
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    state_counter += 1
                    model.stateRules.append(
                        StateRuleModel(
                            ruleId=f"STATE-{state_counter:04d}",
                            targetComponentId=component_id,
                            stateProperty=state_property,
                            triggerCondition=block.condition,
                            sourceFunction=script_function.name,
                            expression=expression,
                            targetValue=_coerce_value(expression),
                        )
                    )

            for match_start, component_id, state_property, expression in _extract_state_assignments_with_pos(
                script_function.body,
                set(component_lookup),
            ):
                if any(start <= match_start <= end for start, end in conditional_ranges):
                    continue
                key = (script_function.name, component_id, state_property, "", expression)
                if key in seen:
                    continue
                seen.add(key)
                state_counter += 1
                model.stateRules.append(
                    StateRuleModel(
                        ruleId=f"STATE-{state_counter:04d}",
                        targetComponentId=component_id,
                        stateProperty=state_property,
                        triggerCondition="",
                        sourceFunction=script_function.name,
                        expression=expression,
                        targetValue=_coerce_value(expression),
                    )
                )


def _extract_state_assignments(text: str, component_ids: set[str]) -> list[tuple[str, str, str]]:
    return [
        (component_id, state_property, expression)
        for _, component_id, state_property, expression in _extract_state_assignments_with_pos(
            text,
            component_ids,
        )
    ]


def _extract_state_assignments_with_pos(
    text: str,
    component_ids: set[str],
) -> list[tuple[int, str, str, str]]:
    if not component_ids:
        return []

    component_pattern = "|".join(sorted((re.escape(item) for item in component_ids), key=len, reverse=True))
    direct_pattern = re.compile(
        rf"\b(?P<component>{component_pattern})\.(?P<property>{'|'.join(STATE_PROPERTIES)})\s*=\s*(?P<expr>[^;]+);?"
    )
    method_pattern = re.compile(
        rf"\b(?P<component>{component_pattern})\.(?P<method>{'|'.join(map(re.escape, STATE_METHOD_MAP))})\s*\((?P<expr>[^)]*)\)"
    )

    results: list[tuple[int, str, str, str]] = []
    for match in direct_pattern.finditer(text):
        results.append(
            (
                match.start(),
                match.group("component"),
                match.group("property"),
                match.group("expr").strip(),
            )
        )
    for match in method_pattern.finditer(text):
        results.append(
            (
                match.start(),
                match.group("component"),
                STATE_METHOD_MAP[match.group("method").lower()],
                match.group("expr").strip(),
            )
        )
    return sorted(results, key=lambda item: item[0])


def _coerce_value(expression: str):
    value = expression.strip()
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return unquote(value)
