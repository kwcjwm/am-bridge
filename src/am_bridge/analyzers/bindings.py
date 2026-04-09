from __future__ import annotations

import re

from am_bridge.models import BindingModel, PageModel
from am_bridge.source import PageSource, get_attr, local_name, xml_source_ref


class BindingAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        binding_counter = 0

        for component in model.components:
            element = source.get_element(component.componentId)
            if element is None:
                continue

            bind_dataset = get_attr(element, "BindDataset")
            if bind_dataset:
                binding_counter += 1
                model.bindings.append(
                    BindingModel(
                        bindingId=f"BIND-{binding_counter:04d}",
                        componentId=component.componentId,
                        datasetId=bind_dataset,
                        bindingType="component-dataset",
                        direction="display-only",
                        sourceRefs=[xml_source_ref(source.path, element)],
                    )
                )

            inner_dataset = get_attr(element, "InnerDataset")
            if inner_dataset:
                for binding_type, column_name in (
                    ("inner-dataset", ""),
                    ("code-data", get_attr(element, "CodeColumn")),
                    ("display-data", get_attr(element, "DataColumn")),
                ):
                    binding_counter += 1
                    model.bindings.append(
                        BindingModel(
                            bindingId=f"BIND-{binding_counter:04d}",
                            componentId=component.componentId,
                            datasetId=inner_dataset,
                            columnName=column_name,
                            bindingType=binding_type,
                            direction="display-only",
                            sourceRefs=[xml_source_ref(source.path, element)],
                        )
                    )

            if local_name(element.tag).lower() == "grid":
                binding_counter = _append_grid_bindings(
                    binding_counter=binding_counter,
                    source=source,
                    element=element,
                    component_id=component.componentId,
                    bind_dataset=bind_dataset,
                    model=model,
                )

        binding_counter = _append_script_dataset_bindings(
            binding_counter=binding_counter,
            model=model,
            source=source,
        )


def _append_grid_bindings(
    binding_counter: int,
    source: PageSource,
    element,
    component_id: str,
    bind_dataset: str,
    model: PageModel,
) -> int:
    if not bind_dataset:
        return binding_counter

    for node in element.iter():
        if local_name(node.tag).lower() != "cell":
            continue
        column_name = get_attr(node, "colid")
        if not column_name:
            continue
        binding_counter += 1
        model.bindings.append(
            BindingModel(
                bindingId=f"BIND-{binding_counter:04d}",
                componentId=component_id,
                datasetId=bind_dataset,
                columnName=column_name,
                bindingType="grid-cell",
                direction="display-only",
                sourceRefs=[xml_source_ref(source.path, node)],
            )
        )
    return binding_counter


def _append_script_dataset_bindings(
    binding_counter: int,
    model: PageModel,
    source: PageSource,
) -> int:
    pattern = re.compile(
        r"\b(ds_[A-Za-z0-9_]+)\s*\.\s*(setColumn|getColumn)\s*\([^,]+,\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE,
    )

    for match in pattern.finditer(source.script_text):
        dataset_id = match.group(1)
        method_name = match.group(2).lower()
        column_name = match.group(3)
        binding_counter += 1
        model.bindings.append(
            BindingModel(
                bindingId=f"BIND-{binding_counter:04d}",
                componentId="",
                datasetId=dataset_id,
                columnName=column_name,
                bindingType=f"script-{method_name}",
                direction="two-way" if method_name == "setcolumn" else "display-only",
                sourceRefs=[str(source.path)],
            )
        )
    return binding_counter

