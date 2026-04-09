from __future__ import annotations

from collections import Counter, defaultdict
import re

from am_bridge.models import PageModel, StyleModel
from am_bridge.source import PageSource


STYLE_PROPERTY_MAP = {
    "bkcolor": "background-color",
    "background": "background",
    "backgroundcolor": "background-color",
    "color": "text-color",
    "font": "font",
    "align": "text-align",
    "border": "border",
    "bordercolor": "border-color",
    "bordertype": "border-style",
    "cssclass": "class",
    "class": "class",
    "style": "style",
    "image": "image",
    "icon": "icon",
}


class StyleAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        collected = []
        counts: Counter[tuple[str, str]] = Counter()

        for component in model.components:
            for key, value in component.properties.items():
                normalized_property = STYLE_PROPERTY_MAP.get(key.lower())
                raw_value = str(value).strip()
                if not normalized_property or not raw_value:
                    continue
                collected.append((component.componentId, normalized_property, raw_value, component.sourceRefs))
                counts[(normalized_property, raw_value)] += 1

        tokens_by_component: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
        for index, (component_id, property_name, raw_value, source_refs) in enumerate(collected, start=1):
            token_candidate = _build_token_candidate(property_name, raw_value)
            usage_scope = _infer_usage_scope(property_name, raw_value, counts[(property_name, raw_value)])
            model.styles.append(
                StyleModel(
                    styleId=f"STYLE-{index:04d}",
                    componentId=component_id,
                    property=property_name,
                    rawValue=raw_value,
                    tokenCandidate=token_candidate,
                    usageScope=usage_scope,
                )
            )
            tokens_by_component[component_id].append((usage_scope, token_candidate))

        component_lookup = {component.componentId: component for component in model.components}
        for component_id, tokens in tokens_by_component.items():
            component = component_lookup.get(component_id)
            if component is None or component.styleKey:
                continue
            preferred = next((token for scope, token in tokens if scope == "shared"), "")
            component.styleKey = preferred or tokens[0][1]


def _build_token_candidate(property_name: str, raw_value: str) -> str:
    if property_name == "class":
        return raw_value.strip()

    slug = re.sub(r"[^a-z0-9]+", "-", raw_value.lower()).strip("-")
    if not slug:
        slug = "default"
    if len(slug) > 36:
        slug = slug[:36].rstrip("-")
    prefix = {
        "background-color": "bg",
        "text-color": "text",
        "font": "font",
        "text-align": "align",
        "border": "border",
        "border-color": "border-color",
        "border-style": "border-style",
        "image": "image",
        "icon": "icon",
    }.get(property_name, property_name.replace("_", "-"))
    return f"{prefix}-{slug}"


def _infer_usage_scope(property_name: str, raw_value: str, frequency: int) -> str:
    if property_name == "class":
        return "shared"
    if frequency > 1:
        return "shared"
    if raw_value.startswith("#"):
        return "page"
    return "component"
