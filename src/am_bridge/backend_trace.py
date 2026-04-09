from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from am_bridge.models import BackendTraceModel, PageModel, TransactionModel


REQUEST_MAPPING_RE = re.compile(
    r'@RequestMapping\s*\(\s*value\s*=\s*"([^"]+)"[^)]*\)',
    re.S,
)
METHOD_SIGNATURE_RE = re.compile(
    r'public\s+([A-Za-z0-9_<>\[\], ?]+)\s+([A-Za-z_]\w*)\s*\(',
    re.S,
)
CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_]\w*)")
IMPLEMENTS_RE = re.compile(r"\bclass\s+([A-Za-z_]\w*)[^{]*\bimplements\b([^{]+)\{", re.S)
FIELD_RE = re.compile(
    r'(?:@Resource\s*\(\s*name\s*=\s*"([^"]+)"\s*\)\s*)?'
    r'(?:private|protected)\s+([A-Za-z0-9_<>\.\[\]]+)\s+([A-Za-z_]\w*)\s*;',
    re.S,
)
METHOD_RE_TEMPLATE = r"public\s+[A-Za-z0-9_<>\[\], ?]+\s+{name}\s*\(([^)]*)\)\s*(?:throws[^{{]+)?\{{"
CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*\(")
SQL_CALL_RE = re.compile(r"\b(list|insert|update|delete|getSqlMapClientTemplate)\s*\(\s*\"([^\"]+)\"", re.I)
SQL_BLOCK_RE_TEMPLATE = r"<(select|insert|update|delete)\s+id=\"{sql_id}\"[^>]*>(.*?)</\1>"
RESULT_FIELD_RE = re.compile(r"\bas\s+([A-Za-z_]\w*)", re.I)
TABLE_RE = re.compile(r"\b(?:from|join)\s+([A-Za-z_][A-Za-z0-9_\.]*)", re.I)


@dataclass
class JavaMethodMatch:
    path: Path
    class_name: str
    method_name: str
    return_type: str
    params: str
    body: str
    fields: dict[str, tuple[str, str]]


def trace_backend_dependencies(page: PageModel, backend_roots: list[Path]) -> list[BackendTraceModel]:
    roots = [root.resolve() for root in backend_roots if root.exists()]
    if not roots:
        return []

    java_files = _collect_files(roots, {".java"})
    sql_files = _collect_files(roots, {".xml"})
    traces: list[BackendTraceModel] = []

    for transaction in page.transactions:
        if not transaction.url or _looks_dynamic_url(transaction.url):
            continue

        trace = BackendTraceModel(
            transactionId=transaction.transactionId,
            url=transaction.url,
            requestMapping=_normalize_request_path(transaction.url),
        )

        controller = _find_controller_method(trace.requestMapping, java_files)
        if controller is None:
            traces.append(trace)
            continue

        trace.controllerClass = controller.class_name
        trace.controllerMethod = controller.method_name
        trace.controllerMethodSignature = f"{controller.return_type} {controller.method_name}({controller.params})"
        trace.requestDtoType = _first_param_type(controller.params)
        trace.responseCarrierType = controller.return_type
        trace.sourceRefs.append(str(controller.path))

        service_field, service_method = _find_layer_call(controller.body, controller.fields, preferred_tokens=("service",))
        if service_field:
            service_type, service_resource = controller.fields[service_field]
            trace.serviceBeanName = service_resource
            trace.serviceInterface = service_type
            trace.serviceMethod = service_method
            service_impl = _find_service_impl(service_type, java_files)
            if service_impl is not None and service_method:
                trace.serviceImplClass = service_impl.class_name
                trace.sourceRefs.append(str(service_impl.path))
                service_text = service_impl.path.read_text(encoding="utf-8", errors="ignore")
                service_body = _extract_method_body(service_text, service_method) or service_text

                dao_field, dao_method = _find_layer_call(service_body, service_impl.fields, preferred_tokens=("dao", "mapper", "repository"))
                if dao_field:
                    dao_type, _ = service_impl.fields[dao_field]
                    trace.daoClass = dao_type
                    trace.daoMethod = dao_method
                    dao_impl = _find_named_class(dao_type, java_files)
                    if dao_impl is not None and dao_method:
                        trace.sourceRefs.append(str(dao_impl.path))
                        sql_map_id, sql_operation = _find_sql_map_call(dao_impl.body, dao_method)
                        trace.sqlMapId = sql_map_id
                        trace.sqlOperation = sql_operation

                        if sql_map_id:
                            sql_file, sql_block = _find_sql_block(sql_map_id, sql_files)
                            if sql_file is not None:
                                trace.sqlMapFile = str(sql_file)
                                trace.sourceRefs.append(str(sql_file))
                            if sql_block:
                                trace.querySummary = _summarize_sql(sql_block)
                                trace.tableCandidates = sorted(set(TABLE_RE.findall(sql_block)))
                                trace.responseFieldCandidates = _extract_response_fields(sql_block)

        trace.sourceRefs = sorted(dict.fromkeys(trace.sourceRefs))
        traces.append(trace)

    return traces


def _collect_files(roots: list[Path], suffixes: set[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                files.append(path.resolve())
    return files


def _normalize_request_path(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return parsed.path or url
    return url


def _looks_dynamic_url(url: str) -> bool:
    stripped = url.strip()
    return not stripped or any(token in stripped for token in ('"', "'", "+", "svc::"))


def _find_controller_method(request_path: str, java_files: list[Path]) -> JavaMethodMatch | None:
    for path in java_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        class_name = _extract_class_name(text, path)
        fields = _extract_fields(text)
        for match in REQUEST_MAPPING_RE.finditer(text):
            mapping = match.group(1)
            if mapping != request_path:
                continue
            method_match = METHOD_SIGNATURE_RE.search(text, match.end())
            if not method_match:
                continue
            return_type, method_name = method_match.groups()
            params_start = method_match.end() - 1
            params_end = _scan_balanced(text, params_start, open_char="(", close_char=")")
            params = text[params_start + 1 : params_end]
            body_start = text.find("{", params_end)
            if body_start == -1:
                continue
            body_end = _scan_balanced(text, body_start)
            body = text[body_start + 1 : body_end]
            return JavaMethodMatch(
                path=path,
                class_name=class_name,
                method_name=method_name,
                return_type=return_type.strip(),
                params=params.strip(),
                body=body,
                fields=fields,
            )
    return None


def _find_service_impl(service_type: str, java_files: list[Path]) -> JavaMethodMatch | None:
    impl = _find_implementing_class(service_type, java_files)
    if impl is not None:
        return impl
    if service_type.endswith("Service"):
        return _find_named_class(f"{service_type}Impl", java_files)
    return None


def _find_implementing_class(interface_name: str, java_files: list[Path]) -> JavaMethodMatch | None:
    for path in java_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = IMPLEMENTS_RE.search(text)
        if not match:
            continue
        class_name, interface_block = match.groups()
        if interface_name not in interface_block:
            continue
        return JavaMethodMatch(
            path=path,
            class_name=class_name,
            method_name="",
            return_type="",
            params="",
            body=text,
            fields=_extract_fields(text),
        )
    return None


def _find_named_class(class_name: str, java_files: list[Path]) -> JavaMethodMatch | None:
    for path in java_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        extracted = _extract_class_name(text, path)
        if extracted != class_name:
            continue
        return JavaMethodMatch(
            path=path,
            class_name=class_name,
            method_name="",
            return_type="",
            params="",
            body=text,
            fields=_extract_fields(text),
        )
    return None


def _find_layer_call(
    method_body: str,
    fields: dict[str, tuple[str, str]],
    preferred_tokens: tuple[str, ...],
) -> tuple[str, str]:
    candidates: list[tuple[int, str, str]] = []
    for match in CALL_RE.finditer(method_body):
        variable_name, method_name = match.groups()
        field = fields.get(variable_name)
        if field is None:
            continue
        type_name, _resource_name = field
        variable_lower = variable_name.lower()
        type_lower = type_name.lower()
        score = 0
        for token in preferred_tokens:
            if token in variable_lower:
                score += 6
            if token in type_lower:
                score += 5
        if type_name.endswith(("Service", "ServiceImpl", "DAO", "Mapper", "Repository")):
            score += 3
        if method_body[max(0, match.start() - 10) : match.start()].strip().endswith("return"):
            score += 1
        candidates.append((score, variable_name, method_name))

    if not candidates:
        return "", ""
    candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    _score, variable_name, method_name = candidates[0]
    return variable_name, method_name


def _find_sql_map_call(java_text: str, dao_method: str) -> tuple[str, str]:
    method_body = _extract_method_body(java_text, dao_method)
    if not method_body:
        return "", ""
    match = SQL_CALL_RE.search(method_body)
    if not match:
        return "", ""
    operation, sql_map_id = match.groups()
    return sql_map_id, operation.lower()


def _find_sql_block(sql_map_id: str, sql_files: list[Path]) -> tuple[Path | None, str]:
    escaped_id = re.escape(sql_map_id)
    pattern = re.compile(SQL_BLOCK_RE_TEMPLATE.format(sql_id=escaped_id), re.S | re.I)
    for path in sql_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = pattern.search(text)
        if match:
            _operation, block = match.groups()
            return path, _normalize_sql_block(block)
    return None, ""


def _extract_class_name(text: str, path: Path) -> str:
    match = CLASS_RE.search(text)
    if match:
        return match.group(1)
    return path.stem


def _extract_fields(text: str) -> dict[str, tuple[str, str]]:
    sanitized_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        sanitized_lines.append(re.sub(r"//.*", "", line))

    sanitized_text = "\n".join(sanitized_lines)
    sanitized_text = re.sub(r"/\*.*?\*/", "", sanitized_text, flags=re.S)

    fields: dict[str, tuple[str, str]] = {}
    for resource_name, type_name, variable_name in FIELD_RE.findall(sanitized_text):
        fields[variable_name] = (type_name.split(".")[-1], resource_name or "")
    return fields


def _extract_method_body(java_text: str, method_name: str) -> str:
    pattern = re.compile(METHOD_RE_TEMPLATE.format(name=re.escape(method_name)), re.S)
    match = pattern.search(java_text)
    if not match:
        return ""
    body_start = match.end() - 1
    body_end = _scan_balanced(java_text, body_start)
    return java_text[body_start + 1 : body_end]


def _scan_balanced(
    text: str,
    start_index: int,
    open_char: str = "{",
    close_char: str = "}",
) -> int:
    depth = 0
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    escape = False

    for index in range(start_index, len(text)):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
            continue

        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
            continue

        if in_single:
            if not escape and char == "'":
                in_single = False
            escape = char == "\\" and not escape
            continue

        if in_double:
            if not escape and char == '"':
                in_double = False
            escape = char == "\\" and not escape
            continue

        if char == "/" and next_char == "/":
            in_line_comment = True
            continue

        if char == "/" and next_char == "*":
            in_block_comment = True
            continue

        if char == "'":
            in_single = True
            escape = False
            continue

        if char == '"':
            in_double = True
            escape = False
            continue

        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return index

    raise ValueError(f"Unbalanced {open_char}{close_char} while parsing Java source")


def _first_param_type(params: str) -> str:
    if not params.strip():
        return ""
    first_param_chars: list[str] = []
    depth = 0
    angle_depth = 0
    in_single = False
    in_double = False

    for char in params:
        if in_single:
            first_param_chars.append(char)
            if char == "'":
                in_single = False
            continue

        if in_double:
            first_param_chars.append(char)
            if char == '"':
                in_double = False
            continue

        if char == "'":
            in_single = True
            first_param_chars.append(char)
            continue
        if char == '"':
            in_double = True
            first_param_chars.append(char)
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "<":
            angle_depth += 1
        elif char == ">":
            angle_depth = max(0, angle_depth - 1)
        elif char == "," and depth == 0 and angle_depth == 0:
            break

        first_param_chars.append(char)

    first_param = "".join(first_param_chars).strip()
    if not first_param:
        return ""

    while True:
        annotation_match = re.match(r'^\s*@[\w\.]+(?:\s*\([^)]*\))?\s*', first_param)
        if not annotation_match:
            break
        first_param = first_param[annotation_match.end() :].strip()

    tokens = [token for token in first_param.split() if token != "final"]
    if not tokens:
        return ""
    return tokens[0].split(".")[-1]


def _normalize_sql_block(sql: str) -> str:
    lines = [line.strip() for line in sql.splitlines() if line.strip()]
    return "\n".join(lines)


def _summarize_sql(sql: str) -> str:
    compact = re.sub(r"\s+", " ", sql).strip()
    if len(compact) <= 220:
        return compact
    return compact[:217] + "..."


def _extract_response_fields(sql: str) -> list[str]:
    aliased = RESULT_FIELD_RE.findall(sql)
    if aliased:
        return sorted(dict.fromkeys(aliased))

    header_match = re.search(r"\bselect\b(.*?)\bfrom\b", sql, re.I | re.S)
    if not header_match:
        return []

    fields: list[str] = []
    for raw_part in header_match.group(1).split(","):
        token = raw_part.strip().split()[-1]
        token = token.split(".")[-1]
        token = token.replace(")", "").replace("(", "")
        if re.fullmatch(r"[A-Za-z_]\w*", token):
            fields.append(token)
    return sorted(dict.fromkeys(fields))
