from __future__ import annotations

import re

from am_bridge.models import DatasetColumn, DatasetModel, PageModel
from am_bridge.source import PageSource, get_attr, local_name, xml_source_ref


class DatasetAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        if source.form is None:
            return

        for datasets_node in source.form:
            if local_name(datasets_node.tag).lower() != "datasets":
                continue
            for dataset in datasets_node:
                if local_name(dataset.tag).lower() != "dataset":
                    continue

                dataset_id = get_attr(dataset, "Id")
                if not dataset_id:
                    continue

                columns: list[DatasetColumn] = []
                default_records: list[dict[str, str]] = []

                for node in dataset.iter():
                    lowered = local_name(node.tag).lower()
                    if lowered == "colinfo":
                        size_value = get_attr(node, "size")
                        columns.append(
                            DatasetColumn(
                                name=get_attr(node, "id"),
                                type=get_attr(node, "type"),
                                size=int(size_value) if size_value.isdigit() else None,
                                semanticType=_infer_semantic_type(get_attr(node, "id")),
                            )
                        )
                    elif lowered == "record":
                        record: dict[str, str] = {}
                        for column_node in list(node):
                            record[local_name(column_node.tag)] = (column_node.text or "").strip()
                        if record:
                            default_records.append(record)

                model.datasets.append(
                    DatasetModel(
                        datasetId=dataset_id,
                        role=_infer_dataset_role(dataset_id),
                        columns=columns,
                        defaultRecords=default_records,
                        usageContexts=_infer_usage_contexts(dataset_id, source),
                        sourceRefs=[xml_source_ref(source.path, dataset)],
                    )
                )


def _infer_dataset_role(dataset_id: str) -> str:
    lowered = dataset_id.lower()
    if re.search(r"(search|input|param|request)", lowered):
        return "request"
    if re.search(r"(result|output|list|grid)", lowered):
        return "response"
    if re.search(r"(code|combo|lookup)", lowered):
        return "code"
    if re.search(r"(state|flag|status|view)", lowered):
        return "view-state"
    if re.search(r"(realtime|alarm|event)", lowered):
        return "realtime"
    return "unknown"


def _infer_semantic_type(column_name: str) -> str:
    lowered = column_name.lower()
    if lowered.endswith("id") or lowered.endswith("no"):
        return "id"
    if "code" in lowered:
        return "code"
    if "name" in lowered:
        return "name"
    if "date" in lowered or "time" in lowered:
        return "time"
    if "status" in lowered or "state" in lowered:
        return "status"
    return ""


def _infer_usage_contexts(dataset_id: str, source: PageSource) -> list[str]:
    contexts: list[str] = []
    if dataset_id in source.script_text:
        contexts.append("script")
    for element in source.element_lookup.values():
        if dataset_id in element.attrib.values():
            contexts.append("component")
            break
    return sorted(set(contexts))

