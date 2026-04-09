from __future__ import annotations

from collections import defaultdict

from am_bridge.models import PageModel


class PlatformDependencyAnalyzer:
    def analyze(self, source, model: PageModel) -> None:
        function_lookup = {function.functionName: function for function in model.functions}
        event_sources_by_function: defaultdict[str, list[str]] = defaultdict(list)
        for event in model.events:
            if event.handlerFunction:
                event_sources_by_function[event.handlerFunction].append(event.sourceComponentId)

        shared_usage: set[str] = set(model.platform.sharedComponentUsage)

        for function_name, function in function_lookup.items():
            if not function.platformCalls:
                continue
            shared_usage.update(function.platformCalls)
            source_components = event_sources_by_function.get(function_name, [])
            for component in model.components:
                if component.componentId in source_components:
                    merged = set(component.platformDependency)
                    merged.update(function.platformCalls)
                    component.platformDependency = sorted(merged)

        for component in model.components:
            text = str(component.properties.get("Text", "")).lower()
            component_id = component.componentId.lower()
            inferred: list[str] = []
            if "approval" in text or "결재" in text or "approval" in component_id:
                inferred.append("approval")
            if "mail" in text or "메일" in text or "mail" in component_id:
                inferred.append("mail")
            if "auth" in text or "인증" in text or "auth" in component_id:
                inferred.append("auth")
            if "권한" in text or "permission" in component_id:
                inferred.append("permission")

            if inferred:
                merged = set(component.platformDependency)
                merged.update(inferred)
                component.platformDependency = sorted(merged)
                shared_usage.update(inferred)

        model.platform.sharedComponentUsage = sorted(shared_usage)
        model.platform.approvalRequired = "approval" in shared_usage
        model.platform.mailIntegration = "mail" in shared_usage
        if ("permission" in shared_usage or "auth" in shared_usage) and not model.platform.permissionKey:
            model.platform.permissionKey = f"PAGE:{model.pageId}"
        if shared_usage and not model.platform.menuKey:
            model.platform.menuKey = f"MENU:{model.pageId}"
