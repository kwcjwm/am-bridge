from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path


DEFAULT_CONFIG_NAME = "am-bridge.config.json"


@dataclass
class CliConfig:
    sourceRoots: list[Path] = field(default_factory=list)
    analysisRoot: Path = Path("artifacts/analysis")
    pageSpecRoot: Path = Path("artifacts/target")
    configPath: Path | None = None


def load_cli_config(config_path: str | Path | None = None, cwd: Path | None = None) -> CliConfig:
    working_dir = (cwd or Path.cwd()).resolve()
    resolved_path = _find_config_path(config_path, working_dir)

    if resolved_path is None or not resolved_path.exists():
        return CliConfig()

    raw = json.loads(resolved_path.read_text(encoding="utf-8"))
    base_dir = resolved_path.parent
    return CliConfig(
        sourceRoots=[
            _resolve_config_path(Path(item), base_dir) for item in raw.get("sourceRoots", [])
        ],
        analysisRoot=_resolve_config_path(
            Path(raw.get("analysisRoot", "artifacts/analysis")),
            base_dir,
        ),
        pageSpecRoot=_resolve_config_path(
            Path(raw.get("pageSpecRoot", "artifacts/target")),
            base_dir,
        ),
        configPath=resolved_path,
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
    resolved_input = input_path.resolve()
    source_root = _find_best_source_root(resolved_input, config.sourceRoots)

    if source_root is None:
        relative_path = Path(resolved_input.name)
    else:
        relative_path = resolved_input.relative_to(source_root)

    json_path = (config.analysisRoot / relative_path).with_suffix(".json")
    page_spec_name = relative_path.with_name(f"{relative_path.stem}-spec.md")
    page_spec_path = config.pageSpecRoot / page_spec_name
    return json_path, page_spec_path


def _find_config_path(config_path: str | Path | None, working_dir: Path) -> Path | None:
    if config_path:
        requested_path = Path(config_path)
        if requested_path.is_absolute():
            return requested_path.resolve()
        return (working_dir / requested_path).resolve()

    for candidate_dir in (working_dir, *working_dir.parents):
        candidate = candidate_dir / DEFAULT_CONFIG_NAME
        if candidate.exists():
            return candidate.resolve()

    package_default = _package_root() / DEFAULT_CONFIG_NAME
    if package_default.exists():
        return package_default.resolve()

    return None


def _package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_config_path(path: Path, base_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


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
