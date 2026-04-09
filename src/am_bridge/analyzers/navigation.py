from __future__ import annotations

import re

from am_bridge.models import NavigationModel, PageModel
from am_bridge.script_utils import extract_functions, find_named_calls, split_arguments, unquote
from am_bridge.source import PageSource


class NavigationAnalyzer:
    def analyze(self, source: PageSource, model: PageModel) -> None:
        functions = extract_functions(source.script_text)
        navigation_counter = 0

        for script_function in functions:
            dialog_calls = find_named_calls(script_function.body, "Dialog")
            for args in dialog_calls:
                navigation_counter += 1
                target = unquote(args[0]) if args else ""
                params = [unquote(arg) for arg in args[1:] if arg.strip()]
                model.navigation.append(
                    NavigationModel(
                        navigationId=f"NAV-{navigation_counter:04d}",
                        triggerFunction=script_function.name,
                        navigationType="popup",
                        target=target,
                        parameterBindings=params,
                        returnHandling="callback-or-close",
                    )
                )

            for match in re.finditer(r"\b([A-Za-z_]\w*)\.Url\s*=\s*([^;]+);", script_function.body):
                navigation_counter += 1
                target_expr = match.group(2).strip()
                model.navigation.append(
                    NavigationModel(
                        navigationId=f"NAV-{navigation_counter:04d}",
                        triggerFunction=script_function.name,
                        navigationType="subview",
                        target=unquote(target_expr),
                        parameterBindings=[],
                        returnHandling="none",
                    )
                )

