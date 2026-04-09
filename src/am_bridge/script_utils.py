from __future__ import annotations

from dataclasses import dataclass
import re


RESERVED_CALL_NAMES = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "function",
    "transaction",
    "alert",
    "confirm",
    "Dialog",
    "Quote",
    "parseInt",
    "parseFloat",
    "setTimeout",
    "setInterval",
}

DATASET_WRITE_METHODS = {
    "setcolumn",
    "addrow",
    "appendrow",
    "cleardata",
    "copydata",
    "deleterow",
    "insertrow",
}

DATASET_READ_METHODS = {
    "getcolumn",
    "getrowcount",
    "findrow",
    "getsum",
    "getcasecount",
}

PLATFORM_HINTS = ("approval", "mail", "auth", "permission", "menu")


@dataclass
class ScriptFunction:
    name: str
    params: list[str]
    body: str
    start: int
    end: int


@dataclass
class ConditionalBlock:
    condition: str
    body: str
    start: int
    end: int


def _scan_balanced(text: str, start_index: int, open_char: str, close_char: str) -> int:
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

    raise ValueError(f"Could not find closing {close_char!r}")


def _scan_statement_end(text: str, start_index: int) -> int:
    depth_round = depth_square = depth_curly = 0
    in_single = False
    in_double = False
    escape = False

    for index in range(start_index, len(text)):
        char = text[index]

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

        if char == "'":
            in_single = True
            escape = False
            continue

        if char == '"':
            in_double = True
            escape = False
            continue

        if char == "(":
            depth_round += 1
        elif char == ")":
            depth_round -= 1
        elif char == "[":
            depth_square += 1
        elif char == "]":
            depth_square -= 1
        elif char == "{":
            depth_curly += 1
        elif char == "}":
            if depth_curly == 0:
                return index - 1
            depth_curly -= 1

        if char == ";" and depth_round == 0 and depth_square == 0 and depth_curly == 0:
            return index

    return len(text) - 1


def _strip_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    in_single = False
    in_double = False
    escape = False

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_single:
            result.append(char)
            if not escape and char == "'":
                in_single = False
            escape = char == "\\" and not escape
            index += 1
            continue

        if in_double:
            result.append(char)
            if not escape and char == '"':
                in_double = False
            escape = char == "\\" and not escape
            index += 1
            continue

        if char == "'":
            in_single = True
            escape = False
            result.append(char)
            index += 1
            continue

        if char == '"':
            in_double = True
            escape = False
            result.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            result.append(" ")
            result.append(" ")
            index += 2
            while index < len(text) and text[index] != "\n":
                result.append(" ")
                index += 1
            continue

        if char == "/" and next_char == "*":
            result.append(" ")
            result.append(" ")
            index += 2
            while index < len(text):
                current = text[index]
                following = text[index + 1] if index + 1 < len(text) else ""
                if current == "*" and following == "/":
                    result.append(" ")
                    result.append(" ")
                    index += 2
                    break
                result.append("\n" if current == "\n" else " ")
                index += 1
            continue

        result.append(char)
        index += 1

    return "".join(result)


def extract_functions(script: str) -> list[ScriptFunction]:
    functions: list[ScriptFunction] = []
    pattern = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")

    for match in pattern.finditer(script):
        name = match.group(1)
        open_paren = match.end() - 1
        close_paren = _scan_balanced(script, open_paren, "(", ")")
        params_text = script[open_paren + 1 : close_paren].strip()
        params = [part.strip() for part in params_text.split(",") if part.strip()]

        body_start = close_paren + 1
        while body_start < len(script) and script[body_start].isspace():
            body_start += 1
        if body_start >= len(script) or script[body_start] != "{":
            continue
        body_end = _scan_balanced(script, body_start, "{", "}")
        body = script[body_start + 1 : body_end]

        functions.append(
            ScriptFunction(
                name=name,
                params=params,
                body=body,
                start=match.start(),
                end=body_end,
            )
        )

    return functions


def split_arguments(text: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    depth_round = depth_square = depth_curly = 0
    in_single = False
    in_double = False
    escape = False

    for char in text:
        if in_single:
            current.append(char)
            if not escape and char == "'":
                in_single = False
            escape = char == "\\" and not escape
            continue

        if in_double:
            current.append(char)
            if not escape and char == '"':
                in_double = False
            escape = char == "\\" and not escape
            continue

        if char == "'":
            in_single = True
            current.append(char)
            escape = False
            continue

        if char == '"':
            in_double = True
            current.append(char)
            escape = False
            continue

        if char == "(":
            depth_round += 1
        elif char == ")":
            depth_round -= 1
        elif char == "[":
            depth_square += 1
        elif char == "]":
            depth_square -= 1
        elif char == "{":
            depth_curly += 1
        elif char == "}":
            depth_curly -= 1

        if (
            char == ","
            and depth_round == 0
            and depth_square == 0
            and depth_curly == 0
        ):
            args.append("".join(current).strip())
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return args


def find_named_calls(script_body: str, call_name: str) -> list[list[str]]:
    results: list[list[str]] = []
    clean_body = _strip_comments(script_body)
    pattern = re.compile(rf"\b{re.escape(call_name)}\s*\(")

    for match in pattern.finditer(clean_body):
        open_paren = match.end() - 1
        close_paren = _scan_balanced(clean_body, open_paren, "(", ")")
        args_text = clean_body[open_paren + 1 : close_paren]
        results.append(split_arguments(args_text))

    return results


def find_if_blocks(script_body: str) -> list[ConditionalBlock]:
    results: list[ConditionalBlock] = []
    pattern = re.compile(r"\bif\s*\(")

    for match in pattern.finditer(script_body):
        open_paren = match.end() - 1
        close_paren = _scan_balanced(script_body, open_paren, "(", ")")
        condition = script_body[open_paren + 1 : close_paren].strip()

        body_start = close_paren + 1
        while body_start < len(script_body) and script_body[body_start].isspace():
            body_start += 1
        if body_start >= len(script_body):
            continue

        if script_body[body_start] == "{":
            body_end = _scan_balanced(script_body, body_start, "{", "}")
            body = script_body[body_start + 1 : body_end].strip()
            end = body_end
        else:
            body_end = _scan_statement_end(script_body, body_start)
            body = script_body[body_start : body_end + 1].strip().rstrip(";")
            end = body_end

        results.append(
            ConditionalBlock(
                condition=condition,
                body=body,
                start=match.start(),
                end=end,
            )
        )

    return results


def slug_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", value).upper() or "UNKNOWN"


def make_transaction_id(function_name: str, ordinal: int) -> str:
    return f"TX-{slug_token(function_name)}-{ordinal}"


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_dataset_mapping(value: str) -> list[str]:
    unquoted = unquote(value)
    if not unquoted:
        return []

    dataset_ids: list[str] = []
    for token in unquoted.split():
        if "=" in token:
            left = token.split("=", 1)[0].strip()
            if left:
                dataset_ids.append(left)
        else:
            dataset_ids.append(token.strip())
    return [item for item in dataset_ids if item]


def infer_function_type(name: str) -> str:
    lowered = name.lower()
    if lowered.endswith("callback"):
        return "callback"
    if lowered.endswith("onclick") or "_on" in lowered:
        return "event-handler"
    if lowered.startswith("fn"):
        return "helper"
    return "helper"


def infer_event_type(event_name: str, component_id: str) -> str:
    lowered = event_name.lower()
    if any(token in lowered for token in ("load", "close", "unload", "destroy")):
        return "lifecycle"
    if component_id.lower().startswith("form"):
        return "lifecycle"
    if "timer" in lowered:
        return "timer"
    if "click" in lowered or "changed" in lowered or "sel" in lowered:
        return "user-action"
    return "unknown"


def infer_effects(body: str, transaction_ids: list[str]) -> list[str]:
    clean_body = _strip_comments(body)
    effects = list(transaction_ids)
    if "Dialog(" in clean_body:
        effects.append("navigation:popup")
    if ".Url=" in clean_body or ".Url =" in clean_body:
        effects.append("navigation:subview")
    if "alert(" in clean_body:
        effects.append("message:alert")
    return effects


def collect_function_calls(body: str, known_function_names: set[str]) -> list[str]:
    clean_body = _strip_comments(body)
    pattern = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
    calls: list[str] = []
    for match in pattern.finditer(clean_body):
        name = match.group(1)
        if name in RESERVED_CALL_NAMES:
            continue
        if name in known_function_names:
            calls.append(name)
    return sorted(set(calls))


def collect_dataset_usage(body: str) -> tuple[list[str], list[str]]:
    clean_body = _strip_comments(body)
    pattern = re.compile(r"\b(ds_[A-Za-z0-9_]+)\s*\.\s*([A-Za-z_]\w*)", re.IGNORECASE)
    reads: set[str] = set()
    writes: set[str] = set()

    for match in pattern.finditer(clean_body):
        dataset_name = match.group(1)
        method = match.group(2).lower()
        if method in DATASET_WRITE_METHODS:
            writes.add(dataset_name)
        if method in DATASET_READ_METHODS or method not in DATASET_WRITE_METHODS:
            reads.add(dataset_name)

    return sorted(reads), sorted(writes)


def collect_component_usage(body: str, component_ids: set[str]) -> list[str]:
    clean_body = _strip_comments(body)
    used = []
    for component_id in component_ids:
        if re.search(rf"\b{re.escape(component_id)}\s*\.", clean_body):
            used.append(component_id)
    return sorted(set(used))


def collect_platform_calls(body: str) -> list[str]:
    lowered = _strip_comments(body).lower()
    return [hint for hint in PLATFORM_HINTS if hint in lowered]


def extract_string_literals(text: str) -> list[str]:
    return [match.group(2) for match in re.finditer(r'(["\'])(.*?)\1', text, re.DOTALL)]
