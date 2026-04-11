from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from am_bridge.config import derive_stage_artifact_paths, load_cli_config, resolve_input_path
from am_bridge.generators import generate_page_conversion_spec
from am_bridge.pipeline import analyze_file
from am_bridge.report_hubs import build_page_report_hub
from am_bridge.report_artifacts import build_stage1_report_sidecars, build_stage2_report_sidecars
from am_bridge.stages import (
    build_conversion_package,
    build_conversion_plan,
    build_review_template,
    build_starter_bundle,
    build_vue_page_config,
    generate_analysis_report,
    generate_plan_prompt_pack,
    generate_plan_registries,
    generate_package_report,
    generate_stage1_registries,
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
    stage1_registries = generate_stage1_registries(package)
    stage1_registry_dir = paths.stage1ReportDir / "registries"

    _write_text(paths.analysisJson, model.to_json())
    _write_text(paths.pageSpec, generate_page_conversion_spec(model))
    _write_text(paths.packageJson, package.to_json())
    _write_registry_files(stage1_registry_dir, stage1_registries)
    _write_text(
        paths.packageReport,
        generate_package_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.packageReport.parent),
            artifact_links={
                "package-json": _relative_path(paths.packageJson, paths.packageReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.packageReport.parent),
                "page-spec": _relative_path(paths.pageSpec, paths.packageReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.packageReport.parent),
                "stage1 report pack": _relative_path(paths.stage1ReportDir / "README.md", paths.packageReport.parent),
            },
        ),
    )
    _write_text(
        paths.analysisReport,
        generate_analysis_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.analysisReport.parent),
            artifact_links={
                "package-json": _relative_path(paths.packageJson, paths.analysisReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.analysisReport.parent),
                "page-spec": _relative_path(paths.pageSpec, paths.analysisReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.analysisReport.parent),
                "stage1 report pack": _relative_path(paths.stage1ReportDir / "README.md", paths.analysisReport.parent),
            },
        ),
    )
    _write_sidecars(paths.stage1ReportDir, build_stage1_report_sidecars(package))
    _write_json(paths.reviewJson, build_review_template(package))
    _write_sidecars(
        paths.reportDir,
        build_page_report_hub(
            package,
            {
                "page_spec": _relative_path(paths.pageSpec, paths.reportDir),
                "package_json": _relative_path(paths.packageJson, paths.reportDir),
                "package_report": _relative_path(paths.packageReport, paths.reportDir),
                "analysis_report": _relative_path(paths.analysisReport, paths.reportDir),
                "review_json": _relative_path(paths.reviewJson, paths.reportDir),
            },
            {"stage1"},
        ),
    )

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
    stage1_registries = generate_stage1_registries(package)
    stage1_registry_dir = paths.stage1ReportDir / "registries"
    stage2_registries = generate_plan_registries(plan, package)
    stage2_registry_dir = paths.stage2ReportDir / "registries"
    prompt_pack_path = paths.stage2ReportDir / "ai-prompts.md"

    _write_text(paths.packageJson, package.to_json())
    _write_registry_files(stage1_registry_dir, stage1_registries)
    _write_text(
        paths.packageReport,
        generate_package_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.packageReport.parent),
            artifact_links={
                "package-json": _relative_path(paths.packageJson, paths.packageReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.packageReport.parent),
                "page-spec": _relative_path(paths.pageSpec, paths.packageReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.packageReport.parent),
                "stage1 report pack": _relative_path(paths.stage1ReportDir / "README.md", paths.packageReport.parent),
            },
        ),
    )
    _write_text(
        paths.analysisReport,
        generate_analysis_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.analysisReport.parent),
            artifact_links={
                "package-json": _relative_path(paths.packageJson, paths.analysisReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.analysisReport.parent),
                "page-spec": _relative_path(paths.pageSpec, paths.analysisReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.analysisReport.parent),
                "stage1 report pack": _relative_path(paths.stage1ReportDir / "README.md", paths.analysisReport.parent),
            },
        ),
    )
    _write_json(paths.reviewJson, build_review_template(package), overwrite=False)
    _write_text(paths.planJson, plan.to_json())
    _write_registry_files(stage2_registry_dir, stage2_registries)
    _write_text(prompt_pack_path, generate_plan_prompt_pack(plan))
    _write_text(
        paths.planReport,
        generate_plan_report(
            plan,
            package,
            registry_dir=_relative_path(stage2_registry_dir, paths.planReport.parent),
            prompt_pack_path=_relative_path(prompt_pack_path, paths.planReport.parent),
            artifact_links={
                "plan-json": _relative_path(paths.planJson, paths.planReport.parent),
                "vue-config-json": _relative_path(paths.vueConfigJson, paths.planReport.parent),
                "pm-checklist": _relative_path(paths.pmChecklist, paths.planReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.planReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.planReport.parent),
                "stage2 report pack": _relative_path(paths.stage2ReportDir / "README.md", paths.planReport.parent),
            },
        ),
    )
    _write_text(paths.vueConfigJson, vue_config.to_json())
    _write_text(paths.pmChecklist, pm_checklist)
    _write_sidecars(paths.stage1ReportDir, build_stage1_report_sidecars(package))
    _write_sidecars(paths.stage2ReportDir, build_stage2_report_sidecars(package, plan, vue_config))
    _write_sidecars(
        paths.reportDir,
        build_page_report_hub(
            package,
            {
                "page_spec": _relative_path(paths.pageSpec, paths.reportDir),
                "package_json": _relative_path(paths.packageJson, paths.reportDir),
                "package_report": _relative_path(paths.packageReport, paths.reportDir),
                "analysis_report": _relative_path(paths.analysisReport, paths.reportDir),
                "review_json": _relative_path(paths.reviewJson, paths.reportDir),
                "plan_json": _relative_path(paths.planJson, paths.reportDir),
                "plan_report": _relative_path(paths.planReport, paths.reportDir),
                "vue_config_json": _relative_path(paths.vueConfigJson, paths.reportDir),
                "pm_checklist": _relative_path(paths.pmChecklist, paths.reportDir),
            },
            {"stage1", "stage2"},
        ),
    )

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
    bundle = build_starter_bundle(package, plan, vue_config)
    stage1_registries = generate_stage1_registries(package)
    stage1_registry_dir = paths.stage1ReportDir / "registries"
    stage2_registries = generate_plan_registries(plan, package)
    stage2_registry_dir = paths.stage2ReportDir / "registries"
    prompt_pack_path = paths.stage2ReportDir / "ai-prompts.md"

    for starter_file in [*bundle.frontendFiles, *bundle.backendFiles]:
        _write_text(paths.starterDir / starter_file.path, starter_file.content)
    _write_text(paths.packageJson, package.to_json())
    _write_json(paths.reviewJson, build_review_template(package), overwrite=False)
    _write_registry_files(stage1_registry_dir, stage1_registries)
    _write_registry_files(stage2_registry_dir, stage2_registries)
    _write_text(prompt_pack_path, generate_plan_prompt_pack(plan))
    _write_text(
        paths.packageReport,
        generate_package_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.packageReport.parent),
            artifact_links={
                "package-json": _relative_path(paths.packageJson, paths.packageReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.packageReport.parent),
                "page-spec": _relative_path(paths.pageSpec, paths.packageReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.packageReport.parent),
                "stage1 report pack": _relative_path(paths.stage1ReportDir / "README.md", paths.packageReport.parent),
            },
        ),
    )
    _write_text(
        paths.analysisReport,
        generate_analysis_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.analysisReport.parent),
            artifact_links={
                "package-json": _relative_path(paths.packageJson, paths.analysisReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.analysisReport.parent),
                "page-spec": _relative_path(paths.pageSpec, paths.analysisReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.analysisReport.parent),
                "stage1 report pack": _relative_path(paths.stage1ReportDir / "README.md", paths.analysisReport.parent),
            },
        ),
    )
    _write_text(paths.planJson, plan.to_json())
    _write_text(
        paths.planReport,
        generate_plan_report(
            plan,
            package,
            registry_dir=_relative_path(stage2_registry_dir, paths.planReport.parent),
            prompt_pack_path=_relative_path(prompt_pack_path, paths.planReport.parent),
            artifact_links={
                "plan-json": _relative_path(paths.planJson, paths.planReport.parent),
                "vue-config-json": _relative_path(paths.vueConfigJson, paths.planReport.parent),
                "pm-checklist": _relative_path(paths.pmChecklist, paths.planReport.parent),
                "review-json": _relative_path(paths.reviewJson, paths.planReport.parent),
                "page report hub": _relative_path(paths.reportDir / "README.md", paths.planReport.parent),
                "stage2 report pack": _relative_path(paths.stage2ReportDir / "README.md", paths.planReport.parent),
            },
        ),
    )
    _write_text(paths.vueConfigJson, vue_config.to_json())
    _write_text(paths.pmChecklist, pm_checklist)
    _write_sidecars(paths.stage1ReportDir, build_stage1_report_sidecars(package))
    _write_sidecars(paths.stage2ReportDir, build_stage2_report_sidecars(package, plan, vue_config))
    _write_text(paths.starterDir / "starter-bundle.json", bundle.to_json())
    _write_json(paths.starterDir / "handoff-prompts.json", bundle.handoffPrompts)
    _write_text(paths.starterDir / "vue-page-config.json", vue_config.to_json())
    _write_text(paths.starterDir / "pm-test-checklist.md", pm_checklist)
    _write_sidecars(
        paths.reportDir,
        build_page_report_hub(
            package,
            {
                "page_spec": _relative_path(paths.pageSpec, paths.reportDir),
                "package_json": _relative_path(paths.packageJson, paths.reportDir),
                "package_report": _relative_path(paths.packageReport, paths.reportDir),
                "analysis_report": _relative_path(paths.analysisReport, paths.reportDir),
                "review_json": _relative_path(paths.reviewJson, paths.reportDir),
                "plan_json": _relative_path(paths.planJson, paths.reportDir),
                "plan_report": _relative_path(paths.planReport, paths.reportDir),
                "vue_config_json": _relative_path(paths.vueConfigJson, paths.reportDir),
                "pm_checklist": _relative_path(paths.pmChecklist, paths.reportDir),
                "starter_dir": _relative_path(paths.starterDir, paths.reportDir),
                "starter_bundle": _relative_path(paths.starterDir / "starter-bundle.json", paths.reportDir),
            },
            {"stage1", "stage2", "stage3"},
        ),
    )

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
        "stage1ReportDir": str(paths.stage1ReportDir),
        "stage2ReportDir": str(paths.stage2ReportDir),
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


def _write_registry_files(root: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        _write_text(root / relative_path, content)


def _write_sidecars(root: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        _write_text(root / relative_path, content)


def _relative_path(path: Path, start: Path) -> str:
    return Path(os.path.relpath(path, start)).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
