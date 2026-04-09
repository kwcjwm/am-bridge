from __future__ import annotations

from pathlib import Path

from am_bridge.models import PageModel
from am_bridge.source import PageSource, get_attr, local_name


GENERIC_FORM_IDS = {"form", "newform", "form1"}


class ShellAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        model.legacy.sourceFile = str(source.path)
        model.legacy.windowId = get_attr(source.root, "Id")

        if source.form is None:
            if not model.pageId:
                model.pageId = source.path.stem
            model.pageName = model.pageName or source.path.stem
            model.pageType = "unknown"
            return

        raw_form_id = get_attr(source.form, "Id") or source.path.stem
        title = get_attr(source.form, "Title") or Path(source.path).stem
        initial_event = get_attr(source.form, "OnLoadCompleted") or get_attr(
            source.form, "OnLoad"
        )

        model.pageId = _derive_page_id(raw_form_id, source.path)
        model.pageName = title
        model.pageType = _infer_page_type(source)

        model.legacy.formId = raw_form_id
        model.legacy.title = title
        model.legacy.initialEvent = initial_event
        model.legacy.legacyPageType = local_name(source.form.tag)

        model.layout = {
            "left": get_attr(source.form, "Left"),
            "top": get_attr(source.form, "Top"),
            "width": get_attr(source.form, "Width"),
            "height": get_attr(source.form, "Height"),
            "workArea": get_attr(source.form, "WorkArea"),
        }


def _derive_page_id(form_id: str, path: Path) -> str:
    normalized = (form_id or "").strip()
    if normalized.lower() in GENERIC_FORM_IDS:
        return path.stem
    return normalized or path.stem


def _infer_page_type(source: PageSource) -> str:
    path_name = source.path.stem.lower()
    if "popup" in path_name or "dialog" in path_name:
        return "popup"
    if source.form is None:
        return "unknown"
    if get_attr(source.form, "WorkArea").lower() == "true":
        return "main"
    return "dialog"
