from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from am_bridge.config import (
    derive_default_output_paths,
    derive_stage_artifact_paths,
    load_cli_config,
    resolve_input_path,
)
from am_bridge.generators import generate_page_conversion_spec
from am_bridge.pipeline import analyze_file
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


KNOWN_SUBCOMMANDS = {"analyze", "stage1", "stage2", "stage3"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AM Bridge staged workflow for legacy page modernization.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a legacy XML page file.")
    _add_common_input_args(analyze_parser)
    analyze_parser.add_argument("-o", "--output", help="Optional output path for JSON result")
    analyze_parser.add_argument(
        "--page-spec-output",
        help="Optional output path for generated page conversion spec markdown",
    )

    stage1_parser = subparsers.add_parser("stage1", help="Build the stage 1 conversion package.")
    _add_common_input_args(stage1_parser)
    stage1_parser.add_argument("--review", help="Optional review override JSON path")
    stage1_parser.add_argument("--review-output", help="Optional path for review template JSON")
    stage1_parser.add_argument("--package-output", help="Optional path for package JSON")
    stage1_parser.add_argument("--package-report-output", help="Optional path for package markdown report")

    stage2_parser = subparsers.add_parser("stage2", help="Build the stage 2 conversion plan.")
    _add_common_input_args(stage2_parser)
    stage2_parser.add_argument("--review", help="Optional review override JSON path")
    stage2_parser.add_argument("--plan-output", help="Optional path for plan JSON")
    stage2_parser.add_argument("--plan-report-output", help="Optional path for plan markdown report")

    stage3_parser = subparsers.add_parser("stage3", help="Build the stage 3 starter bundle.")
    _add_common_input_args(stage3_parser)
    stage3_parser.add_argument("--review", help="Optional review override JSON path")
    stage3_parser.add_argument("--starter-dir", help="Optional starter bundle directory")

    return parser


def main() -> int:
    parser = build_parser()
    argv = _normalize_argv(sys.argv[1:])
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _run_analyze(args)
    if args.command == "stage1":
        return _run_stage1(args)
    if args.command == "stage2":
        return _run_stage2(args)
    if args.command == "stage3":
        return _run_stage3(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


def _run_analyze(args: argparse.Namespace) -> int:
    config = load_cli_config(args.config)
    input_path = resolve_input_path(args.input, config)
    default_json_path, default_spec_path = derive_default_output_paths(input_path, config)

    model = analyze_file(input_path)
    output_text = model.to_json()

    json_output_path = Path(args.output).resolve() if args.output else (
        default_json_path if config.configPath is not None else None
    )
    page_spec_output_path = Path(args.page_spec_output).resolve() if args.page_spec_output else (
        default_spec_path if config.configPath is not None else None
    )

    if json_output_path is not None:
        _write_text(json_output_path, output_text)
        print(f"JSON saved to: {json_output_path}")
    else:
        print(output_text)

    if page_spec_output_path is not None:
        _write_text(page_spec_output_path, generate_page_conversion_spec(model))
        print(f"Page spec saved to: {page_spec_output_path}")

    return 0


def _run_stage1(args: argparse.Namespace) -> int:
    config = load_cli_config(args.config)
    input_path = resolve_input_path(args.input, config)
    paths = derive_stage_artifact_paths(input_path, config)
    review_path = Path(args.review).resolve() if args.review else paths.reviewJson

    model = analyze_file(input_path)
    package = build_conversion_package(
        input_path=input_path,
        backend_roots=config.backendRoots,
        source_roots=config.sourceRoots,
        review_path=review_path if review_path.exists() else None,
    )

    package_output = Path(args.package_output).resolve() if args.package_output else paths.packageJson
    package_report_output = (
        Path(args.package_report_output).resolve() if args.package_report_output else paths.packageReport
    )
    review_output = Path(args.review_output).resolve() if args.review_output else paths.reviewJson
    stage1_registries = generate_stage1_registries(package)
    stage1_registry_dir = paths.stage1ReportDir / "registries"
    package_artifact_links = {
        "package-json": _relative_path(package_output, package_report_output.parent),
        "review-json": _relative_path(review_output, package_report_output.parent),
        "page-spec": _relative_path(paths.pageSpec, package_report_output.parent),
    }
    analysis_artifact_links = {
        "package-json": _relative_path(package_output, paths.analysisReport.parent),
        "review-json": _relative_path(review_output, paths.analysisReport.parent),
        "page-spec": _relative_path(paths.pageSpec, paths.analysisReport.parent),
    }

    _write_text(paths.analysisJson, model.to_json())
    _write_text(paths.pageSpec, generate_page_conversion_spec(model))
    _write_text(package_output, package.to_json())
    _write_registry_files(stage1_registry_dir, stage1_registries)
    _write_text(
        package_report_output,
        generate_package_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, package_report_output.parent),
            artifact_links=package_artifact_links,
        ),
    )
    _write_text(
        paths.analysisReport,
        generate_analysis_report(
            package,
            registry_dir=_relative_path(stage1_registry_dir, paths.analysisReport.parent),
            artifact_links=analysis_artifact_links,
        ),
    )
    _write_sidecars(paths.stage1ReportDir, build_stage1_report_sidecars(package))
    if not review_output.exists():
        _write_json(review_output, build_review_template(package))

    print(f"Analysis JSON saved to: {paths.analysisJson}")
    print(f"Page spec saved to: {paths.pageSpec}")
    print(f"Stage 1 package saved to: {package_output}")
    print(f"Stage 1 report saved to: {package_report_output}")
    print(f"Detailed analysis report saved to: {paths.analysisReport}")
    print(f"Stage 1 report tables saved to: {paths.stage1ReportDir}")
    print(f"Review template saved to: {review_output}")
    return 0


def _run_stage2(args: argparse.Namespace) -> int:
    config = load_cli_config(args.config)
    input_path = resolve_input_path(args.input, config)
    paths = derive_stage_artifact_paths(input_path, config)
    review_path = Path(args.review).resolve() if args.review else paths.reviewJson

    package = build_conversion_package(
        input_path=input_path,
        backend_roots=config.backendRoots,
        source_roots=config.sourceRoots,
        review_path=review_path if review_path.exists() else None,
    )
    plan = build_conversion_plan(package)
    vue_config = build_vue_page_config(package, plan)
    pm_checklist = generate_pm_test_checklist(package, plan, vue_config)

    plan_output = Path(args.plan_output).resolve() if args.plan_output else paths.planJson
    plan_report_output = (
        Path(args.plan_report_output).resolve() if args.plan_report_output else paths.planReport
    )
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
            },
        ),
    )
    _write_json(paths.reviewJson, build_review_template(package), overwrite=False)
    _write_text(plan_output, plan.to_json())
    _write_registry_files(stage2_registry_dir, stage2_registries)
    _write_text(prompt_pack_path, generate_plan_prompt_pack(plan))
    _write_text(
        plan_report_output,
        generate_plan_report(
            plan,
            package,
            registry_dir=_relative_path(stage2_registry_dir, plan_report_output.parent),
            prompt_pack_path=_relative_path(prompt_pack_path, plan_report_output.parent),
            artifact_links={
                "plan-json": _relative_path(plan_output, plan_report_output.parent),
                "vue-config-json": _relative_path(paths.vueConfigJson, plan_report_output.parent),
                "pm-checklist": _relative_path(paths.pmChecklist, plan_report_output.parent),
                "review-json": _relative_path(paths.reviewJson, plan_report_output.parent),
            },
        ),
    )
    _write_text(paths.vueConfigJson, vue_config.to_json())
    _write_text(paths.pmChecklist, pm_checklist)
    _write_sidecars(paths.stage1ReportDir, build_stage1_report_sidecars(package))
    _write_sidecars(paths.stage2ReportDir, build_stage2_report_sidecars(package, plan, vue_config))

    print(f"Stage 1 package refreshed at: {paths.packageJson}")
    print(f"Stage 2 plan saved to: {plan_output}")
    print(f"Stage 2 report saved to: {plan_report_output}")
    print(f"Vue page config saved to: {paths.vueConfigJson}")
    print(f"PM test checklist saved to: {paths.pmChecklist}")
    print(f"Stage 1 report tables refreshed at: {paths.stage1ReportDir}")
    print(f"Stage 2 report tables saved to: {paths.stage2ReportDir}")
    return 0


def _run_stage3(args: argparse.Namespace) -> int:
    config = load_cli_config(args.config)
    input_path = resolve_input_path(args.input, config)
    paths = derive_stage_artifact_paths(input_path, config)
    review_path = Path(args.review).resolve() if args.review else paths.reviewJson

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

    starter_dir = Path(args.starter_dir).resolve() if args.starter_dir else paths.starterDir
    for starter_file in [*bundle.frontendFiles, *bundle.backendFiles]:
        _write_text(starter_dir / starter_file.path, starter_file.content)
    _write_text(starter_dir / "starter-bundle.json", bundle.to_json())
    _write_json(starter_dir / "handoff-prompts.json", bundle.handoffPrompts)
    _write_text(paths.packageJson, package.to_json())
    _write_json(paths.reviewJson, build_review_template(package), overwrite=False)
    _write_text(paths.planJson, plan.to_json())
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
            },
        ),
    )
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
            },
        ),
    )
    _write_text(paths.vueConfigJson, vue_config.to_json())
    _write_text(paths.pmChecklist, pm_checklist)
    _write_sidecars(paths.stage1ReportDir, build_stage1_report_sidecars(package))
    _write_sidecars(paths.stage2ReportDir, build_stage2_report_sidecars(package, plan, vue_config))
    _write_text(starter_dir / "vue-page-config.json", vue_config.to_json())
    _write_text(starter_dir / "pm-test-checklist.md", pm_checklist)

    print(f"Starter bundle saved to: {starter_dir}")
    print(f"Stage 2 plan refreshed at: {paths.planJson}")
    print(f"Vue page config saved to: {paths.vueConfigJson}")
    print(f"PM test checklist saved to: {paths.pmChecklist}")
    print(f"Stage 1 report tables refreshed at: {paths.stage1ReportDir}")
    print(f"Stage 2 report tables refreshed at: {paths.stage2ReportDir}")
    return 0


def _add_common_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", help="Path, relative path, or file name of a legacy XML page file")
    parser.add_argument(
        "--config",
        help="Optional CLI config path. Defaults to am-bridge.config.json in the current workspace.",
    )


def _normalize_argv(argv: list[str]) -> list[str]:
    if argv and argv[0] not in KNOWN_SUBCOMMANDS and not argv[0].startswith("-"):
        return ["analyze", *argv]
    return argv


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
