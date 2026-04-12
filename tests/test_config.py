from __future__ import annotations

import json
from pathlib import Path

from am_bridge.config import load_cli_config


def test_load_cli_config_prefers_local_override(tmp_path: Path) -> None:
    base = tmp_path / "am-bridge.config.json"
    local = tmp_path / "am-bridge.config.local.json"

    base.write_text(
        json.dumps(
            {
                "sourceRoots": ["samples/base-ui"],
                "backendRoots": ["samples/base-backend"],
                "reportRoot": "artifacts/reports-base",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    local.write_text(
        json.dumps(
            {
                "sourceRoots": ["live-ui"],
                "backendRoots": ["live-backend-a", "live-backend-b"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    config = load_cli_config(cwd=tmp_path)

    assert config.sourceRoots == [(tmp_path / "live-ui").resolve()]
    assert config.backendRoots == [
        (tmp_path / "live-backend-a").resolve(),
        (tmp_path / "live-backend-b").resolve(),
    ]
    assert config.reportRoot == (tmp_path / "artifacts/reports-base").resolve()
    assert config.configPath == local.resolve()


def test_load_cli_config_explicit_base_still_applies_local_override(tmp_path: Path) -> None:
    base = tmp_path / "am-bridge.config.json"
    local = tmp_path / "am-bridge.config.local.json"

    base.write_text(json.dumps({"sourceRoots": ["base-ui"]}, ensure_ascii=False), encoding="utf-8")
    local.write_text(json.dumps({"sourceRoots": ["live-ui"]}, ensure_ascii=False), encoding="utf-8")

    config = load_cli_config(base, cwd=tmp_path)

    assert config.sourceRoots == [(tmp_path / "live-ui").resolve()]
    assert config.configPath == local.resolve()
