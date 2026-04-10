from __future__ import annotations

import csv
import re
from io import StringIO
from typing import Any


def render_csv(rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> str:
    ordered_rows = list(rows)
    columns = list(fieldnames or _collect_fieldnames(ordered_rows))
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in ordered_rows:
        writer.writerow({column: _stringify(row.get(column, "")) for column in columns})
    return buffer.getvalue()


def render_markdown_table(columns: list[tuple[str, str]], rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["- None"]

    header = "| " + " | ".join(label for label, _key in columns) + " |"
    divider = "| " + " | ".join("---" for _label, _key in columns) + " |"
    body = [
        "| " + " | ".join(_escape_markdown_cell(row.get(key, "")) for _label, key in columns) + " |"
        for row in rows
    ]
    return [header, divider, *body]


def render_contents(section_titles: list[str]) -> list[str]:
    if not section_titles:
        return []
    lines = ["## Contents", ""]
    lines.extend(f"- [{title}](#{slug_anchor(title)})" for title in section_titles)
    lines.append("")
    return lines


def slug_anchor(value: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_]+", "-", normalized)


def markdown_link(label: str, target: str) -> str:
    return f"[{label}]({target})"


def join_values(values: list[str], empty: str = "none") -> str:
    items = [str(item) for item in values if str(item)]
    return ", ".join(items) if items else empty


def limit_text(value: str, limit: int = 120) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(limit - 3, 0)].rstrip() + "..."


def _collect_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    return fieldnames


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(_stringify(item) for item in value if _stringify(item))
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _escape_markdown_cell(value: Any) -> str:
    text = _stringify(value)
    text = text.replace("\n", " ").replace("|", "\\|")
    return text or "-"
