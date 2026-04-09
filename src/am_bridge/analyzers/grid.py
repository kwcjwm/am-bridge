from __future__ import annotations

from am_bridge.models import PageModel
from am_bridge.source import PageSource, get_attr, local_name


class GridAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        for component in model.components:
            if component.componentType.lower() != "grid":
                continue

            element = source.get_element(component.componentId)
            if element is None:
                continue

            body_cells = _extract_band_cells(element, "body")
            head_cells = _extract_band_cells(element, "head")
            summary_cells = _extract_band_cells(element, "summary")

            component.properties["gridMeta"] = {
                "bodyColumns": body_cells,
                "headColumns": head_cells,
                "summaryColumns": summary_cells,
                "columnCount": len(body_cells),
                "hasSummary": bool(summary_cells),
                "editable": any(cell.get("display", "").lower() not in {"", "text"} for cell in body_cells),
            }


def _extract_band_cells(grid_element, band_name: str) -> list[dict[str, str]]:
    columns: list[dict[str, str]] = []
    for band in grid_element.iter():
        if local_name(band.tag).lower() != band_name:
            continue
        for cell in band:
            if local_name(cell.tag).lower() != "cell":
                continue
            columns.append(
                {
                    "band": band_name,
                    "col": get_attr(cell, "col"),
                    "columnName": get_attr(cell, "colid"),
                    "display": get_attr(cell, "display"),
                    "text": get_attr(cell, "text"),
                }
            )
    return columns

