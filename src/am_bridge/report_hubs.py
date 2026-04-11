from __future__ import annotations

from am_bridge.models import ConversionPlanModel, PageConversionPackage, VuePageConfigModel
from am_bridge.reporting import join_values, markdown_link, render_contents, render_markdown_table


PAGE_ARTIFACT_LABELS: dict[str, tuple[str, str]] = {
    "page_spec": ("페이지 스펙", "Page spec"),
    "package_json": ("Stage 1 패키지 JSON", "Stage 1 package JSON"),
    "package_report": ("Stage 1 패키지 보고서", "Stage 1 package report"),
    "analysis_report": ("상세 레거시 분석 보고서", "Detailed legacy analysis report"),
    "review_json": ("리뷰 보정 파일", "Review override file"),
    "plan_json": ("Stage 2 계획 JSON", "Stage 2 plan JSON"),
    "plan_report": ("Stage 2 계획 보고서", "Stage 2 plan report"),
    "vue_config_json": ("Vue 계약 JSON", "Vue contract JSON"),
    "pm_checklist": ("PM 테스트 체크리스트", "PM test checklist"),
    "starter_dir": ("Starter 디렉토리", "Starter directory"),
    "starter_bundle": ("Starter 번들 메타파일", "Starter bundle metadata"),
}


def build_page_report_hub(
    package: PageConversionPackage,
    artifact_links: dict[str, str],
    available_stages: set[str],
) -> dict[str, str]:
    return {
        "README.md": _render_page_hub(package, artifact_links, available_stages, "en"),
        "README.en.md": _render_page_hub(package, artifact_links, available_stages, "en"),
        "translate-to-korean.md": _render_translation_guide(package),
    }


def build_stage1_hub_docs(
    package: PageConversionPackage,
    compact_specs: list[tuple[str, str, str]],
) -> dict[str, str]:
    return {
        "README.md": _render_stage1_overview(package, compact_specs, "en"),
        "README.en.md": _render_stage1_overview(package, compact_specs, "en"),
        "sections/datasets.md": _render_stage1_datasets_doc(package, "en"),
        "sections/datasets.en.md": _render_stage1_datasets_doc(package, "en"),
        "sections/components.md": _render_stage1_components_doc(package, "en"),
        "sections/components.en.md": _render_stage1_components_doc(package, "en"),
        "sections/actions.md": _render_stage1_actions_doc(package, "en"),
        "sections/actions.en.md": _render_stage1_actions_doc(package, "en"),
        "sections/backend.md": _render_stage1_backend_doc(package, "en"),
        "sections/backend.en.md": _render_stage1_backend_doc(package, "en"),
        "sections/navigation.md": _render_stage1_navigation_doc(package, "en"),
        "sections/navigation.en.md": _render_stage1_navigation_doc(package, "en"),
        "sections/validation.md": _render_stage1_validation_doc(package, "en"),
        "sections/validation.en.md": _render_stage1_validation_doc(package, "en"),
    }


def build_stage2_hub_docs(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    compact_specs: list[tuple[str, str, str]],
) -> dict[str, str]:
    return {
        "README.md": _render_stage2_overview(package, plan, vue_config, compact_specs, "en"),
        "README.en.md": _render_stage2_overview(package, plan, vue_config, compact_specs, "en"),
        "sections/ui-contract.md": _render_stage2_ui_contract_doc(package, plan, vue_config, "en"),
        "sections/ui-contract.en.md": _render_stage2_ui_contract_doc(package, plan, vue_config, "en"),
        "sections/actions.md": _render_stage2_actions_doc(package, vue_config, "en"),
        "sections/actions.en.md": _render_stage2_actions_doc(package, vue_config, "en"),
        "sections/endpoints.md": _render_stage2_endpoints_doc(package, vue_config, "en"),
        "sections/endpoints.en.md": _render_stage2_endpoints_doc(package, vue_config, "en"),
        "sections/files.md": _render_stage2_files_doc(plan, "en"),
        "sections/files.en.md": _render_stage2_files_doc(plan, "en"),
        "sections/verification.md": _render_stage2_verification_doc(package, plan, vue_config, "en"),
        "sections/verification.en.md": _render_stage2_verification_doc(package, plan, vue_config, "en"),
    }


def _render_translation_guide(package: PageConversionPackage) -> str:
    page = package.page
    lines = [
        f"# Translate Report Pack To Korean - {page.pageId or 'legacy-page'}",
        "",
        "Use this guide after the English report pack has been reviewed.",
        "",
        "## Rules",
        "",
        "- Treat the generated English Markdown as the canonical source of truth.",
        "- Preserve dataset IDs, transaction IDs, endpoint names, and file paths in backticks.",
        "- Translate explanation text, not technical identifiers.",
        "- Do not edit the English originals unless explicitly asked.",
        "- Default to summary-only Korean delivery, not a full mirrored Korean tree.",
        "- Keep detailed links pointed at the English canonical docs unless a Korean counterpart is explicitly required.",
        "",
        "## Default Korean Output Scope",
        "",
        "- `README.ko.md` for the page hub summary",
        "- `stage1/README.ko.md` for the Stage 1 overview summary",
        "- `stage2/README.ko.md` for the Stage 2 overview summary",
        "- Korean summaries of the main narrative reports in `artifacts/packages/` and `artifacts/plans/`",
        "- A Korean PM/operator version of the PM checklist when requested",
        "- Keep section guides, CSV files, registries, and deep technical docs in English by default",
        "",
        "## Suggested Prompt For Internal AI",
        "",
        "```text",
        f"Read the English canonical report set for `{page.pageId or 'legacy-page'}` and produce a Korean delivery version.",
        "Requirements:",
        "1. Keep technical IDs, dataset IDs, transaction IDs, endpoint IDs, and file paths in backticks.",
        "2. Translate only the explanatory text into natural Korean.",
        "3. Translate only the summary-level PM/operator documents unless explicitly asked for a full Korean mirror.",
        "4. Keep links pointed at the English canonical docs unless a Korean counterpart is explicitly required and named in advance.",
        "5. Before writing files, list the exact Korean output files you plan to create and confirm that none of them overwrite the English originals.",
        "6. Separate layout/signoff items from behavior/API/SQL lock items.",
        "7. Call out unresolved risks and manual review points clearly.",
        "8. If file output is needed, create derived files such as `README.ko.md` or `stage2/README.ko.md` without changing the English originals.",
        "```",
        "",
    ]
    return "\n".join(lines)


def _render_page_hub(
    package: PageConversionPackage,
    artifact_links: dict[str, str],
    available_stages: set[str],
    lang: str,
) -> str:
    page = package.page
    reading_order = [
        f"1. {markdown_link(_t(lang, 'Stage 1 전체 안내', 'Stage 1 overview'), 'stage1/README.md')}",
        f"2. {markdown_link(_t(lang, '데이터셋 분석', 'Dataset analysis'), 'stage1/sections/datasets.md')}",
        f"3. {markdown_link(_t(lang, '행동/이벤트 분석', 'Action and event analysis'), 'stage1/sections/actions.md')}",
        f"4. {markdown_link(_t(lang, '백엔드 추적', 'Backend trace'), 'stage1/sections/backend.md')}",
    ]
    if "stage2" in available_stages:
        reading_order.extend(
            [
                f"5. {markdown_link(_t(lang, 'Stage 2 전체 안내', 'Stage 2 overview'), 'stage2/README.md')}",
                f"6. {markdown_link(_t(lang, 'UI 계약', 'UI contract'), 'stage2/sections/ui-contract.md')}",
                f"7. {markdown_link(_t(lang, '엔드포인트 계약', 'Endpoint contract'), 'stage2/sections/endpoints.md')}",
                f"8. {markdown_link(_t(lang, '검증/체크리스트', 'Verification/checklist'), 'stage2/sections/verification.md')}",
            ]
        )
    stage_status = [
        f"- Stage 1: {_t(lang, '생성됨', 'generated')}",
        f"- Stage 2: {_t(lang, '생성됨', 'generated') if 'stage2' in available_stages else _t(lang, '아직 없음', 'not generated yet')}",
        f"- Stage 3: {_t(lang, '생성됨', 'generated') if 'stage3' in available_stages else _t(lang, '아직 없음', 'not generated yet')}",
    ]
    return _render_doc(
        _t(lang, "페이지 종합 보고서", "Page Report Hub") + f" - {page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "한눈에 보기", "At A Glance"),
                [
                    f"- {_t(lang, '페이지명', 'Page name')}: `{page.pageName or 'unknown'}`",
                    f"- {_t(lang, '상호작용 패턴', 'Interaction pattern')}: `{page.interactionPattern or 'unknown'}`",
                    f"- {_t(lang, '주요 데이터셋', 'Primary dataset')}: `{page.primaryDatasetId or 'unknown'}`",
                    f"- {_t(lang, '대표 그리드', 'Main grid')}: `{page.mainGridComponentId or 'unknown'}`",
                    f"- {_t(lang, '주요 트랜잭션', 'Primary transactions')}: `{join_values(page.primaryTransactionIds, 'none')}`",
                ],
            ),
            (_t(lang, "현재 상태", "Current Status"), stage_status),
            (_t(lang, "권장 읽기 순서", "Recommended Reading Order"), reading_order),
            (_t(lang, "바로 가기", "Shortcuts"), _page_shortcuts(lang, available_stages)),
            (_t(lang, "원본 산출물", "Primary Artifacts"), _artifact_lines(artifact_links, lang)),
            (
                _t(lang, "언어 안내", "Language"),
                [
                    f"- {markdown_link(_t(lang, '영문 정본', 'English canonical'), 'README.md')}",
                    f"- {markdown_link(_t(lang, '호환용 영문 미러', 'Compatibility mirror'), 'README.en.md')}",
                    f"- {markdown_link(_t(lang, '한글 변환 가이드', 'Korean translation guide'), 'translate-to-korean.md')}",
                ],
            ),
        ],
    )


def _render_stage1_overview(
    package: PageConversionPackage,
    compact_specs: list[tuple[str, str, str]],
    lang: str,
) -> str:
    page = package.page
    return _render_doc(
        _t(lang, "Stage 1 분석 보고서 안내", "Stage 1 Analysis Guide") + f" - {page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "한눈에 보기", "At A Glance"),
                [
                    f"- {_t(lang, '페이지명', 'Page name')}: `{page.pageName or 'unknown'}`",
                    f"- {_t(lang, '주요 데이터셋', 'Primary dataset')}: `{page.primaryDatasetId or 'unknown'}`",
                    f"- {_t(lang, '대표 그리드', 'Main grid')}: `{page.mainGridComponentId or 'unknown'}`",
                    f"- {_t(lang, '주요 트랜잭션', 'Primary transactions')}: `{join_values(page.primaryTransactionIds, 'none')}`",
                    f"- {_t(lang, '백엔드 추적 수', 'Backend trace count')}: `{len(package.backendTraces)}`",
                    f"- {_t(lang, '관련 화면 수', 'Related screen count')}: `{len(package.relatedPages)}`",
                ],
            ),
            (_t(lang, "읽기 순서", "Reading Order"), _stage1_reading_order(lang)),
            (_t(lang, "카테고리 안내", "Categories"), _stage1_categories(lang)),
            (
                _t(lang, "Compact CSV", "Compact CSV"),
                [f"- {markdown_link(name, name)}: {_t(lang, ko, en)}" for name, ko, en in compact_specs],
            ),
            (
                _t(lang, "한글 변환 워크플로", "Korean Translation Workflow"),
                [f"- {markdown_link('translate-to-korean.md', '../translate-to-korean.md')}"],
            ),
        ],
    )


def _render_stage2_overview(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    compact_specs: list[tuple[str, str, str]],
    lang: str,
) -> str:
    return _render_doc(
        _t(lang, "Stage 2 구현 계약 안내", "Stage 2 Plan Guide") + f" - {plan.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "한눈에 보기", "At A Glance"),
                [
                    f"- {_t(lang, '라우트', 'Route')}: `{plan.route or 'unknown'}`",
                    f"- {_t(lang, 'Vue 페이지명', 'Vue page name')}: `{plan.vuePageName or 'unknown'}`",
                    f"- {_t(lang, '주요 데이터셋', 'Primary dataset')}: `{package.page.primaryDatasetId or 'unknown'}`",
                    f"- {_t(lang, '검색 컨트롤 수', 'Search control count')}: `{len(vue_config.searchControls)}`",
                    f"- {_t(lang, '행동 수', 'Action count')}: `{len(vue_config.actions)}`",
                    f"- {_t(lang, '엔드포인트 수', 'Endpoint count')}: `{len(vue_config.endpoints)}`",
                ],
            ),
            (_t(lang, "읽기 순서", "Reading Order"), _stage2_reading_order(lang)),
            (_t(lang, "카테고리 안내", "Categories"), _stage2_categories(lang)),
            (
                _t(lang, "Compact CSV", "Compact CSV"),
                [f"- {markdown_link(name, name)}: {_t(lang, ko, en)}" for name, ko, en in compact_specs],
            ),
            (
                _t(lang, "추가 자료", "Additional Material"),
                [f"- {markdown_link('ai-prompts.md', 'ai-prompts.md')}"],
            ),
        ],
    )


def _render_doc(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]
    lines.extend(render_contents([section_title for section_title, _body in sections]))
    for section_title, body in sections:
        lines.append(f"## {section_title}")
        lines.append("")
        lines.extend(body or ["- None"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _artifact_lines(artifact_links: dict[str, str], lang: str) -> list[str]:
    lines: list[str] = []
    for key, target in artifact_links.items():
        ko_label, en_label = PAGE_ARTIFACT_LABELS.get(key, (key, key))
        lines.append(f"- {markdown_link(_t(lang, ko_label, en_label), target)}")
    return lines or ["- None"]


def _page_shortcuts(lang: str, available_stages: set[str]) -> list[str]:
    lines = [
        f"- {_t(lang, '데이터셋', 'Datasets')}: {markdown_link('stage1/sections/datasets.md', 'stage1/sections/datasets.md')}",
        f"- {_t(lang, '컴포넌트', 'Components')}: {markdown_link('stage1/sections/components.md', 'stage1/sections/components.md')}",
        f"- {_t(lang, '행동/이벤트', 'Actions and events')}: {markdown_link('stage1/sections/actions.md', 'stage1/sections/actions.md')}",
        f"- {_t(lang, '백엔드', 'Backend')}: {markdown_link('stage1/sections/backend.md', 'stage1/sections/backend.md')}",
    ]
    if "stage2" in available_stages:
        lines.extend(
            [
                f"- {_t(lang, 'UI 계약', 'UI contract')}: {markdown_link('stage2/sections/ui-contract.md', 'stage2/sections/ui-contract.md')}",
                f"- {_t(lang, '엔드포인트 계약', 'Endpoint contract')}: {markdown_link('stage2/sections/endpoints.md', 'stage2/sections/endpoints.md')}",
                f"- {_t(lang, '검증', 'Verification')}: {markdown_link('stage2/sections/verification.md', 'stage2/sections/verification.md')}",
            ]
        )
    return lines


def _stage1_reading_order(lang: str) -> list[str]:
    return [
        f"1. {markdown_link(_t(lang, '데이터셋 분석', 'Dataset analysis'), 'sections/datasets.md')}",
        f"2. {markdown_link(_t(lang, '백엔드 추적', 'Backend trace'), 'sections/backend.md')}",
        f"3. {markdown_link(_t(lang, '행동/이벤트', 'Actions and events'), 'sections/actions.md')}",
        f"4. {markdown_link(_t(lang, '관련 화면', 'Related screens'), 'sections/navigation.md')}",
    ]


def _stage2_reading_order(lang: str) -> list[str]:
    return [
        f"1. {markdown_link(_t(lang, 'UI 계약', 'UI contract'), 'sections/ui-contract.md')}",
        f"2. {markdown_link(_t(lang, '행동 계약', 'Action contract'), 'sections/actions.md')}",
        f"3. {markdown_link(_t(lang, '엔드포인트 계약', 'Endpoint contract'), 'sections/endpoints.md')}",
        f"4. {markdown_link(_t(lang, '파일 청사진', 'File blueprints'), 'sections/files.md')}",
        f"5. {markdown_link(_t(lang, '검증과 체크리스트', 'Verification and checklist'), 'sections/verification.md')}",
    ]


def _stage1_categories(lang: str) -> list[str]:
    return [
        f"- {markdown_link(_t(lang, '데이터셋 분석', 'Dataset analysis'), 'sections/datasets.md')}",
        f"- {markdown_link(_t(lang, '컴포넌트와 배치', 'Components and layout'), 'sections/components.md')}",
        f"- {markdown_link(_t(lang, '행동과 이벤트', 'Actions and events'), 'sections/actions.md')}",
        f"- {markdown_link(_t(lang, '백엔드 추적', 'Backend trace'), 'sections/backend.md')}",
        f"- {markdown_link(_t(lang, '관련 화면', 'Related screens'), 'sections/navigation.md')}",
        f"- {markdown_link(_t(lang, '검증과 메시지', 'Validation and messages'), 'sections/validation.md')}",
    ]


def _stage2_categories(lang: str) -> list[str]:
    return [
        f"- {markdown_link(_t(lang, 'UI 계약', 'UI contract'), 'sections/ui-contract.md')}",
        f"- {markdown_link(_t(lang, '행동 계약', 'Action contract'), 'sections/actions.md')}",
        f"- {markdown_link(_t(lang, '엔드포인트 계약', 'Endpoint contract'), 'sections/endpoints.md')}",
        f"- {markdown_link(_t(lang, '파일 청사진', 'File blueprints'), 'sections/files.md')}",
        f"- {markdown_link(_t(lang, '검증과 체크리스트', 'Verification and checklist'), 'sections/verification.md')}",
    ]


def _t(lang: str, ko: str, en: str) -> str:
    return ko if lang == "ko" else en


def _mark_primary(value: str, is_primary: bool) -> str:
    return f"{value} [PRIMARY]" if is_primary else value


def _join_pair(first: str, second: str) -> str:
    parts = [item for item in [first, second] if item]
    return ".".join(parts) if parts else "unknown"


def _render_stage1_datasets_doc(package: PageConversionPackage, lang: str) -> str:
    page = package.page
    rows = [
        {
            "dataset": _mark_primary(dataset.datasetId, dataset.datasetId == page.primaryDatasetId),
            "role": dataset.role or "unknown",
            "usage": dataset.primaryUsage or "unknown",
            "components": join_values(dataset.boundComponents, "none"),
            "columns": str(len(dataset.columns)),
            "salience": str(dataset.salienceScore),
        }
        for dataset in sorted(page.datasets, key=lambda item: (-item.salienceScore, item.datasetId))
    ]
    return _render_doc(
        _t(lang, "Stage 1 데이터셋 분석", "Stage 1 Dataset Analysis") + f" - {page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "주요 ds가 무엇인지, 검색/코드/결과 ds가 구분되는지 확인한다.", "Check the main dataset and whether search/code/result datasets are properly separated."),
                    _t(lang, "컬럼 상세나 바인딩은 아래 링크로 내려가서 확인한다.", "Use the links below for column and binding detail."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('datasets.csv', '../datasets.csv')}",
                    f"- {markdown_link('dataset-columns.csv', '../registries/dataset-columns.csv')}",
                    f"- {markdown_link('bindings.csv', '../registries/bindings.csv')}",
                    f"- {markdown_link(_t(lang, '컴포넌트 문서', 'Component guide'), 'components.md')}",
                ],
            ),
            (
                _t(lang, "데이터셋 요약", "Dataset Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "Dataset", "Dataset"), "dataset"),
                        (_t(lang, "역할", "Role"), "role"),
                        (_t(lang, "주요 사용", "Usage"), "usage"),
                        (_t(lang, "바인딩 컴포넌트", "Bound components"), "components"),
                        (_t(lang, "컬럼 수", "Columns"), "columns"),
                        (_t(lang, "중요도", "Salience"), "salience"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage1_components_doc(package: PageConversionPackage, lang: str) -> str:
    page = package.page
    rows = [
        {
            "component": component.componentId,
            "type": component.componentType,
            "group": component.layoutGroup or "unknown",
            "parent": component.parentId or "root",
            "events": join_values(component.events, "none"),
            "platform": join_values(component.platformDependency, "none"),
        }
        for component in page.components
    ]
    return _render_doc(
        _t(lang, "Stage 1 컴포넌트와 배치", "Stage 1 Components And Layout") + f" - {page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "버튼, 입력, 그리드가 어떤 그룹에 놓였는지 확인한다.", "Review where buttons, inputs, and grids are placed."),
                    _t(lang, "UI Shell First 논의가 필요하면 이 문서를 먼저 본다.", "Start here when discussing UI Shell First layout signoff."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('components.csv', '../components.csv')}",
                    f"- {markdown_link('bindings.csv', '../registries/bindings.csv')}",
                    f"- {markdown_link('grid-columns.csv', '../registries/grid-columns.csv')}",
                ],
            ),
            (
                _t(lang, "컴포넌트 요약", "Component Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "컴포넌트", "Component"), "component"),
                        (_t(lang, "유형", "Type"), "type"),
                        (_t(lang, "그룹", "Group"), "group"),
                        (_t(lang, "부모", "Parent"), "parent"),
                        (_t(lang, "이벤트", "Events"), "events"),
                        (_t(lang, "플랫폼 의존", "Platform dependency"), "platform"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage1_actions_doc(package: PageConversionPackage, lang: str) -> str:
    page = package.page
    rows = [
        {
            "handler": function.functionName,
            "transactions": join_values(function.callsTransactions, "none"),
            "reads": join_values(function.readsDatasets, "none"),
            "writes": join_values(function.writesDatasets, "none"),
            "controls": join_values(function.controlsComponents, "none"),
            "calls": join_values(function.callsFunctions, "none"),
        }
        for function in page.functions
        if function.functionType == "event-handler"
    ]
    return _render_doc(
        _t(lang, "Stage 1 행동과 이벤트", "Stage 1 Actions And Events") + f" - {page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "버튼 클릭이나 onload가 어떤 ds와 transaction을 건드리는지 확인한다.", "Review which datasets and transactions are touched by clicks and onload handlers."),
                    _t(lang, "기능 흐름이 맞지 않으면 Stage 2 action contract도 틀어질 수 있다.", "If the flow is wrong here, the Stage 2 action contract will drift too."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('user-actions.csv', '../user-actions.csv')}",
                    f"- {markdown_link('functions.csv', '../registries/functions.csv')}",
                    f"- {markdown_link('events.csv', '../registries/events.csv')}",
                    f"- {markdown_link('transactions.csv', '../registries/transactions.csv')}",
                ],
            ),
            (
                _t(lang, "핸들러 요약", "Handler Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "핸들러", "Handler"), "handler"),
                        (_t(lang, "트랜잭션", "Transactions"), "transactions"),
                        (_t(lang, "읽기 ds", "Reads"), "reads"),
                        (_t(lang, "쓰기 ds", "Writes"), "writes"),
                        (_t(lang, "제어 컴포넌트", "Controls"), "controls"),
                        (_t(lang, "호출 함수", "Calls"), "calls"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage1_backend_doc(package: PageConversionPackage, lang: str) -> str:
    rows = [
        {
            "transaction": trace.transactionId,
            "url": trace.url or "unknown",
            "controller": _join_pair(trace.controllerClass, trace.controllerMethod),
            "service": _join_pair(trace.serviceImplClass or trace.serviceInterface, trace.serviceMethod),
            "dao": _join_pair(trace.daoClass, trace.daoMethod),
            "sql": trace.sqlMapId or "unknown",
            "tables": join_values(trace.tableCandidates, "none"),
        }
        for trace in package.backendTraces
    ]
    return _render_doc(
        _t(lang, "Stage 1 백엔드 추적", "Stage 1 Backend Trace") + f" - {package.page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "transaction이 실제로 어느 controller/service/dao/sqlMap으로 이어지는지 본다.", "Trace where each transaction leads in controller/service/DAO/sqlMap terms."),
                    _t(lang, "DB/API 계약 고정 전에는 datasets 문서와 같이 본다.", "Read this together with the dataset guide before locking DB/API contracts."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('backend-traces.csv', '../backend-traces.csv')}",
                    f"- {markdown_link('transactions.csv', '../registries/transactions.csv')}",
                ],
            ),
            (
                _t(lang, "백엔드 추적 요약", "Backend Trace Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "트랜잭션", "Transaction"), "transaction"),
                        (_t(lang, "URL", "URL"), "url"),
                        (_t(lang, "컨트롤러", "Controller"), "controller"),
                        (_t(lang, "서비스", "Service"), "service"),
                        (_t(lang, "DAO", "DAO"), "dao"),
                        (_t(lang, "SQL Map", "SQL Map"), "sql"),
                        (_t(lang, "테이블", "Tables"), "tables"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage1_navigation_doc(package: PageConversionPackage, lang: str) -> str:
    rows = [
        {
            "type": related.navigationType or "unknown",
            "trigger": related.triggerFunction or "unknown",
            "target": related.target or related.navigationId,
            "page": related.pageId or related.pageName or "unresolved",
            "status": related.resolutionStatus or "unknown",
        }
        for related in package.relatedPages
    ]
    return _render_doc(
        _t(lang, "Stage 1 관련 화면", "Stage 1 Related Screens") + f" - {package.page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "팝업, 서브뷰, 화면 이동처럼 현재 화면 밖으로 나가는 흐름을 정리한다.", "Review flows that leave the current page, including popups, subviews, and screen navigation."),
                    _t(lang, "unresolved 대상은 현재 화면 안으로 섞지 말지 먼저 결정해야 한다.", "Resolve whether unresolved targets should stay as separate screens before merging them into the current page."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('related-pages.csv', '../related-pages.csv')}",
                    f"- {markdown_link('navigation.csv', '../registries/navigation.csv')}",
                ],
            ),
            (
                _t(lang, "관련 화면 요약", "Related Screen Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "유형", "Type"), "type"),
                        (_t(lang, "트리거", "Trigger"), "trigger"),
                        (_t(lang, "대상", "Target"), "target"),
                        (_t(lang, "해석 결과", "Resolved page"), "page"),
                        (_t(lang, "상태", "Status"), "status"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage1_validation_doc(package: PageConversionPackage, lang: str) -> str:
    rows = [
        {
            "rule": rule.ruleId,
            "field": rule.targetField or "unknown",
            "type": rule.validationType or "unknown",
            "timing": rule.triggerTiming or "unknown",
            "source": rule.sourceFunction or "unknown",
            "message": rule.message or rule.expression or "unknown",
        }
        for rule in package.page.validationRules
    ]
    return _render_doc(
        _t(lang, "Stage 1 검증과 메시지", "Stage 1 Validation And Messages") + f" - {package.page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "validation, 상태 제어, 사용자 메시지 근거를 점검한다.", "Review validation, state rules, and user-facing message evidence."),
                    _t(lang, "예외 메시지나 disabled 제어가 중요한 화면이면 actions 문서와 함께 본다.", "Read this with the action guide when error messaging or disabled-state control matters."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('validation-rules.csv', '../validation-rules.csv')}",
                    f"- {markdown_link('validation-rules.csv', '../registries/validation-rules.csv')}",
                    f"- {markdown_link('state-rules.csv', '../registries/state-rules.csv')}",
                    f"- {markdown_link('messages.csv', '../registries/messages.csv')}",
                ],
            ),
            (
                _t(lang, "검증 규칙 요약", "Validation Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "규칙", "Rule"), "rule"),
                        (_t(lang, "대상 필드", "Field"), "field"),
                        (_t(lang, "유형", "Type"), "type"),
                        (_t(lang, "시점", "Timing"), "timing"),
                        (_t(lang, "소스", "Source"), "source"),
                        (_t(lang, "메시지", "Message"), "message"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage2_ui_contract_doc(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    lang: str,
) -> str:
    search_rows = [
        {
            "component": item.get("componentId", ""),
            "label": item.get("label", "") or item.get("componentId", ""),
            "dataset": item.get("datasetId", "") or "none",
            "field": item.get("requestFieldCandidate", "") or item.get("boundColumn", "") or "none",
            "role": item.get("controlRole", "") or "unknown",
        }
        for item in vue_config.searchControls
    ]
    grid_rows = [
        {
            "grid": item.get("componentId", ""),
            "dataset": item.get("datasetId", "") or "unknown",
            "layout": item.get("layoutGroup", "") or "unknown",
            "columns": str(len(item.get("bodyColumns", []))),
            "headers": join_values(item.get("headerTexts", []), "none"),
        }
        for item in vue_config.grids
    ]
    return _render_doc(
        _t(lang, "Stage 2 UI 계약", "Stage 2 UI Contract") + f" - {plan.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "Vue 전환 후 화면 껍데기와 데이터 바인딩 계약을 확인한다.", "Review the post-conversion page shell and binding contract."),
                    _t(lang, "고객이 보는 검색영역, 버튼, 그리드 배치 합의는 여기서 본다.", "Use this to review customer-facing search, button, and grid placement."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('search-controls.csv', '../search-controls.csv')}",
                    f"- {markdown_link('grids.csv', '../grids.csv')}",
                    f"- {markdown_link('grid-columns.csv', '../grid-columns.csv')}",
                ],
            ),
            (
                _t(lang, "검색/명령 컨트롤", "Search / Command Controls"),
                render_markdown_table(
                    [
                        (_t(lang, "컴포넌트", "Component"), "component"),
                        (_t(lang, "라벨", "Label"), "label"),
                        (_t(lang, "데이터셋", "Dataset"), "dataset"),
                        (_t(lang, "요청 필드", "Request field"), "field"),
                        (_t(lang, "역할", "Role"), "role"),
                    ],
                    search_rows,
                ),
            ),
            (
                _t(lang, "그리드 계약", "Grid Contract"),
                render_markdown_table(
                    [
                        (_t(lang, "그리드", "Grid"), "grid"),
                        (_t(lang, "데이터셋", "Dataset"), "dataset"),
                        (_t(lang, "레이아웃", "Layout"), "layout"),
                        (_t(lang, "컬럼 수", "Columns"), "columns"),
                        (_t(lang, "헤더", "Headers"), "headers"),
                    ],
                    grid_rows,
                ),
            ),
        ],
    )


def _render_stage2_actions_doc(
    package: PageConversionPackage,
    vue_config: VuePageConfigModel,
    lang: str,
) -> str:
    rows = [
        {
            "function": item.get("functionName", ""),
            "kind": item.get("actionKind", "") or "unknown",
            "source": item.get("sourceComponentLabel", "") or item.get("sourceComponentId", "") or "unknown",
            "transactions": join_values(item.get("transactions", []), "none"),
            "reads": join_values(item.get("readsDatasets", []), "none"),
            "writes": join_values(item.get("writesDatasets", []), "none"),
            "navigation": join_values(
                [nav.get("pageId") or nav.get("target") or "unresolved" for nav in item.get("navigationTargets", [])],
                "none",
            ),
        }
        for item in vue_config.actions
    ]
    return _render_doc(
        _t(lang, "Stage 2 행동 계약", "Stage 2 Action Contract") + f" - {package.page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "버튼/이벤트가 어떤 transaction, dataset, 연관 화면과 연결되는지 확인한다.", "Review which buttons or events connect to transactions, datasets, and related screens."),
                    _t(lang, "Stage 1 흐름이 Stage 2 계약으로 어떻게 굳었는지 보는 문서다.", "This shows how the Stage 1 flow became the Stage 2 contract."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('actions.csv', '../actions.csv')}",
                    f"- {markdown_link('related-pages.csv', '../related-pages.csv')}",
                ],
            ),
            (
                _t(lang, "Action 요약", "Action Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "함수", "Function"), "function"),
                        (_t(lang, "종류", "Kind"), "kind"),
                        (_t(lang, "소스", "Source"), "source"),
                        (_t(lang, "트랜잭션", "Transactions"), "transactions"),
                        (_t(lang, "읽기 ds", "Reads"), "reads"),
                        (_t(lang, "쓰기 ds", "Writes"), "writes"),
                        (_t(lang, "연관 화면", "Navigation"), "navigation"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage2_endpoints_doc(
    package: PageConversionPackage,
    vue_config: VuePageConfigModel,
    lang: str,
) -> str:
    rows = [
        {
            "transaction": item.get("transactionId", ""),
            "url": item.get("url", "") or "unknown",
            "inputs": join_values(item.get("inputDatasets", []), "none"),
            "outputs": join_values(item.get("outputDatasets", []), "none"),
            "controller": item.get("controller", "") or "unknown",
            "service": item.get("service", "") or "unknown",
            "dao": item.get("dao", "") or "unknown",
            "sql": item.get("sqlMapId", "") or "unknown",
        }
        for item in vue_config.endpoints
    ]
    return _render_doc(
        _t(lang, "Stage 2 엔드포인트 계약", "Stage 2 Endpoint Contract") + f" - {package.page.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "입출력 데이터셋과 backend chain을 함께 확인한다.", "Review input/output datasets together with the backend chain."),
                    _t(lang, "MyBatis 전환 전후 비교 포인트는 이 문서가 기준이 된다.", "Use this as the reference for pre/post MyBatis conversion comparison."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('endpoints.csv', '../endpoints.csv')}",
                    f"- {markdown_link('related-pages.csv', '../related-pages.csv')}",
                ],
            ),
            (
                _t(lang, "엔드포인트 요약", "Endpoint Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "트랜잭션", "Transaction"), "transaction"),
                        (_t(lang, "URL", "URL"), "url"),
                        (_t(lang, "입력 ds", "Input datasets"), "inputs"),
                        (_t(lang, "출력 ds", "Output datasets"), "outputs"),
                        (_t(lang, "컨트롤러", "Controller"), "controller"),
                        (_t(lang, "서비스", "Service"), "service"),
                        (_t(lang, "DAO", "DAO"), "dao"),
                        (_t(lang, "SQL Map", "SQL Map"), "sql"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage2_files_doc(plan: ConversionPlanModel, lang: str) -> str:
    rows = [
        {"kind": "frontend", "path": file.path, "purpose": file.purpose, "summary": file.summary}
        for file in plan.frontendFiles
    ] + [
        {"kind": "backend", "path": file.path, "purpose": file.purpose, "summary": file.summary}
        for file in plan.backendFiles
    ]
    return _render_doc(
        _t(lang, "Stage 2 파일 청사진", "Stage 2 File Blueprints") + f" - {plan.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "프론트/백엔드 파일이 왜 필요한지와 역할을 설명한다.", "Explain which frontend/backend files are planned and why."),
                    _t(lang, "R&R 조정이 생겨도 최소 파일 구분 기준은 여기서 확인한다.", "Use this as the minimum file split reference even if responsibilities shift later."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('file-blueprints.csv', '../file-blueprints.csv')}",
                    f"- {markdown_link('file-blueprints.csv', '../registries/file-blueprints.csv')}",
                ],
            ),
            (
                _t(lang, "파일 청사진 요약", "File Blueprint Summary"),
                render_markdown_table(
                    [
                        (_t(lang, "구분", "Kind"), "kind"),
                        (_t(lang, "경로", "Path"), "path"),
                        (_t(lang, "목적", "Purpose"), "purpose"),
                        (_t(lang, "설명", "Summary"), "summary"),
                    ],
                    rows,
                ),
            ),
        ],
    )


def _render_stage2_verification_doc(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel,
    lang: str,
) -> str:
    verification_rows = [{"check": item} for item in plan.verificationChecks]
    pm_rows = [
        {
            "item": _t(lang, "주요 데이터셋/그리드 확인", "Confirm the primary dataset/grid"),
            "detail": f"`{package.page.primaryDatasetId or 'unknown'}` / `{package.page.mainGridComponentId or 'unknown'}`",
        },
        {
            "item": _t(lang, "주요 트랜잭션 확인", "Confirm the primary transactions"),
            "detail": join_values(package.page.primaryTransactionIds, "none"),
        },
        {
            "item": _t(lang, "엔드포인트/행동 수 확인", "Confirm endpoint/action counts"),
            "detail": f"endpoint={len(vue_config.endpoints)}, action={len(vue_config.actions)}",
        },
    ]
    return _render_doc(
        _t(lang, "Stage 2 검증과 체크리스트", "Stage 2 Verification And Checklist") + f" - {plan.pageId or 'legacy-page'}",
        [
            (
                _t(lang, "이 문서가 하는 일", "What This Document Does"),
                [
                    _t(lang, "Stage 2 잠금 이후 무엇을 검증해야 하는지 정리한다.", "Explain what must be verified after Stage 2 decisions are locked."),
                    _t(lang, "PM 체크리스트와 내부 검증 포인트를 같이 보여준다.", "Show the PM checklist focus together with internal verification points."),
                ],
            ),
            (
                _t(lang, "빠른 링크", "Quick Links"),
                [
                    f"- {markdown_link('verification-checks.csv', '../registries/verification-checks.csv')}",
                    f"- {markdown_link('execution-steps.csv', '../registries/execution-steps.csv')}",
                    f"- {markdown_link('ai-prompts.md', '../ai-prompts.md')}",
                ],
            ),
            (
                _t(lang, "검증 항목", "Verification Checks"),
                render_markdown_table([(_t(lang, "체크 항목", "Check"), "check")], verification_rows),
            ),
            (
                _t(lang, "PM 확인 포인트", "PM Review Focus"),
                render_markdown_table(
                    [(_t(lang, "항목", "Item"), "item"), (_t(lang, "상세", "Detail"), "detail")],
                    pm_rows,
                ),
            ),
            (
                _t(lang, "미해결 항목", "Open Questions"),
                [f"- {item}" for item in package.openQuestions] or ["- None"],
            ),
        ],
    )
