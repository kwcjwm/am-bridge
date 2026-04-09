from __future__ import annotations

from am_bridge.models import (
    ConversionPlanModel,
    DatasetModel,
    PageConversionPackage,
    StarterBundleModel,
    StarterFileModel,
)
from am_bridge.stages.plan_stage import slug


def build_starter_bundle(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
) -> StarterBundleModel:
    page = package.page
    primary_dataset = _find_dataset(page.datasets, page.primaryDatasetId)
    search_dataset = next(
        (dataset for dataset in page.datasets if dataset.primaryUsage == "search-form"),
        None,
    )
    primary_trace = _find_primary_trace(package)
    domain_slug = slug(page.pageId or "legacy-page").replace("-", "")

    frontend_files = [
        StarterFileModel(
            path=f"frontend/src/pages/{slug(page.pageId or plan.pageId)}/{plan.vuePageName}.vue",
            purpose="vue page shell",
            content=_generate_vue_page(page.pageId or plan.pageId, page.pageName, plan.vuePageName),
        ),
        StarterFileModel(
            path=f"frontend/src/composables/use{plan.vuePageName}.ts",
            purpose="page composable",
            content=_generate_composable(
                vue_page_name=plan.vuePageName,
                api_module_slug=slug(page.pageId or "legacy-page"),
                primary_dataset=primary_dataset,
                search_dataset=search_dataset,
            ),
        ),
        StarterFileModel(
            path=f"frontend/src/api/{slug(page.pageId or 'legacy-page')}.ts",
            purpose="typed api client",
            content=_generate_frontend_api(
                vue_page_name=plan.vuePageName,
                page_id=page.pageId or plan.pageId,
                route=plan.route,
            ),
        ),
    ]

    backend_files = [
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/web/{plan.vuePageName}Controller.java",
            purpose="spring controller",
            content=_generate_controller(domain_slug, plan.vuePageName, page.pageId or plan.pageId, primary_trace.url if primary_trace else ""),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/service/{plan.vuePageName}Service.java",
            purpose="service interface",
            content=_generate_service_interface(domain_slug, plan.vuePageName),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/service/impl/{plan.vuePageName}ServiceImpl.java",
            purpose="service implementation",
            content=_generate_service_impl(domain_slug, plan.vuePageName, primary_trace.querySummary if primary_trace else ""),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/dto/{plan.vuePageName}SearchCondition.java",
            purpose="request dto",
            content=_generate_dto(domain_slug, plan.vuePageName, "SearchCondition", search_dataset),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{domain_slug}/dto/{plan.vuePageName}Row.java",
            purpose="response dto",
            content=_generate_dto(domain_slug, plan.vuePageName, "Row", primary_dataset),
        ),
        StarterFileModel(
            path=f"backend/src/main/resources/mapper/{plan.vuePageName}Mapper.xml",
            purpose="query placeholder",
            content=_generate_mapper_xml(plan.vuePageName, primary_trace.sqlMapId if primary_trace else "", primary_trace.querySummary if primary_trace else ""),
        ),
    ]

    return StarterBundleModel(
        pageId=page.pageId,
        frontendFiles=frontend_files,
        backendFiles=backend_files,
        handoffPrompts={
            "stage3-frontend": plan.aiPrompts.get("frontend", ""),
            "stage3-backend": plan.aiPrompts.get("backend", ""),
        },
    )


def _find_dataset(datasets: list[DatasetModel], dataset_id: str) -> DatasetModel | None:
    return next((dataset for dataset in datasets if dataset.datasetId == dataset_id), None)


def _find_primary_trace(package: PageConversionPackage):
    if not package.backendTraces:
        return None
    for transaction_id in package.page.primaryTransactionIds:
        trace = next(
            (item for item in package.backendTraces if item.transactionId == transaction_id),
            None,
        )
        if trace is not None:
            return trace
    return package.backendTraces[0]


def _generate_vue_page(page_id: str, page_name: str, vue_page_name: str) -> str:
    return f"""<template>
  <section class=\"page-shell\">
    <header>
      <h1>{page_name or vue_page_name}</h1>
      <p>Legacy page: {page_id}</p>
    </header>

    <form @submit.prevent=\"actions.search()\">
      <!-- TODO: replace with real search controls -->
      <pre>{{{{ state.searchForm }}}}</pre>
      <button type=\"submit\">Search</button>
    </form>

    <section>
      <!-- TODO: replace with real grid/detail blocks -->
      <pre>{{{{ state.rows }}}}</pre>
    </section>
  </section>
</template>

<script setup lang=\"ts\">
import {{ use{vue_page_name} }} from '../../composables/use{vue_page_name}';

const {{ state, actions }} = use{vue_page_name}();
</script>
"""


def _generate_composable(
    vue_page_name: str,
    api_module_slug: str,
    primary_dataset: DatasetModel | None,
    search_dataset: DatasetModel | None,
) -> str:
    primary_dataset_id = primary_dataset.datasetId if primary_dataset else ""
    search_dataset_id = search_dataset.datasetId if search_dataset else ""
    return f"""import {{ reactive }} from 'vue';
import {{ fetch{vue_page_name}Rows }} from '../api/{api_module_slug}';

export function use{vue_page_name}() {{
  const state = reactive({{
    searchForm: {{}},
    rows: [],
    loading: false,
  }});

  async function search() {{
    state.loading = true;
    try {{
      state.rows = await fetch{vue_page_name}Rows(state.searchForm);
    }} finally {{
      state.loading = false;
    }}
  }}

  return {{
    state,
    actions: {{ search }},
    meta: {{
      primaryDatasetId: '{primary_dataset_id}',
      searchDatasetId: '{search_dataset_id}',
    }},
  }};
}}

export default use{vue_page_name};
"""


def _generate_frontend_api(vue_page_name: str, page_id: str, route: str) -> str:
    api_slug = slug(page_id)
    return f"""export async function fetch{vue_page_name}Rows(searchForm: Record<string, unknown>) {{
  const response = await fetch('/api/{api_slug}/search', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(searchForm),
  }});

  if (!response.ok) {{
    throw new Error('Failed to fetch data for {page_id}');
  }}

  return response.json();
}}

export const targetRoute = '{route}';
"""


def _generate_controller(domain_slug: str, vue_page_name: str, page_id: str, legacy_url: str) -> str:
    return f"""package com.example.am.{domain_slug}.web;

import java.util.List;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.example.am.{domain_slug}.dto.{vue_page_name}Row;
import com.example.am.{domain_slug}.dto.{vue_page_name}SearchCondition;
import com.example.am.{domain_slug}.service.{vue_page_name}Service;

@RestController
@RequestMapping("/api/{slug(page_id)}")
public class {vue_page_name}Controller {{

    private final {vue_page_name}Service service;

    public {vue_page_name}Controller({vue_page_name}Service service) {{
        this.service = service;
    }}

    @PostMapping("/search")
    public List<{vue_page_name}Row> search(@RequestBody {vue_page_name}SearchCondition request) {{
        // Legacy URL hint: {legacy_url or 'manual review required'}
        return service.search(request);
    }}
}}
"""


def _generate_service_interface(domain_slug: str, vue_page_name: str) -> str:
    return f"""package com.example.am.{domain_slug}.service;

import java.util.List;
import com.example.am.{domain_slug}.dto.{vue_page_name}Row;
import com.example.am.{domain_slug}.dto.{vue_page_name}SearchCondition;

public interface {vue_page_name}Service {{
    List<{vue_page_name}Row> search({vue_page_name}SearchCondition request);
}}
"""


def _generate_service_impl(domain_slug: str, vue_page_name: str, query_hint: str) -> str:
    return f"""package com.example.am.{domain_slug}.service.impl;

import java.util.Collections;
import java.util.List;
import org.springframework.stereotype.Service;
import com.example.am.{domain_slug}.dto.{vue_page_name}Row;
import com.example.am.{domain_slug}.dto.{vue_page_name}SearchCondition;
import com.example.am.{domain_slug}.service.{vue_page_name}Service;

@Service
public class {vue_page_name}ServiceImpl implements {vue_page_name}Service {{

    @Override
    public List<{vue_page_name}Row> search({vue_page_name}SearchCondition request) {{
        // TODO: port legacy business logic
        // Query hint: {query_hint or 'manual review required'}
        return Collections.emptyList();
    }}
}}
"""


def _generate_dto(
    domain_slug: str,
    vue_page_name: str,
    suffix: str,
    dataset: DatasetModel | None,
) -> str:
    fields = dataset.columns if dataset else []
    declarations = "\n".join(
        f"    private {_java_type(column.type)} {column.name};"
        for column in fields[:20]
    ) or "    // TODO: add fields"
    return f"""package com.example.am.{domain_slug}.dto;

public class {vue_page_name}{suffix} {{
{declarations}
}}
"""


def _generate_mapper_xml(vue_page_name: str, sql_map_id: str, query_hint: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
  PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{vue_page_name}Mapper">

  <!-- Legacy SQL map: {sql_map_id or 'manual review required'} -->
  <!-- Query hint: {query_hint or 'manual review required'} -->
  <select id="search" parameterType="{vue_page_name}SearchCondition" resultType="{vue_page_name}Row">
    <!-- TODO: migrate legacy SQL here -->
    select 1
  </select>
</mapper>
"""


def _java_type(column_type: str) -> str:
    lowered = column_type.lower()
    if lowered in {"int", "integer", "long", "short"}:
        return "Integer"
    if lowered in {"double", "float", "number", "decimal"}:
        return "Double"
    return "String"
