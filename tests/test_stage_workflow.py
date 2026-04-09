import json
from pathlib import Path

from am_bridge.config import load_cli_config
from am_bridge.stages import (
    build_conversion_package,
    build_conversion_plan,
    build_review_template,
    build_starter_bundle,
)


CONFIG_PATH = Path("am-bridge.config.json")
FORM_XML = Path(
    "samples/ScoreRanking_Proj-master/src/main/resources/egovframework/conf/scoreranking/DefApp/Win32/form.xml"
)


def test_stage1_package_resolves_primary_dataset_and_backend_chains() -> None:
    config = load_cli_config(CONFIG_PATH)

    package = build_conversion_package(FORM_XML, backend_roots=config.backendRoots)
    traces = {trace.transactionId: trace for trace in package.backendTraces}

    assert package.page.primaryDatasetId == "ds_scorechk"
    assert package.page.mainGridComponentId == "Grid0"
    assert package.page.primaryTransactionIds == ["TX-BUTTON0ONCLICK-1"]

    score_trace = traces["TX-BUTTON0ONCLICK-1"]
    assert score_trace.controllerClass == "EgovSampleController"
    assert score_trace.controllerMethod == "selectScoreList"
    assert score_trace.serviceImplClass == "EgovSampleServiceImpl"
    assert score_trace.serviceMethod == "ScoreChk"
    assert score_trace.daoClass == "SampleDAO"
    assert score_trace.daoMethod == "ScoreChk"
    assert score_trace.sqlMapId == "sampleDAO.ScoreChk"
    assert Path(score_trace.sqlMapFile).name == "EgovSample_Sample_SQL.xml"
    assert {"score_jew", "student_jew"} <= set(score_trace.tableCandidates)
    assert {"stuno", "stuname", "avgscore", "rank", "denseRank"} <= set(
        score_trace.responseFieldCandidates
    )

    lookup_trace = traces["TX-TESTNAMESELECT-1"]
    assert lookup_trace.controllerMethod == "selectTestList"
    assert lookup_trace.requestDtoType == "SampleDefaultVO"
    assert lookup_trace.serviceMethod == "testNameList"
    assert lookup_trace.daoClass == "SampleDAO"
    assert lookup_trace.daoMethod == "testNameList"
    assert lookup_trace.sqlMapId == "sampleDAO.testNameList"
    assert lookup_trace.tableCandidates == ["score_jew"]
    assert lookup_trace.responseFieldCandidates == ["testCategory", "testname"]


def test_review_overrides_flow_into_stage2_and_stage3_outputs(tmp_path: Path) -> None:
    config = load_cli_config(CONFIG_PATH)

    base_package = build_conversion_package(FORM_XML, backend_roots=config.backendRoots)
    review = build_review_template(base_package)
    review["primaryDatasetId"] = "ds_testCategory"
    review["secondaryDatasetIds"] = ["ds_scorechk", "ds_screen"]
    review["primaryTransactionIds"] = ["TX-TESTNAMESELECT-1"]
    review["interactionPattern"] = "lookup-bootstrap-page"
    review["backendTraces"]["TX-TESTNAMESELECT-1"]["sqlMapId"] = "manual.testNameList"

    review_path = tmp_path / "form-review.json"
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")

    reviewed_package = build_conversion_package(
        FORM_XML,
        backend_roots=config.backendRoots,
        review_path=review_path,
    )
    plan = build_conversion_plan(reviewed_package)
    bundle = build_starter_bundle(reviewed_package, plan)

    assert reviewed_package.page.primaryDatasetId == "ds_testCategory"
    assert reviewed_package.page.primaryTransactionIds == ["TX-TESTNAMESELECT-1"]
    assert reviewed_package.page.interactionPattern == "lookup-bootstrap-page"

    reviewed_trace = next(
        trace for trace in reviewed_package.backendTraces if trace.transactionId == "TX-TESTNAMESELECT-1"
    )
    assert reviewed_trace.sqlMapId == "manual.testNameList"
    assert "testNameList.do" in plan.aiPrompts["backend"]

    mapper_file = next(file for file in bundle.backendFiles if file.path.endswith("Mapper.xml"))
    assert "manual.testNameList" in mapper_file.content
