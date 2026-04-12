from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


REPO_ROOT = Path(__file__).resolve().parents[1]


FILES_TO_COPY = [
    (Path("deploy/internal-ai/AGENTS.md"), Path("AGENTS.md")),
    (Path("deploy/internal-ai/README.md"), Path("README.md")),
    (Path("deploy/internal-ai/bootstrap-initial-prompt.md"), Path("bootstrap-initial-prompt.md")),
    (Path("deploy/internal-ai/no-admin-runtime-prompt.md"), Path("no-admin-runtime-prompt.md")),
    (Path("deploy/internal-ai/operator-script.md"), Path("operator-script.md")),
    (Path("deploy/internal-ai/bundle-version.json"), Path("bundle-version.json")),
    (Path("deploy/internal-ai/update-journal.md"), Path("update-journal.md")),
    (Path("deploy/internal-ai/update-playbook.md"), Path("update-playbook.md")),
    (
        Path("deploy/internal-ai/am-bridge.config.local.example.json"),
        Path("am-bridge.config.local.example.json"),
    ),
    (Path(".agents/skills/am-page-modernization/SKILL.md"), Path(".agents/skills/am-page-modernization/SKILL.md")),
    (
        Path(".agents/skills/am-page-modernization/references/stage-procedure.md"),
        Path(".agents/skills/am-page-modernization/references/stage-procedure.md"),
    ),
    (
        Path(".agents/skills/am-page-modernization/references/review-contract.md"),
        Path(".agents/skills/am-page-modernization/references/review-contract.md"),
    ),
    (
        Path(".agents/skills/am-page-modernization/references/ai-pro-prompts.md"),
        Path(".agents/skills/am-page-modernization/references/ai-pro-prompts.md"),
    ),
    (Path("integrations/ai-pro/README.md"), Path("integrations/ai-pro/README.md")),
    (
        Path("integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md"),
        Path("integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md"),
    ),
    (
        Path("integrations/ai-pro/bootstrap/bootstrap-prompts.md"),
        Path("integrations/ai-pro/bootstrap/bootstrap-prompts.md"),
    ),
    (
        Path("integrations/ai-pro/bootstrap/bootstrap-manifest.json"),
        Path("integrations/ai-pro/bootstrap/bootstrap-manifest.json"),
    ),
    (
        Path("integrations/ai-pro/global/harness-global.md"),
        Path("integrations/ai-pro/global/harness-global.md"),
    ),
    (
        Path("integrations/ai-pro/project/am-page-modernization.md"),
        Path("integrations/ai-pro/project/am-page-modernization.md"),
    ),
    (
        Path("integrations/ai-pro/project/operator-prompts.md"),
        Path("integrations/ai-pro/project/operator-prompts.md"),
    ),
    (
        Path("integrations/ai-pro/tools/tool-contract.md"),
        Path("integrations/ai-pro/tools/tool-contract.md"),
    ),
    (
        Path("integrations/ai-pro/tools/tool-registry.example.json"),
        Path("integrations/ai-pro/tools/tool-registry.example.json"),
    ),
    (
        Path("integrations/ai-pro/tools/tool-registry.single-tool.example.json"),
        Path("integrations/ai-pro/tools/tool-registry.single-tool.example.json"),
    ),
    (Path("scripts/ai_pro_stage_runner.py"), Path("scripts/ai_pro_stage_runner.py")),
    (Path("scripts/am_stage.ps1"), Path("scripts/am_stage.ps1")),
    (Path("am-bridge.config.json"), Path("am-bridge.config.json")),
]

DIRS_TO_COPY = [
    (Path("deploy/internal-ai/prompts"), Path("prompts")),
    (Path("src/am_bridge"), Path("src/am_bridge")),
    (
        Path("samples/ScoreRanking_Proj-master/src/main/java"),
        Path("samples/ScoreRanking_Proj-master/src/main/java"),
    ),
    (
        Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/conf/scoreranking"),
        Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/conf/scoreranking"),
    ),
    (
        Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/sqlmap"),
        Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/sqlmap"),
    ),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export the internal single-model AI workspace.")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "exports" / "internal-ai-workspace"),
        help="Destination directory for the exported internal workspace",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_root = Path(args.output).resolve()
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for source_relative_path, target_relative_path in FILES_TO_COPY:
        source = REPO_ROOT / source_relative_path
        target = output_root / target_relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    for source_relative_path, target_relative_path in DIRS_TO_COPY:
        source = REPO_ROOT / source_relative_path
        target = output_root / target_relative_path
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )

    _write_resolved_tool_registry(output_root)
    _write_bundle_readme(output_root)
    print(output_root)
    return 0


def _write_resolved_tool_registry(output_root: Path) -> None:
    registry_dir = output_root / "integrations" / "ai-pro" / "tools"
    registry_dir.mkdir(parents=True, exist_ok=True)
    replacements = {"<REPO_ROOT>": "."}

    templates = {
        "tool-registry.example.json": "tool-registry.resolved.json",
        "tool-registry.single-tool.example.json": "tool-registry.single-tool.resolved.json",
    }

    for source_name, target_name in templates.items():
        template_path = REPO_ROOT / "integrations" / "ai-pro" / "tools" / source_name
        content = template_path.read_text(encoding="utf-8")
        for key, value in replacements.items():
            content = content.replace(key, value)
        (registry_dir / target_name).write_text(content, encoding="utf-8")


def _write_bundle_readme(output_root: Path) -> None:
    bundle_readme = {
        "bundleType": "internal-ai-workspace",
        "bundleRoot": ".",
        "entryDocument": "AGENTS.md",
        "operatorScript": "operator-script.md",
        "bootstrapPrompt": "bootstrap-initial-prompt.md",
        "noAdminRuntimePrompt": "no-admin-runtime-prompt.md",
        "bundleVersionFile": "bundle-version.json",
        "updateJournal": "update-journal.md",
        "updatePlaybook": "update-playbook.md",
        "globalHarnessSource": "integrations/ai-pro/global/harness-global.md",
        "projectHarnessSource": "integrations/ai-pro/project/am-page-modernization.md",
        "toolRegistrySource": "integrations/ai-pro/tools/tool-registry.resolved.json",
        "runnerScript": "scripts/ai_pro_stage_runner.py",
        "configFile": "am-bridge.config.json",
        "configLocalExample": "am-bridge.config.local.example.json",
        "sampleValidationPage": (
            "samples/ScoreRanking_Proj-master/src/main/resources/"
            "egovframework/conf/scoreranking/DefApp/Win32/form.xml"
        ),
    }
    target = output_root / "bundle-manifest.json"
    target.write_text(json.dumps(bundle_readme, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
