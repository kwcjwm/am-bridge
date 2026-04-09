from __future__ import annotations

from am_bridge.models import ImageVisionViewModel, PageModel
from am_bridge.script_utils import extract_functions
from am_bridge.source import PageSource


class ImageVisionAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        script_functions = extract_functions(source.script_text)
        dataset_lookup = {dataset.datasetId: dataset for dataset in model.datasets}

        for component in model.components:
            if not _is_image_vision_component(component.componentType, component.componentId, component.properties):
                continue

            result_dataset_id = _resolve_result_dataset(component.properties)
            image_source = _build_image_source(component.properties, result_dataset_id)
            overlay_types = _collect_overlay_types(component.properties, script_functions, component.componentId)
            interactions = _collect_interactions(component.properties, script_functions, component.componentId)

            dataset = dataset_lookup.get(result_dataset_id)
            result_fields = []
            if dataset is not None:
                result_fields = [
                    column.name for column in dataset.columns if _is_vision_result_field(column.name)
                ]

            model.imageVisionViews.append(
                ImageVisionViewModel(
                    viewerId=component.componentId,
                    viewerType=_infer_viewer_type(component.componentType, component.properties),
                    imageSource=image_source,
                    overlayEnabled=bool(overlay_types),
                    overlayTypes=overlay_types,
                    interactions=interactions,
                    resultDatasetId=result_dataset_id,
                    resultFields=result_fields,
                )
            )


def _is_image_vision_component(component_type: str, component_id: str, properties: dict[str, object]) -> bool:
    haystack = " ".join(
        [
            component_type.lower(),
            component_id.lower(),
            str(properties.get("ImageUrlField", "")).lower(),
            str(properties.get("CameraStreamUrl", "")).lower(),
            str(properties.get("Overlay", "")).lower(),
            str(properties.get("OverlayTypes", "")).lower(),
        ]
    )
    return any(
        token in haystack
        for token in ("image", "viewer", "canvas", "video", "camera", "picture", "overlay", "roi")
    )


def _resolve_result_dataset(properties: dict[str, object]) -> str:
    for key in ("ResultDataset", "ImageDataset", "BindDataset", "Dataset", "InnerDataset"):
        value = str(properties.get(key, "")).strip()
        if value:
            return value
    return ""


def _build_image_source(properties: dict[str, object], dataset_id: str) -> dict[str, str]:
    if properties.get("CameraStreamUrl"):
        return {
            "mode": "stream",
            "url": str(properties.get("CameraStreamUrl", "")),
        }
    if properties.get("ImageUrlField"):
        return {
            "mode": "dataset-field",
            "datasetId": dataset_id,
            "field": str(properties.get("ImageUrlField", "")),
        }
    if properties.get("ImageUrl"):
        return {
            "mode": "static-url",
            "url": str(properties.get("ImageUrl", "")),
        }
    return {
        "mode": "unknown",
        "datasetId": dataset_id,
    }


def _collect_overlay_types(properties: dict[str, object], script_functions, component_id: str) -> list[str]:
    overlay_tokens: set[str] = set()

    for key in ("Overlay", "OverlayTypes"):
        raw_value = str(properties.get(key, ""))
        for item in raw_value.replace(";", ",").split(","):
            token = item.strip().lower()
            if token:
                overlay_tokens.add(token)

    for script_function in script_functions:
        lowered = script_function.body.lower()
        if component_id.lower() not in lowered:
            continue
        for token in ("bbox", "label", "roi", "mask", "contour", "heatmap"):
            if token in lowered:
                overlay_tokens.add(token)

    return sorted(overlay_tokens)


def _collect_interactions(properties: dict[str, object], script_functions, component_id: str) -> list[str]:
    interaction_tokens: set[str] = set()

    for item in str(properties.get("InteractionMode", "")).replace(";", ",").split(","):
        token = item.strip().lower()
        if token:
            interaction_tokens.add(token)

    for script_function in script_functions:
        lowered = script_function.body.lower()
        if component_id.lower() not in lowered:
            continue
        for token in ("zoom", "pan", "roi", "draw", "measure", "select", "review"):
            if token in lowered:
                interaction_tokens.add(token)

    return sorted(interaction_tokens)


def _infer_viewer_type(component_type: str, properties: dict[str, object]) -> str:
    lowered = component_type.lower()
    if "camera" in lowered or properties.get("CameraStreamUrl"):
        return "camera-stream"
    if "video" in lowered:
        return "video-viewer"
    if properties.get("Overlay") or properties.get("OverlayTypes"):
        return "image-review"
    return lowered or "image-viewer"


def _is_vision_result_field(column_name: str) -> bool:
    lowered = column_name.lower()
    return any(
        token in lowered
        for token in (
            "defect",
            "judge",
            "review",
            "confidence",
            "score",
            "image",
            "x",
            "y",
            "width",
            "height",
            "roi",
        )
    )
