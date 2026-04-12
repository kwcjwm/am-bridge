from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path


DEFAULT_CONFIG_NAME = "am-bridge.config.json"
DEFAULT_LOCAL_CONFIG_NAME = "am-bridge.config.local.json"


@dataclass
class CliConfig:
    sourceRoots: list[Path] = field(default_factory=list)
    backendRoots: list[Path] = field(default_factory=list)
    analysisRoot: Path = Path("artifacts/analysis")
    pageSpecRoot: Path = Path("artifacts/target")
    packageRoot: Path = Path("artifacts/packages")
    planRoot: Path = Path("artifacts/plans")
    starterRoot: Path = Path("artifacts/starter")
    reportRoot: Path = Path("artifacts/reports")
    reviewRoot: Path = Path("artifacts/reviews")
    configPath: Path | None = None


@dataclass
class StageArtifactPaths:
    analysisJson: Path
    pageSpec: Path
    packageJson: Path
    packageReport: Path
    analysisReport: Path
    planJson: Path
    planReport: Path
    vueConfigJson: Path
    pmChecklist: Path
    starterDir: Path
    reportDir: Path
    stage1ReportDir: Path
    stage2ReportDir: Path
    reviewJson: Path


def load_cli_config(config_path: str | Path | None = None, cwd: Path | None = None) -> CliConfig:
    working_dir = (cwd or Path.cwd()).resolve()
    base_config_path, local_config_path = _find_config_paths(config_path, working_dir)
    base_raw = _load_config_json(base_config_path)
    local_raw = _load_config_json(local_config_path)

    if base_config_path is None and local_config_path is None:
        return CliConfig()

    return CliConfig(
        sourceRoots=_resolve_path_list("sourceRoots", base_raw, base_config_path, local_raw, local_config_path),
        backendRoots=_resolve_path_list("backendRoots", base_raw, base_config_path, local_raw, local_config_path),
        analysisRoot=_resolve_scalar_path(
            "analysisRoot",
            "artifacts/analysis",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        pageSpecRoot=_resolve_scalar_path(
            "pageSpecRoot",
            "artifacts/target",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        packageRoot=_resolve_scalar_path(
            "packageRoot",
            "artifacts/packages",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        planRoot=_resolve_scalar_path(
            "planRoot",
            "artifacts/plans",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        starterRoot=_resolve_scalar_path(
            "starterRoot",
            "artifacts/starter",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        reportRoot=_resolve_scalar_path(
            "reportRoot",
            "artifacts/reports",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        reviewRoot=_resolve_scalar_path(
            "reviewRoot",
            "artifacts/reviews",
            base_raw,
            base_config_path,
            local_raw,
            local_config_path,
        ),
        configPath=local_config_path or base_config_path,
    )


def resolve_input_path(input_value: str, config: CliConfig, cwd: Path | None = None) -> Path:
    working_dir = (cwd or Path.cwd()).resolve()
    direct_candidates = _build_input_candidates(input_value, working_dir)
    for candidate in direct_candidates:
        if candidate.exists():
            return candidate.resolve()

    matches: list[Path] = []
    for root in config.sourceRoots:
        for candidate in _build_root_candidates(input_value, root):
            if candidate.exists():
                matches.append(candidate.resolve())

    unique_matches = sorted(set(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if len(unique_matches) > 1:
        match_list = ", ".join(str(item) for item in unique_matches)
        raise ValueError(f"입력 파일 후보가 여러 개입니다: {match_list}")

    raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_value}")


def derive_default_output_paths(input_path: Path, config: CliConfig) -> tuple[Path, Path]:
    paths = derive_stage_artifact_paths(input_path, config)
    return paths.analysisJson, paths.pageSpec


def derive_stage_artifact_paths(input_path: Path, config: CliConfig) -> StageArtifactPaths:
    resolved_input = input_path.resolve()
    source_root = _find_best_source_root(resolved_input, config.sourceRoots)

    if source_root is None:
        relative_path = Path(resolved_input.name)
    else:
        relative_path = resolved_input.relative_to(source_root)

    relative_stem = relative_path.with_suffix("")
    analysis_json = (config.analysisRoot / relative_path).with_suffix(".json")
    page_spec = config.pageSpecRoot / relative_path.with_name(f"{relative_stem.name}-spec.md")
    package_json = config.packageRoot / relative_path.with_name(f"{relative_stem.name}-package.json")
    package_report = config.packageRoot / relative_path.with_name(f"{relative_stem.name}-package.md")
    analysis_report = config.packageRoot / relative_path.with_name(f"{relative_stem.name}-analysis.md")
    plan_json = config.planRoot / relative_path.with_name(f"{relative_stem.name}-plan.json")
    plan_report = config.planRoot / relative_path.with_name(f"{relative_stem.name}-plan.md")
    vue_config_json = config.planRoot / relative_path.with_name(f"{relative_stem.name}-vue-config.json")
    pm_checklist = config.planRoot / relative_path.with_name(f"{relative_stem.name}-pm-checklist.md")
    starter_dir = config.starterRoot / relative_stem
    report_dir = config.reportRoot / relative_stem
    stage1_report_dir = report_dir / "stage1"
    stage2_report_dir = report_dir / "stage2"
    review_json = config.reviewRoot / relative_path.with_name(f"{relative_stem.name}-review.json")

    return StageArtifactPaths(
        analysisJson=analysis_json,
        pageSpec=page_spec,
        packageJson=package_json,
        packageReport=package_report,
        analysisReport=analysis_report,
        planJson=plan_json,
        planReport=plan_report,
        vueConfigJson=vue_config_json,
        pmChecklist=pm_checklist,
        starterDir=starter_dir,
        reportDir=report_dir,
        stage1ReportDir=stage1_report_dir,
        stage2ReportDir=stage2_report_dir,
        reviewJson=review_json,
    )


def _find_config_paths(
    config_path: str | Path | None,
    working_dir: Path,
) -> tuple[Path | None, Path | None]:
    if config_path:
        requested_path = Path(config_path)
        resolved_requested = (
            requested_path.resolve()
            if requested_path.is_absolute()
            else (working_dir / requested_path).resolve()
        )
        if resolved_requested.name == DEFAULT_LOCAL_CONFIG_NAME:
            return None, resolved_requested if resolved_requested.exists() else None
        sibling_local = resolved_requested.with_name(DEFAULT_LOCAL_CONFIG_NAME)
        return (
            resolved_requested if resolved_requested.exists() else None,
            sibling_local if sibling_local.exists() else None,
        )

    for candidate_dir in (working_dir, *working_dir.parents):
        base_candidate = candidate_dir / DEFAULT_CONFIG_NAME
        local_candidate = candidate_dir / DEFAULT_LOCAL_CONFIG_NAME
        if base_candidate.exists():
            return base_candidate.resolve(), local_candidate.resolve() if local_candidate.exists() else None
        if local_candidate.exists():
            return None, local_candidate.resolve()

    package_default = _package_root() / DEFAULT_CONFIG_NAME
    package_local = _package_root() / DEFAULT_LOCAL_CONFIG_NAME
    if package_default.exists():
        return package_default.resolve(), package_local.resolve() if package_local.exists() else None
    if package_local.exists():
        return None, package_local.resolve()

    return None, None


def _package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_config_path(path: Path, base_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


def _load_config_json(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path_list(
    key: str,
    base_raw: dict[str, object],
    base_path: Path | None,
    local_raw: dict[str, object],
    local_path: Path | None,
) -> list[Path]:
    values, source_path = _pick_config_value(key, [], base_raw, base_path, local_raw, local_path)
    base_dir = source_path.parent if source_path is not None else Path.cwd()
    return [_resolve_config_path(Path(str(item)), base_dir) for item in values]


def _resolve_scalar_path(
    key: str,
    default: str,
    base_raw: dict[str, object],
    base_path: Path | None,
    local_raw: dict[str, object],
    local_path: Path | None,
) -> Path:
    value, source_path = _pick_config_value(key, default, base_raw, base_path, local_raw, local_path)
    base_dir = source_path.parent if source_path is not None else Path.cwd()
    return _resolve_config_path(Path(str(value)), base_dir)


def _pick_config_value(
    key: str,
    default: object,
    base_raw: dict[str, object],
    base_path: Path | None,
    local_raw: dict[str, object],
    local_path: Path | None,
) -> tuple[object, Path | None]:
    if key in local_raw:
        return local_raw[key], local_path
    if key in base_raw:
        return base_raw[key], base_path
    return default, local_path or base_path


def _build_input_candidates(input_value: str, working_dir: Path) -> list[Path]:
    raw_path = Path(input_value)
    candidates = [raw_path]
    if raw_path.suffix == "":
        candidates.append(raw_path.with_suffix(".xml"))

    resolved: list[Path] = []
    for candidate in candidates:
        if candidate.is_absolute():
            resolved.append(candidate)
        else:
            resolved.append((working_dir / candidate).resolve())
    return resolved


def _build_root_candidates(input_value: str, root: Path) -> list[Path]:
    requested = Path(input_value)
    names_to_try = [requested]
    if requested.suffix == "":
        names_to_try.append(requested.with_suffix(".xml"))

    candidates: list[Path] = []
    seen: set[Path] = set()

    for name in names_to_try:
        direct = (root / name).resolve()
        if direct not in seen:
            candidates.append(direct)
            seen.add(direct)

        if len(name.parts) == 1:
            for match in root.rglob(name.name):
                resolved_match = match.resolve()
                if resolved_match not in seen:
                    candidates.append(resolved_match)
                    seen.add(resolved_match)

    return candidates


def _find_best_source_root(input_path: Path, source_roots: list[Path]) -> Path | None:
    matched_roots = []
    for root in source_roots:
        try:
            input_path.relative_to(root)
            matched_roots.append(root)
        except ValueError:
            continue

    if not matched_roots:
        return None
    return max(matched_roots, key=lambda item: len(item.parts))
