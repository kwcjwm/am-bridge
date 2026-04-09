from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from am_bridge.config import derive_stage_artifact_paths, load_cli_config, resolve_input_path
from am_bridge.generators import generate_page_conversion_spec
from am_bridge.pipeline import analyze_file
from am_bridge.stages import (
    build_conversion_package,
    build_conversion_plan,
    build_review_template,
    build_starter_bundle,
    build_vue_page_config,
    generate_analysis_report,
    generate_package_report,
    generate_plan_report,
    generate_pm_test_checklist,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Structured AI Pro wrapper for am-bridge staged AM workflow."
    )
    parser.add_argument("stage", choices=["analyze", "stage1", "stage2", "stage3"])
    parser.add_argument("input", help="Legacy XML page path, relative path, or file name")
    parser.add_argument("--config", help="Path to am-bridge.config.json")
    parser.add_argument("--review", help="Optional review override JSON path")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    config = load_cli_config(args.config)
    input_path = resolve_input_path(args.input, config)
    paths = derive_stage_artifact_paths(input_path, config)
    review_path = Path(args.review).resolve() if args.review else paths.reviewJson

    if args.stage == "analyze":
        return _run_analyze(input_path, paths)
    if args.stage == "stage1":
        return _run_stage1(input_path, config, paths, review_path)
    if args.stage == "stage2":
        return _run_stage2(input_path, config, paths, review_path)
    if args.stage == "stage3":
        return _run_stage3(input_path, config, paths, review_path)
    raise ValueError(f"Unsupported stage: {args.stage}")


def _run_analyze(input_path: Path, paths) -> int:
    model = analyze_file(input_path)
    _write_text(paths.analysisJson, model.to_json())
    _write_text(paths.pageSpec, generate_page_conversion_spec(model))

    summary = {
        "stage": "analyze",
        "input": str(input_path),
        "artifacts": {
            "analysisJson": str(paths.analysisJson),
            "pageSpec": str(paths.pageSpec),
        },
        "page": {
            "pageId": model.pageId,
            "pageName": model.pageName,
            "pageType": model.pageType,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _run_stage1(input_path: Path, config, paths, review_path: Path) -> int:
    model = analyze_file(input_path)
    package = build_conversion_package(
        input_path=input_path,
        backend_roots=config.backendRoots,
        source_roots=config.sourceRoots,
        review_path=review_path if review_path.exists() else None,
    )

    _write_text(paths.analysisJson, model.to_json())
    _write_text(paths.pageSpec, generate_page_conversion_spec(model))
    _write_text(paths.packageJson, package.to_json())
    _write_text(paths.packageReport, generate_package_report(package))
    _write_text(paths.analysisReport, generate_analysis_report(package))
    _write_json(paths.reviewJson, build_review_template(package))

    summary = {
        "stage": "stage1",
        "input": str(input_path),
        "artifacts": _artifact_paths(paths),
        "page": {
            "pageId": package.page.pageId,
            "pageName": package.page.pageName,
            "primaryDatasetId": package.page.primaryDatasetId,
            "mainGridComponentId": package.page.mainGridComponentId,
            "primaryTransactionIds": package.page.primaryTransactionIds,
            "interactionPattern": package.page.interactionPattern,
        },
        "backendTraces": [_trace_summary(trace) for trace in package.backendTraces],
        "relatedPages": [
            {
                "navigationType": item.navigationType,
                "target": item.target,
                "resolvedPath": item.resolvedPath,
                "pageId": item.pageId,
                "resolutionStatus": item.resolutionStatus,
            }
            for item in package.relatedPages
        ],
        "openQuestions": package.openQuestions,
        "aiHints": package.aiHints,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _run_stage2(input_path: Path, config, paths, review_path: Path) -> int:
    package = build_conversion_package(
        input_path=input_path,
        backend_roots=config.backendRoots,
        source_roots=config.sourceRoots,
        review_path=review_path if review_path.exists() else None,
    )
    plan = build_conversion_plan(package)
    vue_config = build_vue_page_config(package, plan)
    pm_checklist = generate_pm_test_checklist(package, plan, vue_config)

    _write_text(paths.packageJson, package.to_json())
    _write_text(paths.packageReport, generate_package_report(package))
    _write_text(paths.analysisReport, generate_analysis_report(package))
    _write_json(paths.reviewJson, build_review_template(package), overwrite=False)
    _write_text(paths.planJson, plan.to_json())
    _write_text(paths.planReport, generate_plan_report(plan, package))
    _write_text(paths.vueConfigJson, vue_config.to_json())
    _write_text(paths.pmChecklist, pm_checklist)

    summary = {
        "stage": "stage2",
        "input": str(input_path),
        "artifacts": _artifact_paths(paths),
        "page": {
            "pageId": package.page.pageId,
            "primaryDatasetId": package.page.primaryDatasetId,
            "primaryTransactionIds": package.page.primaryTransactionIds,
        },
        "plan": {
            "route": plan.route,
            "vuePageName": plan.vuePageName,
            "interactionPattern": plan.interactionPattern,
            "frontendFiles": [item.path for item in plan.frontendFiles],
            "backendFiles": [item.path for item in plan.backendFiles],
            "verificationChecks": plan.verificationChecks,
        },
        "vueConfig": {
            "path": str(paths.vueConfigJson),
            "primaryDatasetId": vue_config.primaryDatasetId,
            "mainGridComponentId": vue_config.mainGridComponentId,
            "relatedPages": vue_config.relatedPages,
        },
        "pmChecklist": {
            "path": str(paths.pmChecklist),
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _run_stage3(input_path: Path, config, paths, review_path: Path) -> int:
    package = build_conversion_package(
        input_path=input_path,
        backend_roots=config.backendRoots,
        source_roots=config.sourceRoots,
        review_path=review_path if review_path.exists() else None,
    )
    plan = build_conversion_plan(package)
    vue_config = build_vue_page_config(package, plan)
    pm_checklist = generate_pm_test_checklist(package, plan, vue_config)
    bundle = build_starter_bundle(package, plan)

    for starter_file in [*bundle.frontendFiles, *bundle.backendFiles]:
        _write_text(paths.starterDir / starter_file.path, starter_file.content)
    _write_text(paths.planJson, plan.to_json())
    _write_text(paths.planReport, generate_plan_report(plan, package))
    _write_text(paths.vueConfigJson, vue_config.to_json())
    _write_text(paths.pmChecklist, pm_checklist)
    _write_text(paths.starterDir / "starter-bundle.json", bundle.to_json())
    _write_json(paths.starterDir / "handoff-prompts.json", bundle.handoffPrompts)
    _write_text(paths.starterDir / "vue-page-config.json", vue_config.to_json())
    _write_text(paths.starterDir / "pm-test-checklist.md", pm_checklist)

    summary = {
        "stage": "stage3",
        "input": str(input_path),
        "artifacts": _artifact_paths(paths),
        "starter": {
            "starterDir": str(paths.starterDir),
            "frontendFiles": [item.path for item in bundle.frontendFiles],
            "backendFiles": [item.path for item in bundle.backendFiles],
            "handoffPromptsFile": str(paths.starterDir / "handoff-prompts.json"),
            "pmChecklistFile": str(paths.starterDir / "pm-test-checklist.md"),
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _artifact_paths(paths) -> dict[str, str]:
    return {
        "analysisJson": str(paths.analysisJson),
        "pageSpec": str(paths.pageSpec),
        "packageJson": str(paths.packageJson),
        "packageReport": str(paths.packageReport),
        "analysisReport": str(paths.analysisReport),
        "reviewJson": str(paths.reviewJson),
        "planJson": str(paths.planJson),
        "planReport": str(paths.planReport),
        "vueConfigJson": str(paths.vueConfigJson),
        "pmChecklist": str(paths.pmChecklist),
        "starterDir": str(paths.starterDir),
    }


def _trace_summary(trace) -> dict[str, object]:
    return {
        "transactionId": trace.transactionId,
        "controller": ".".join(item for item in [trace.controllerClass, trace.controllerMethod] if item),
        "service": ".".join(item for item in [trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod] if item),
        "dao": ".".join(item for item in [trace.daoClass, trace.daoMethod] if item),
        "sqlMapId": trace.sqlMapId,
        "tables": trace.tableCandidates,
        "responseFields": trace.responseFieldCandidates,
    }


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, data: dict, overwrite: bool = True) -> None:
    if path.exists() and not overwrite:
        return
    _write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
