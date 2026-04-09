from pathlib import Path

from am_bridge.config import (
    derive_default_output_paths,
    derive_stage_artifact_paths,
    load_cli_config,
    resolve_input_path,
)


CONFIG_PATH = Path("am-bridge.config.json")
SAMPLE_ROOT = Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/conf/scoreranking")
BACKEND_ROOTS = [
    Path("samples/ScoreRanking_Proj-master/src/main/java"),
    Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/sqlmap"),
]


def test_cli_config_loads_default_source_root_and_output_roots() -> None:
    config = load_cli_config(CONFIG_PATH)

    assert config.configPath is not None
    assert config.sourceRoots == [SAMPLE_ROOT.resolve()]
    assert config.backendRoots == [item.resolve() for item in BACKEND_ROOTS]
    assert config.analysisRoot == Path("artifacts/analysis").resolve()
    assert config.pageSpecRoot == Path("artifacts/target").resolve()
    assert config.packageRoot == Path("artifacts/packages").resolve()
    assert config.planRoot == Path("artifacts/plans").resolve()
    assert config.starterRoot == Path("artifacts/starter").resolve()
    assert config.reviewRoot == Path("artifacts/reviews").resolve()


def test_cli_config_falls_back_to_repo_default_when_cwd_is_elsewhere() -> None:
    fake_home = Path.home()
    config = load_cli_config(cwd=fake_home)

    assert config.configPath == CONFIG_PATH.resolve()
    assert config.sourceRoots == [SAMPLE_ROOT.resolve()]


def test_cli_can_resolve_filename_only_from_configured_source_root() -> None:
    config = load_cli_config(CONFIG_PATH)

    resolved = resolve_input_path("form.xml", config)
    assert resolved == (SAMPLE_ROOT / "DefApp/Win32/form.xml").resolve()


def test_cli_can_resolve_filename_only_from_home_directory_context() -> None:
    config = load_cli_config(cwd=Path.home())

    resolved = resolve_input_path("form.xml", config, cwd=Path.home())
    assert resolved == (SAMPLE_ROOT / "DefApp/Win32/form.xml").resolve()


def test_cli_can_resolve_relative_path_from_configured_source_root() -> None:
    config = load_cli_config(CONFIG_PATH)

    resolved = resolve_input_path("DefApp/Win32/graph.xml", config)
    assert resolved == (SAMPLE_ROOT / "DefApp/Win32/graph.xml").resolve()


def test_cli_default_output_paths_preserve_source_structure() -> None:
    config = load_cli_config(CONFIG_PATH)
    input_path = (SAMPLE_ROOT / "DefApp/Win32/form.xml").resolve()

    json_path, spec_path = derive_default_output_paths(input_path, config)

    assert json_path == Path("artifacts/analysis/DefApp/Win32/form.json").resolve()
    assert spec_path == Path("artifacts/target/DefApp/Win32/form-spec.md").resolve()


def test_cli_stage_artifact_paths_preserve_stage_structure() -> None:
    config = load_cli_config(CONFIG_PATH)
    input_path = (SAMPLE_ROOT / "DefApp/Win32/form.xml").resolve()

    paths = derive_stage_artifact_paths(input_path, config)

    assert paths.packageJson == Path("artifacts/packages/DefApp/Win32/form-package.json").resolve()
    assert paths.packageReport == Path("artifacts/packages/DefApp/Win32/form-package.md").resolve()
    assert paths.planJson == Path("artifacts/plans/DefApp/Win32/form-plan.json").resolve()
    assert paths.planReport == Path("artifacts/plans/DefApp/Win32/form-plan.md").resolve()
    assert paths.reviewJson == Path("artifacts/reviews/DefApp/Win32/form-review.json").resolve()
    assert paths.starterDir == Path("artifacts/starter/DefApp/Win32/form").resolve()
