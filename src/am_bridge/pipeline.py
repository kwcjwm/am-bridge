from __future__ import annotations

from pathlib import Path

from am_bridge.analyzers import (
    AlarmEventAnalyzer,
    BindingAnalyzer,
    ChartAnalyzer,
    ComponentTreeAnalyzer,
    CommandActionAnalyzer,
    DatasetAnalyzer,
    EventFunctionAnalyzer,
    GridAnalyzer,
    ImageVisionAnalyzer,
    MessageAnalyzer,
    NavigationAnalyzer,
    PlatformDependencyAnalyzer,
    RealtimeAnalyzer,
    ReviewWorkflowAnalyzer,
    ShellAnalyzer,
    StateRuleAnalyzer,
    StyleAnalyzer,
    TransactionAnalyzer,
    ValidationRuleAnalyzer,
)
from am_bridge.models import PageModel
from am_bridge.source import load_page_source


def analyze_file(path: str | Path) -> PageModel:
    source = load_page_source(path)
    model = PageModel()

    analyzers = [
        ShellAnalyzer(),
        ComponentTreeAnalyzer(),
        DatasetAnalyzer(),
        BindingAnalyzer(),
        EventFunctionAnalyzer(),
        TransactionAnalyzer(),
        GridAnalyzer(),
        NavigationAnalyzer(),
        PlatformDependencyAnalyzer(),
        RealtimeAnalyzer(),
        ChartAnalyzer(),
        ImageVisionAnalyzer(),
        AlarmEventAnalyzer(),
        CommandActionAnalyzer(),
        ReviewWorkflowAnalyzer(),
        StyleAnalyzer(),
        StateRuleAnalyzer(),
        ValidationRuleAnalyzer(),
        MessageAnalyzer(),
    ]

    for analyzer in analyzers:
        analyzer.analyze(source, model)

    return model
