from pathlib import Path

from am_bridge.generators import generate_page_conversion_spec
from am_bridge.pipeline import analyze_file


SAMPLE_ROOT = Path("samples/ScoreRanking_Proj-master/src/main/resources/egovframework/conf/scoreranking")
FORM_XML = SAMPLE_ROOT / "DefApp/Win32/form.xml"
GRAPH_XML = SAMPLE_ROOT / "DefApp/Win32/graph.xml"
SCHOLARSHIP_XML = SAMPLE_ROOT / "DefApp/Win32/scholarship.xml"
MAIN_CONFIG_XML = SAMPLE_ROOT / "pjt_mng_ci_main_Win32.xml"


def test_sample_form_xml_can_be_analyzed() -> None:
    model = analyze_file(FORM_XML)

    assert model.pageId == "form"
    assert model.legacy.formId == "form"
    assert len(model.datasets) == 3
    assert len(model.components) == 8
    assert any(item.url.endswith("/miplatform/testScoreChk.do") for item in model.transactions)
    assert any(item.navigationType == "popup" and item.target == "DefApp::scholarship.xml" for item in model.navigation)


def test_sample_form_spec_is_detailed_enough_for_rr_and_pseudocode() -> None:
    model = analyze_file(FORM_XML)
    spec = generate_page_conversion_spec(model)

    assert "## 기존 화면 구조(아스키 와이어프레임)" in spec
    assert "PAGE form (828x408)" in spec
    assert "[ROW 02] 조회 조건 / 액션 영역" in spec
    assert "Grid / ds_scorechk" in spec
    assert "Div / container" in spec
    assert "## 함수 호출 연계" in spec
    assert "[FUNC] Button0_OnClick(obj)" in spec
    assert "<- [EVENT] Button0.OnClick" in spec
    assert "-> [TX] TX-BUTTON0ONCLICK-1 / http://127.0.0.1:8080/miplatform/testScoreChk.do" in spec
    assert "[FUNC] fnCmTr(objFrm, svcid, strController, strVoClass, inputDs, outputDs, params, callbackFnc)" in spec
    assert "-> [FUNC] fnSetVoInfo(objFrm, strVoClass)" in spec
    assert "-> [TX] TX-FNCMTR-1 / \"svc::\" + strController" in spec
    assert "-> [NAV] popup / DefApp::scholarship.xml" in spec
    assert "-> [NAV] subview / scurl" in spec
    assert "## 상세 분석" in spec
    assert "## 함수별 슈도코드" in spec
    assert "### Button0_OnClick" in spec
    assert "call transaction TX-BUTTON0ONCLICK-1" in spec
    assert "## R&R 정의" in spec
    assert "### FE 책임" in spec
    assert "### BE 책임" in spec
    assert "### 협의 필요 항목" in spec
    assert "fnCmTr" in spec
    assert "DefApp::scholarship.xml" in spec
    assert "scurl" in spec


def test_sample_graph_xml_uses_file_stem_as_page_id() -> None:
    model = analyze_file(GRAPH_XML)

    assert model.pageId == "graph"
    assert model.legacy.formId == "form"
    assert len(model.datasets) == 1
    assert len(model.components) == 2
    assert any(item.url.endswith("/miplatform/subteacher.do") for item in model.transactions)


def test_sample_scholarship_xml_ignores_commented_alert_calls() -> None:
    model = analyze_file(SCHOLARSHIP_XML)

    assert model.pageId == "scholarship"
    assert len(model.transactions) == 3
    assert len(model.validationRules) == 0
    assert not any(message.messageType == "alert" for message in model.messages)


def test_sample_main_config_xml_is_treated_as_non_page_document() -> None:
    model = analyze_file(MAIN_CONFIG_XML)

    assert model.pageId == "pjt_mng_ci_main_Win32"
    assert model.pageType == "unknown"
    assert len(model.components) == 0
    assert len(model.datasets) == 0
