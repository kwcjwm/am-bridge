from __future__ import annotations

import re
import zlib

from am_bridge.models import MessageModel, PageModel
from am_bridge.script_utils import (
    extract_functions,
    extract_string_literals,
    find_named_calls,
    slug_token,
    unquote,
)
from am_bridge.source import PageSource


class MessageAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        component_lookup = {component.componentId: component for component in model.components}
        message_counter = 0
        seen: set[tuple[str, str, str, str]] = set()

        for component in model.components:
            text = str(component.properties.get("Text", "")).strip()
            if not text:
                continue
            message_type = _infer_component_message_type(component.componentType)
            key = ("xml-property", message_type, component.componentId, text)
            if key in seen:
                continue
            seen.add(key)
            message_counter += 1
            model.messages.append(
                MessageModel(
                    messageId=f"MSG-{message_counter:04d}",
                    sourceType="xml-property",
                    messageType=message_type,
                    text=text,
                    sourceFunction="",
                    targetComponentId=component.componentId,
                    i18nKeyCandidate=_build_i18n_key(model.pageId, message_type, text),
                    sourceRefs=component.sourceRefs,
                )
            )

        for script_function in extract_functions(source.script_text):
            for call_name, message_type in (("alert", "alert"), ("confirm", "confirm")):
                for args in find_named_calls(script_function.body, call_name):
                    text = _normalize_message_text(args[0] if args else "")
                    if not text:
                        continue
                    key = ("script-call", message_type, script_function.name, text)
                    if key in seen:
                        continue
                    seen.add(key)
                    message_counter += 1
                    model.messages.append(
                        MessageModel(
                            messageId=f"MSG-{message_counter:04d}",
                            sourceType="script-call",
                            messageType=message_type,
                            text=text,
                            sourceFunction=script_function.name,
                            targetComponentId="",
                            i18nKeyCandidate=_build_i18n_key(model.pageId, message_type, text),
                            sourceRefs=[str(source.path)],
                        )
                    )

            for component_id, text in _extract_text_assignments(script_function.body, set(component_lookup)):
                key = ("script-assignment", "status-text", component_id, text)
                if key in seen:
                    continue
                seen.add(key)
                message_counter += 1
                model.messages.append(
                    MessageModel(
                        messageId=f"MSG-{message_counter:04d}",
                        sourceType="script-assignment",
                        messageType="status-text",
                        text=text,
                        sourceFunction=script_function.name,
                        targetComponentId=component_id,
                        i18nKeyCandidate=_build_i18n_key(model.pageId, "status", text),
                        sourceRefs=[str(source.path)],
                    )
                )

        if model.messages:
            summary = ", ".join(sorted({message.text for message in model.messages}))
            model.notes = summary if not model.notes else f"{model.notes}\n{summary}"


def _infer_component_message_type(component_type: str) -> str:
    lowered = component_type.lower()
    if lowered == "button":
        return "action-label"
    if lowered in {"static", "label"}:
        return "label"
    return "component-text"


def _normalize_message_text(expression: str) -> str:
    value = unquote(expression)
    if value != expression.strip():
        return value.strip()
    literals = extract_string_literals(expression)
    return " ".join(part.strip() for part in literals if part.strip())


def _extract_text_assignments(text: str, component_ids: set[str]) -> list[tuple[str, str]]:
    if not component_ids:
        return []
    component_pattern = "|".join(sorted((re.escape(item) for item in component_ids), key=len, reverse=True))
    assignment_pattern = re.compile(
        rf"\b(?P<component>{component_pattern})\.Text\s*=(?!=)\s*(?P<expr>[^;]+);"
    )
    method_pattern = re.compile(
        rf"\b(?P<component>{component_pattern})\.(?:setText|set_text)\s*\((?P<expr>[^)]*)\)"
    )

    results: list[tuple[str, str]] = []
    for pattern in (assignment_pattern, method_pattern):
        for match in pattern.finditer(text):
            normalized = _normalize_message_text(match.group("expr"))
            if normalized:
                results.append((match.group("component"), normalized))
    return results


def _build_i18n_key(page_id: str, message_type: str, text: str) -> str:
    page_part = re.sub(r"[^a-z0-9]+", "-", page_id.lower()).strip("-") or "page"
    text_part = slug_token(text).lower()[:24]
    if not text_part or text_part == "unknown":
        text_part = f"msg-{zlib.crc32(text.encode('utf-8')):08x}"
    return f"{page_part}.{message_type}.{text_part}"
