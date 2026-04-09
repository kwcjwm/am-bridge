from __future__ import annotations

from typing import Protocol

from am_bridge.models import PageModel
from am_bridge.source import PageSource


class Analyzer(Protocol):
    def analyze(self, source: PageSource, model: PageModel) -> None:
        ...

