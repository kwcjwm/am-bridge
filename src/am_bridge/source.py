from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET


NON_COMPONENT_TAGS = {
    "window",
    "form",
    "datasets",
    "dataset",
    "contents",
    "script",
    "format",
    "columns",
    "col",
    "head",
    "body",
    "cell",
    "record",
    "colinfo",
}


def local_name(tag: str) -> str:
    if "}" in tag:
        tag = tag.split("}", 1)[1]
    return tag


def get_attr(element: ET.Element, name: str, default: str = "") -> str:
    for key, value in element.attrib.items():
        if key.lower() == name.lower():
            return value
    return default


@dataclass
class PageSource:
    path: Path
    text: str
    root: ET.Element
    form: ET.Element | None
    script_text: str
    element_lookup: dict[str, ET.Element] = field(default_factory=dict)

    def get_element(self, element_id: str) -> ET.Element | None:
        return self.element_lookup.get(element_id)


def load_page_source(path: str | Path) -> PageSource:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    root = ET.fromstring(text)

    form = None
    if local_name(root.tag).lower() == "form":
        form = root
    else:
        for child in root:
            if local_name(child.tag).lower() == "form":
                form = child
                break

    script_text = ""
    for child in root:
        if local_name(child.tag).lower() == "script":
            script_text = child.text or ""
            break

    lookup: dict[str, ET.Element] = {}
    if form is not None:
        for element in form.iter():
            element_id = get_attr(element, "Id")
            if element_id:
                lookup[element_id] = element

    return PageSource(
        path=file_path,
        text=text,
        root=root,
        form=form,
        script_text=script_text,
        element_lookup=lookup,
    )


def xml_source_ref(path: Path, element: ET.Element) -> str:
    element_id = get_attr(element, "Id")
    tag = local_name(element.tag)
    if element_id:
        return f"{path}:{tag}#{element_id}"
    return f"{path}:{tag}"

