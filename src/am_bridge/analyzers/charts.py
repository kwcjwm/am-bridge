from __future__ import annotations

from am_bridge.models import ChartModel, PageModel
from am_bridge.source import PageSource


class ChartAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        for component in model.components:
            if not _is_chart_component(component.componentType, component.componentId, component.properties):
                continue

            dataset_id = (
                str(component.properties.get("BindDataset", ""))
                or str(component.properties.get("Dataset", ""))
                or str(component.properties.get("InnerDataset", ""))
            )
            category_column = (
                str(component.properties.get("CategoryColumn", ""))
                or str(component.properties.get("XAxisColumn", ""))
            )
            chart_type = (
                str(component.properties.get("ChartType", ""))
                or str(component.properties.get("SeriesType", ""))
                or component.componentType
            )
            title = (
                str(component.properties.get("Title", ""))
                or str(component.properties.get("Text", ""))
                or component.componentId
            )

            model.charts.append(
                ChartModel(
                    chartId=component.componentId,
                    chartType=chart_type.lower(),
                    title=title,
                    datasetId=dataset_id,
                    series=_parse_series(component.properties.get("Series", ""), chart_type),
                    refreshMode=_infer_refresh_mode(component.componentId, dataset_id, model),
                    options={
                        "categoryColumn": category_column,
                        "legend": str(component.properties.get("Legend", "")),
                        "palette": str(component.properties.get("Palette", "")),
                    },
                )
            )


def _is_chart_component(component_type: str, component_id: str, properties: dict[str, object]) -> bool:
    haystack = " ".join(
        [
            component_type.lower(),
            component_id.lower(),
            str(properties.get("ChartType", "")).lower(),
            str(properties.get("Series", "")).lower(),
        ]
    )
    return any(
        token in haystack
        for token in (
            "chart",
            "graph",
            "gauge",
            "trend",
            "histogram",
            "pareto",
            "heatmap",
            "spc",
        )
    )


def _parse_series(raw_value: object, fallback_type: str) -> list[dict[str, str]]:
    raw_text = str(raw_value or "").strip()
    if not raw_text:
        return []

    series: list[dict[str, str]] = []
    for item in raw_text.split(","):
        token = item.strip()
        if not token:
            continue
        if ":" in token:
            value_field, series_type = token.split(":", 1)
        else:
            value_field, series_type = token, fallback_type
        series.append(
            {
                "valueField": value_field.strip(),
                "seriesType": series_type.strip().lower(),
            }
        )
    return series


def _infer_refresh_mode(component_id: str, dataset_id: str, model: PageModel) -> str:
    for subscription in model.realtimeSubscriptions:
        if component_id in subscription.targetComponents or dataset_id in subscription.targetDatasets:
            return "realtime"

    for transaction in model.transactions:
        if dataset_id and dataset_id in transaction.outputDatasets:
            return "transaction"

    return "manual"
