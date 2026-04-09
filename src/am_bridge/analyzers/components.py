from __future__ import annotations

from collections import defaultdict
import xml.etree.ElementTree as ET

from am_bridge.models import ComponentModel, PageModel
from am_bridge.source import NON_COMPONENT_TAGS, PageSource, get_attr, local_name, xml_source_ref


class ComponentTreeAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        if source.form is None:
            return

        sibling_counter: defaultdict[str, int] = defaultdict(int)

        for element in source.form.iter():
            if element is source.form:
                continue
            tag_name = local_name(element.tag)
            if tag_name.lower() in NON_COMPONENT_TAGS:
                continue
            if _is_non_component_branch(source.form, element):
                continue

            sibling_counter[tag_name] += 1
            component_id = get_attr(element, "Id") or f"{tag_name}_{sibling_counter[tag_name]}"
            parent_id = _find_parent_component_id(source.form, element)
            events = sorted(key for key in element.attrib if key.lower().startswith("on"))

            model.components.append(
                ComponentModel(
                    componentId=component_id,
                    componentType=tag_name,
                    parentId=parent_id,
                    containerPath=_build_container_path(model.components, parent_id),
                    layoutGroup=_infer_layout_group(element),
                    styleKey="",
                    properties=dict(element.attrib),
                    events=events,
                    sourceRefs=[xml_source_ref(source.path, element)],
                )
            )


def _find_parent_component_id(form: ET.Element, target: ET.Element) -> str:
    for parent in form.iter():
        for child in parent:
            if child is target:
                return get_attr(parent, "Id")
    return ""


def _build_container_path(components: list[ComponentModel], parent_id: str) -> str:
    if not parent_id:
        return ""
    parent_lookup = {component.componentId: component for component in components}
    path: list[str] = []
    current_id = parent_id
    while current_id:
        path.append(current_id)
        current = parent_lookup.get(current_id)
        if current is None:
            break
        current_id = current.parentId
    return "/".join(reversed(path))


def _infer_layout_group(element: ET.Element) -> str:
    tag_name = local_name(element.tag).lower()
    top = int(get_attr(element, "Top", "0") or "0")

    if tag_name == "grid":
        return "data-panel"
    if tag_name in {"button", "combo", "edit", "maskedit", "calendar", "radio", "checkbox"}:
        return "search-panel" if top <= 120 else "form-panel"
    if tag_name in {"div", "tab"}:
        return "container-panel"
    return "content-panel"


def _is_non_component_branch(form: ET.Element, target: ET.Element) -> bool:
    skipped_branches = {"datasets", "dataset", "record", "colinfo", "format", "head", "body"}

    for parent in form.iter():
        for child in parent:
            if child is target:
                return local_name(parent.tag).lower() in skipped_branches
            if _contains(child, target):
                return local_name(parent.tag).lower() in skipped_branches or _is_non_component_branch(
                    child, target
                )
    return False


def _contains(parent: ET.Element, target: ET.Element) -> bool:
    for node in parent.iter():
        if node is target:
            return True
    return False
