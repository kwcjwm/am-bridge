from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


REPO_ROOT = Path(__file__).resolve().parents[1]


FILES_TO_COPY = [
    Path("AGENTS.md"),
    Path(".agents/skills/am-page-modernization/SKILL.md"),
    Path(".agents/skills/am-page-modernization/references/stage-procedure.md"),
    Path(".agents/skills/am-page-modernization/references/review-contract.md"),
    Path(".agents/skills/am-page-modernization/references/ai-pro-prompts.md"),
    Path("integrations/ai-pro/README.md"),
    Path("integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md"),
    Path("integrations/ai-pro/bootstrap/bootstrap-prompts.md"),
    Path("integrations/ai-pro/bootstrap/bootstrap-manifest.json"),
    Path("integrations/ai-pro/global/harness-global.md"),
    Path("integrations/ai-pro/project/am-page-modernization.md"),
    Path("integrations/ai-pro/project/operator-prompts.md"),
    Path("integrations/ai-pro/tools/tool-contract.md"),
    Path("integrations/ai-pro/tools/tool-registry.example.json"),
    Path("integrations/ai-pro/tools/tool-registry.single-tool.example.json"),
    Path("scripts/ai_pro_stage_runner.py"),
    Path("am-bridge.config.json"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a ready-to-copy AI Pro harness bundle.")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "artifacts" / "ai-pro-bundle"),
        help="Destination directory for the exported bundle",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_root = Path(args.output).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    for relative_path in FILES_TO_COPY:
        source = REPO_ROOT / relative_path
        target = output_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    _write_resolved_tool_registry(output_root)
    _write_bundle_readme(output_root)
    print(output_root)
    return 0


def _write_resolved_tool_registry(output_root: Path) -> None:
    template_path = REPO_ROOT / "integrations" / "ai-pro" / "tools" / "tool-registry.example.json"
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("<REPO_ROOT>", str(REPO_ROOT).replace("\\", "/"))
    resolved_path = output_root / "integrations" / "ai-pro" / "tools" / "tool-registry.resolved.json"
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(content, encoding="utf-8")


def _write_bundle_readme(output_root: Path) -> None:
    bundle_readme = {
        "repoRoot": str(REPO_ROOT),
        "bundleRoot": str(output_root),
        "globalHarnessSource": str(output_root / "integrations" / "ai-pro" / "global" / "harness-global.md"),
        "projectHarnessSource": str(output_root / "integrations" / "ai-pro" / "project" / "am-page-modernization.md"),
        "toolRegistrySource": str(output_root / "integrations" / "ai-pro" / "tools" / "tool-registry.resolved.json"),
        "runnerScript": str(output_root / "scripts" / "ai_pro_stage_runner.py"),
        "configFile": str(output_root / "am-bridge.config.json"),
    }
    target = output_root / "bundle-manifest.json"
    target.write_text(json.dumps(bundle_readme, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
