from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
from typing import Any

from am_bridge.models import (
    ConversionPlanModel,
    DatasetModel,
    PageConversionPackage,
    StarterBundleModel,
    StarterFileModel,
    VuePageConfigModel,
)
from am_bridge.stages.plan_stage import slug


def build_starter_bundle(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel | None = None,
) -> StarterBundleModel:
    ctx = _build_ctx(package, plan, vue_config)
    page_slug = slug(ctx["pageId"] or plan.pageId)
    frontend = [
        StarterFileModel(
            path=f"frontend/src/pages/{page_slug}/{plan.vuePageName}.vue",
            purpose="vue page starter",
            content=_generate_vue_page(ctx),
        ),
        StarterFileModel(
            path=f"frontend/src/composables/use{plan.vuePageName}.ts",
            purpose="page composable",
            content=_generate_composable(ctx),
        ),
        StarterFileModel(
            path=f"frontend/src/api/{page_slug or 'legacy-page'}.ts",
            purpose="typed api client",
            content=_generate_frontend_api(ctx),
        ),
    ]

    backend = [
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/web/{plan.vuePageName}Controller.java",
            purpose="spring controller",
            content=_generate_controller(ctx),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/service/{plan.vuePageName}Service.java",
            purpose="service interface",
            content=_generate_service_interface(ctx),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/service/impl/{plan.vuePageName}ServiceImpl.java",
            purpose="service implementation",
            content=_generate_service_impl(ctx),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/mapper/{plan.vuePageName}Mapper.java",
            purpose="mapper interface",
            content=_generate_mapper_interface(ctx),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/dto/{plan.vuePageName}SearchCondition.java",
            purpose="request dto",
            content=_generate_dto(ctx["domainSlug"], ctx["vuePageName"], "SearchCondition", ctx["searchFields"]),
        ),
        StarterFileModel(
            path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/dto/{plan.vuePageName}Row.java",
            purpose="response dto",
            content=_generate_dto(ctx["domainSlug"], ctx["vuePageName"], "Row", ctx["tableColumns"]),
        ),
    ]
    if ctx["lookupEndpoints"]:
        backend.append(
            StarterFileModel(
                path=f"backend/src/main/java/com/example/am/{ctx['domainSlug']}/dto/{plan.vuePageName}LookupOption.java",
                purpose="lookup dto",
                content=_generate_lookup_dto(ctx),
            )
        )
    backend.append(
        StarterFileModel(
            path=f"backend/src/main/resources/mapper/{plan.vuePageName}Mapper.xml",
            purpose="mapper xml",
            content=_generate_mapper_xml(ctx),
        )
    )

    return StarterBundleModel(
        pageId=ctx["pageId"],
        frontendFiles=frontend,
        backendFiles=backend,
        handoffPrompts={
            "stage3-frontend": _augment_prompt(plan.aiPrompts.get("frontend", ""), ctx, "frontend"),
            "stage3-backend": _augment_prompt(plan.aiPrompts.get("backend", ""), ctx, "backend"),
        },
    )


def _build_ctx(
    package: PageConversionPackage,
    plan: ConversionPlanModel,
    vue_config: VuePageConfigModel | None,
) -> dict[str, Any]:
    page = package.page
    comps = {item.componentId: item for item in getattr(page, "components", [])}
    txs = {item.transactionId: item for item in getattr(page, "transactions", [])}
    funcs = {item.functionName: item for item in getattr(page, "functions", [])}
    events = {item.sourceComponentId: item for item in getattr(page, "events", [])}
    nav_items = list(_gv(vue_config, "relatedPages", [])) or list(getattr(package, "relatedPages", []))
    nav = {_gv(item, "triggerFunction", ""): item for item in nav_items if _gv(item, "triggerFunction", "")}
    bindings = list(getattr(page, "bindings", []))
    validations = list(getattr(page, "validationRules", []))
    endpoints = list(_gv(vue_config, "endpoints", []))

    page_id = _gv(vue_config, "pageId", getattr(page, "pageId", plan.pageId)) or plan.pageId
    primary_dataset_id = _gv(vue_config, "primaryDatasetId", getattr(page, "primaryDatasetId", "")) or ""
    primary_tx_ids = list(_gv(vue_config, "primaryTransactionIds", getattr(page, "primaryTransactionIds", [])))
    main_grid_id = _gv(vue_config, "mainGridComponentId", getattr(page, "mainGridComponentId", ""))
    primary_dataset = _find_dataset(getattr(page, "datasets", []), primary_dataset_id)
    primary_trace = _find_primary_trace(package, primary_tx_ids)

    search_fields = _build_search_fields(
        list(_gv(vue_config, "searchControls", [])),
        comps,
        bindings,
        validations,
        getattr(page, "datasets", []),
    )
    table_columns = _build_table_columns(
        primary_dataset,
        comps.get(main_grid_id),
        primary_trace,
        list(_gv(vue_config, "grids", [])),
        main_grid_id,
    )
    lookup_endpoints = _build_lookup_endpoints(search_fields, getattr(page, "datasets", []), txs, endpoints, package.backendTraces, slug(page_id))
    actions = _build_action_contracts(
        list(_gv(vue_config, "searchControls", [])),
        list(_gv(vue_config, "actions", [])),
        comps,
        events,
        nav,
        primary_tx_ids,
        endpoints,
    )
    initial = _infer_initial_behavior(page, funcs, primary_tx_ids, lookup_endpoints)

    if not table_columns and primary_trace is not None:
        table_columns = [
            {
                "name": name,
                "label": _humanize(name),
                "tsType": "string",
                "javaType": "String",
            }
            for name in getattr(primary_trace, "responseFieldCandidates", [])
        ]

    return {
        "pageId": page_id,
        "pageName": _gv(vue_config, "pageName", getattr(page, "pageName", plan.vuePageName)) or plan.vuePageName,
        "vuePageName": plan.vuePageName,
        "route": plan.route,
        "interactionPattern": _gv(vue_config, "interactionPattern", getattr(page, "interactionPattern", "")),
        "domainSlug": slug(page_id or "legacy-page").replace("-", ""),
        "apiSlug": slug(page_id or "legacy-page"),
        "primaryDatasetId": primary_dataset_id,
        "mainGridComponentId": main_grid_id,
        "legacySourceFile": _gv(vue_config, "legacySourceFile", _gv(getattr(page, "legacy", None), "sourceFile", "")),
        "searchFields": search_fields,
        "tableColumns": table_columns,
        "lookupEndpoints": lookup_endpoints,
        "actions": actions,
        "initial": initial,
        "primaryTrace": primary_trace,
        "legacyUrl": getattr(primary_trace, "url", ""),
        "sqlMapId": getattr(primary_trace, "sqlMapId", ""),
        "sqlMapFile": getattr(primary_trace, "sqlMapFile", ""),
        "querySummary": getattr(primary_trace, "querySummary", ""),
        "legacySql": _extract_legacy_sql(primary_trace),
        "tableCandidates": list(getattr(primary_trace, "tableCandidates", [])) if primary_trace else [],
        "legacyChain": _legacy_chain(primary_trace),
        "verificationChecks": list(_gv(vue_config, "verificationChecks", plan.verificationChecks)),
    }


def _build_search_fields(
    search_controls: list[dict[str, Any]],
    comps: dict[str, Any],
    bindings: list[Any],
    validations: list[Any],
    datasets: list[DatasetModel],
) -> list[dict[str, Any]]:
    validation_by_target = {_gv(rule, "targetField", ""): rule for rule in validations if _gv(rule, "targetField", "")}
    seen: set[str] = set()
    fields: list[dict[str, Any]] = []
    for control in search_controls:
        comp_type = (_gv(control, "componentType", "") or "").lower()
        if comp_type in {"button", "imagebutton"}:
            continue
        comp_id = _gv(control, "componentId", "")
        comp = comps.get(comp_id)
        props = _gv(comp, "properties", {})
        dataset_id = _gv(props, "InnerDataset", "") or _gv(control, "datasetId", "") or _binding_dataset(comp_id, bindings)
        dataset = _find_dataset(datasets, dataset_id)
        field_name = (
            _gv(props, "CodeColumn", "")
            or _binding_column(comp_id, bindings)
            or _first_col(dataset)
            or slug(comp_id).replace("-", "_")
        )
        if not field_name or field_name in seen:
            continue
        label = _adjacent_static_label(comp, comps.values()) or _component_text(comp) or _humanize(field_name)
        control_type = _control_type(comp_type)
        rule = validation_by_target.get(comp_id)
        fields.append(
            {
                "name": field_name,
                "componentId": comp_id,
                "label": label,
                "controlType": control_type,
                "tsType": "boolean" if control_type == "checkbox" else "string",
                "javaType": "Boolean" if control_type == "checkbox" else "String",
                "required": rule is not None,
                "requiredMessage": _clean(_gv(rule, "message", ""), f"{label} is required before search."),
                "datasetId": dataset_id,
                "optionDatasetId": dataset_id if control_type == "select" else "",
                "optionValueField": _gv(props, "CodeColumn", "") or _first_col(dataset) or "value",
                "optionLabelField": _gv(props, "DataColumn", "") or _second_col(dataset) or _first_col(dataset) or "label",
                "defaultValue": "false" if control_type == "checkbox" else "''",
                "placeholder": _placeholder(control_type, label),
            }
        )
        seen.add(field_name)
    return fields


def _build_table_columns(
    primary_dataset: DatasetModel | None,
    grid_comp: Any,
    primary_trace: Any,
    grids: list[dict[str, Any]],
    main_grid_id: str,
) -> list[dict[str, Any]]:
    dataset_cols = {column.name: column for column in getattr(primary_dataset, "columns", [])}
    grid = next((item for item in grids if _gv(item, "componentId", "") == main_grid_id), grids[0] if grids else None)
    ordered = list(_gv(grid, "columns", [])) or list(dataset_cols) or list(getattr(primary_trace, "responseFieldCandidates", []))
    head_labels = _grid_labels(grid_comp)
    return [
        {
            "name": name,
            "label": head_labels.get(name, _humanize(name)),
            "tsType": _ts_type(_gv(dataset_cols.get(name), "type", "string")),
            "javaType": _java_type(_gv(dataset_cols.get(name), "type", "string")),
        }
        for name in ordered
    ]


def _build_lookup_endpoints(
    search_fields: list[dict[str, Any]],
    datasets: list[DatasetModel],
    txs: dict[str, Any],
    endpoints: list[dict[str, Any]],
    traces: list[Any],
    api_slug: str,
) -> list[dict[str, Any]]:
    trace_by_tx = {trace.transactionId: trace for trace in traces}
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for field in search_fields:
        dataset_id = field["optionDatasetId"]
        if not dataset_id or dataset_id in seen:
            continue
        endpoint = next((item for item in endpoints if dataset_id in list(_gv(item, "outputDatasets", []))), None)
        tx_id = _gv(endpoint, "transactionId", "")
        trace = trace_by_tx.get(tx_id)
        dataset = _find_dataset(datasets, dataset_id)
        suffix = _pascal(field["name"])
        items.append(
            {
                "fieldName": field["name"],
                "datasetId": dataset_id,
                "methodName": f"fetch{suffix}Options",
                "serviceMethod": f"get{suffix}Options",
                "mapperMethod": f"select{suffix}Options",
                "path": f"/api/{api_slug}/lookups/{slug(field['name'])}",
                "valueField": field["optionValueField"] or _first_col(dataset) or "value",
                "labelField": field["optionLabelField"] or _second_col(dataset) or "label",
                "transactionId": tx_id or _gv(txs.get(tx_id), "transactionId", ""),
                "legacyUrl": _gv(endpoint, "url", "") or getattr(trace, "url", ""),
                "sqlMapId": _gv(endpoint, "sqlMapId", "") or getattr(trace, "sqlMapId", ""),
                "sqlMapFile": getattr(trace, "sqlMapFile", ""),
                "legacySql": _extract_legacy_sql(trace),
                "querySummary": getattr(trace, "querySummary", ""),
                "tableCandidates": list(getattr(trace, "tableCandidates", [])),
            }
        )
        seen.add(dataset_id)
    return items


def _build_action_contracts(
    search_controls: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    comps: dict[str, Any],
    events: dict[str, Any],
    nav: dict[str, Any],
    primary_tx_ids: list[str],
    endpoints: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    actions_by_fn = {_gv(item, "functionName", ""): item for item in actions if _gv(item, "functionName", "")}
    primary = set(primary_tx_ids)
    items: list[dict[str, Any]] = []
    for control in search_controls:
        comp_type = (_gv(control, "componentType", "") or "").lower()
        if comp_type not in {"button", "imagebutton"}:
            continue
        comp_id = _gv(control, "componentId", "")
        comp = comps.get(comp_id)
        event = events.get(comp_id)
        handler = _gv(event, "handlerFunction", "")
        action = actions_by_fn.get(handler)
        tx_ids = list(_gv(action, "transactions", []))
        related = nav.get(handler)
        if primary.intersection(tx_ids):
            kind, method = "search", "search"
        elif related is not None:
            nav_type = _gv(related, "navigationType", "navigate") or "navigate"
            kind = nav_type
            page_id = _gv(related, "pageId", "") or comp_id
            method = f"open{_pascal(page_id)}{'Popup' if kind == 'popup' else 'Subview'}"
        elif tx_ids:
            kind, method = "transaction", f"run{_pascal(handler or comp_id)}"
        else:
            kind, method = "custom", f"handle{_pascal(handler or comp_id)}"
        endpoint = next((item for item in endpoints if _gv(item, "transactionId", "") in tx_ids), None)
        label = _component_text(comp)
        if not label and kind == "search":
            label = "Search"
        if not label and related is not None:
            label = _humanize(_gv(related, "pageId", "") or comp_id)
        if not label:
            label = _humanize(comp_id)
        items.append(
            {
                "componentId": comp_id,
                "label": label,
                "handlerFunction": handler,
                "methodName": method,
                "kind": kind,
                "endpoint": endpoint,
                "relatedPage": related,
            }
        )
    return items


def _infer_initial_behavior(page: Any, funcs: dict[str, Any], primary_tx_ids: list[str], lookup_endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    initial_handler = _gv(getattr(page, "legacy", None), "initialEvent", "")
    initial_txs = _collect_txs(initial_handler, funcs)
    lookup_fields = [
        item["fieldName"] for item in lookup_endpoints if item["transactionId"] and item["transactionId"] in initial_txs
    ] or [item["fieldName"] for item in lookup_endpoints]
    return {
        "handler": initial_handler,
        "lookupFields": lookup_fields,
        "autoSearch": bool(set(primary_tx_ids).intersection(initial_txs)),
    }


def _generate_vue_page(ctx: dict[str, Any]) -> str:
    search_markup = "\n".join(_render_search_field(field) for field in ctx["searchFields"])
    action_markup = "\n".join(_render_action_button(action) for action in ctx["actions"])
    header_cells = "\n".join(f"            <th>{col['label']}</th>" for col in ctx["tableColumns"])
    row_cells = "\n".join(f"            <td>{{{{ row.{col['name']} ?? '-' }}}}</td>" for col in ctx["tableColumns"])
    related_markup = "\n".join(
        _render_related_hint(action) for action in ctx["actions"] if action["kind"] in {"popup", "subview"}
    )
    key_field = ctx["tableColumns"][0]["name"] if ctx["tableColumns"] else "id"
    return f"""<template>
  <section class="page-shell">
    <header class="page-header">
      <div>
        <p class="eyebrow">{ctx["interactionPattern"] or "legacy-page"}</p>
        <h1>{ctx["pageName"] or ctx["vuePageName"]}</h1>
        <p class="legacy-source">Legacy page: {ctx["pageId"]}</p>
      </div>
      <dl class="meta-summary">
        <div><dt>Primary dataset</dt><dd>{{{{ meta.primaryDatasetId }}}}</dd></div>
        <div><dt>Legacy endpoint</dt><dd>{{{{ meta.legacyEndpoint || 'manual review required' }}}}</dd></div>
      </dl>
    </header>

    <form class="search-panel" @submit.prevent="actions.search()">
{search_markup or '      <p class="empty-note">No structured search controls were inferred.</p>'}
      <div class="search-actions">
{action_markup or '        <button type="submit">Search</button>'}
      </div>
      <p v-if="state.error" class="error-banner">{{{{ state.error }}}}</p>
    </form>

    <section class="result-panel">
      <div class="result-toolbar">
        <h2>Result grid</h2>
        <span>{{{{ state.rows.length }}}} rows</span>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
{header_cells or '              <th>Result</th>'}
            </tr>
          </thead>
          <tbody v-if="state.rows.length > 0">
            <tr v-for="(row, rowIndex) in state.rows" :key="row.{key_field} ?? rowIndex">
{row_cells or '              <td>{{ row }}</td>'}
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td :colspan="columns.length || 1" class="empty-cell">
                {{{{ state.loading || state.bootstrapping ? 'Loading legacy flow...' : 'No rows returned yet.' }}}}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside v-if="meta.relatedPages.length > 0" class="related-pages">
      <h2>Related screens</h2>
{related_markup or '      <p class="empty-note">No related page contracts were inferred.</p>'}
    </aside>
  </section>
</template>

<script setup lang="ts">
import {{ use{ctx["vuePageName"]} }} from '../../composables/use{ctx["vuePageName"]}';
const {{ state, actions, columns, meta }} = use{ctx["vuePageName"]}();
</script>

<style scoped>
.page-shell {{ display: grid; gap: 1.5rem; }}
.page-header, .search-panel, .result-panel, .related-pages {{ border: 1px solid #d7dce5; border-radius: 14px; padding: 1rem 1.25rem; background: #fff; }}
.page-header {{ display: flex; justify-content: space-between; gap: 1rem; align-items: start; }}
.eyebrow {{ margin: 0 0 0.25rem; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: #5b6472; }}
.legacy-source, .empty-note, .empty-cell {{ color: #5b6472; }}
.meta-summary {{ display: grid; gap: 0.75rem; margin: 0; }}
.meta-summary dt {{ font-size: 0.75rem; color: #5b6472; }}
.meta-summary dd {{ margin: 0.15rem 0 0; font-weight: 600; }}
.search-panel {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; align-items: end; }}
.search-field {{ display: grid; gap: 0.4rem; }}
.search-field span {{ font-weight: 600; }}
.search-field input, .search-field select {{ min-height: 40px; border: 1px solid #c9d2df; border-radius: 10px; padding: 0.65rem 0.8rem; }}
.search-actions {{ display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; }}
.search-actions button {{ min-height: 40px; border: none; border-radius: 10px; padding: 0.7rem 1rem; background: #0f4c81; color: #fff; cursor: pointer; }}
.search-actions button.secondary {{ background: #5b6472; }}
.error-banner {{ margin: 0; color: #b42318; }}
.result-toolbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }}
.table-wrapper {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 0.75rem; border-bottom: 1px solid #e4e9f0; text-align: left; }}
th {{ background: #f7f9fc; font-size: 0.9rem; }}
.related-pages ul {{ margin: 0; padding-left: 1.1rem; }}
</style>
"""


def _generate_composable(ctx: dict[str, Any]) -> str:
    defaults = "\n".join(f"    {field['name']}: {field['defaultValue']}," for field in ctx["searchFields"])
    lookups_state = "\n".join(f"      {item['fieldName']}: [] as LookupOption[]," for item in ctx["lookupEndpoints"])
    cols = ",\n".join(
        f"  {{ key: {json.dumps(col['name'])}, label: {json.dumps(col['label'], ensure_ascii=False)} }}"
        for col in ctx["tableColumns"]
    )
    extra_imports = ", ".join(item["methodName"] for item in ctx["lookupEndpoints"])
    extra_imports = f", {extra_imports}" if extra_imports else ""
    validations = "\n".join(
        f"    if (!state.searchForm.{field['name']}) {{ throw new Error({json.dumps(field['requiredMessage'], ensure_ascii=False)}); }}"
        for field in ctx["searchFields"]
        if field["required"]
    ) or "    return;"
    lookup_loaders = "\n\n".join(_render_lookup_loader(item) for item in ctx["lookupEndpoints"])
    init_steps = "\n".join(
        f"      await {_loader_name(item)}();"
        for item in ctx["lookupEndpoints"]
        if item["fieldName"] in set(ctx["initial"]["lookupFields"])
    )
    if ctx["initial"]["autoSearch"]:
        init_steps = (init_steps + "\n" if init_steps else "") + "      await search();"
    init_steps = init_steps or "      return;"
    helper_actions = "\n\n".join(_render_action_handler(item) for item in ctx["actions"] if item["methodName"] != "search")
    action_exports = ",\n      ".join(dict.fromkeys(["search"] + [item["methodName"] for item in ctx["actions"] if item["methodName"] != "search"]))
    related_pages = ",\n        ".join(_related_literal(item) for item in ctx["actions"] if item["kind"] in {"popup", "subview"})
    return f"""import {{ onMounted, reactive }} from 'vue';
import {{
  fetch{ctx["vuePageName"]}Rows,
  type {ctx["vuePageName"]}LookupOption as LookupOption,
  type {ctx["vuePageName"]}Row,
  type {ctx["vuePageName"]}SearchCondition{extra_imports}
}} from '../api/{ctx["apiSlug"]}';

const columns = [
{cols or '  { key: "value", label: "Value" }'}
] as const;

function createDefaultSearchForm(): {ctx["vuePageName"]}SearchCondition {{
  return {{
{defaults or '    // TODO: add inferred search fields'}
  }};
}}

export function use{ctx["vuePageName"]}() {{
  const state = reactive({{
    searchForm: createDefaultSearchForm(),
    rows: [] as {ctx["vuePageName"]}Row[],
    lookups: {{
{lookups_state or '      // TODO: add inferred lookup datasets'}
    }},
    loading: false,
    bootstrapping: false,
    error: '',
  }});

  function validateSearch() {{
{validations}
  }}

  async function search() {{
    state.error = '';
    state.loading = true;
    try {{
      validateSearch();
      state.rows = await fetch{ctx["vuePageName"]}Rows(state.searchForm);
    }} catch (error) {{
      state.error = error instanceof Error ? error.message : 'Failed to load rows.';
    }} finally {{
      state.loading = false;
    }}
  }}

{lookup_loaders or ''}

{helper_actions or ''}

  async function initialize() {{
    state.bootstrapping = true;
    state.error = '';
    try {{
{init_steps}
    }} catch (error) {{
      state.error = error instanceof Error ? error.message : 'Failed to initialize page.';
    }} finally {{
      state.bootstrapping = false;
    }}
  }}

  onMounted(() => {{
    void initialize();
  }});

  return {{
    state,
    columns,
    actions: {{
      {action_exports}
    }},
    meta: {{
      primaryDatasetId: {json.dumps(ctx["primaryDatasetId"])},
      mainGridComponentId: {json.dumps(ctx["mainGridComponentId"])},
      legacyEndpoint: {json.dumps(ctx["legacyUrl"])},
      sqlMapId: {json.dumps(ctx["sqlMapId"])},
      relatedPages: [
        {related_pages}
      ],
    }},
  }};
}}

export default use{ctx["vuePageName"]};
"""


def _generate_frontend_api(ctx: dict[str, Any]) -> str:
    search_fields = "\n".join(f"  {field['name']}: {field['tsType']};" for field in ctx["searchFields"]) or "  // TODO: add request fields"
    row_fields = "\n".join(f"  {col['name']}: {col['tsType']};" for col in ctx["tableColumns"]) or "  value: string;"
    lookup_fetchers = "\n\n".join(_render_lookup_fetcher(ctx, item) for item in ctx["lookupEndpoints"])
    return f"""export interface {ctx["vuePageName"]}SearchCondition {{
{search_fields}
}}

export interface {ctx["vuePageName"]}Row {{
{row_fields}
}}

export interface {ctx["vuePageName"]}LookupOption {{
  value: string;
  label: string;
  raw: Record<string, unknown>;
}}

export interface {ctx["vuePageName"]}BackendLookupOption {{
  value: string;
  label: string;
}}

async function requestJson<T>(input: string, init?: RequestInit): Promise<T> {{
  const response = await fetch(input, {{
    headers: {{ 'Content-Type': 'application/json' }},
    ...init,
  }});
  if (!response.ok) {{
    throw new Error(`Request failed: ${{response.status}} ${{response.statusText}}`);
  }}
  return response.json() as Promise<T>;
}}

export async function fetch{ctx["vuePageName"]}Rows(searchForm: {ctx["vuePageName"]}SearchCondition): Promise<{ctx["vuePageName"]}Row[]> {{
  return requestJson<{ctx["vuePageName"]}Row[]>('/api/{ctx["apiSlug"]}/search', {{
    method: 'POST',
    body: JSON.stringify(searchForm),
  }});
}}

{lookup_fetchers or ''}

export const targetRoute = {json.dumps(ctx["route"])};
export const legacySearchEndpoint = {json.dumps(ctx["legacyUrl"])};
"""


def _generate_controller(ctx: dict[str, Any]) -> str:
    lookup_import = f"import com.example.am.{ctx['domainSlug']}.dto.{ctx['vuePageName']}LookupOption;\n" if ctx["lookupEndpoints"] else ""
    lookup_methods = "\n\n".join(_controller_lookup_method(item, ctx) for item in ctx["lookupEndpoints"])
    return f"""package com.example.am.{ctx["domainSlug"]}.web;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}Row;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}SearchCondition;
{lookup_import}import com.example.am.{ctx["domainSlug"]}.service.{ctx["vuePageName"]}Service;

@RestController
@RequestMapping("/api/{ctx["apiSlug"]}")
public class {ctx["vuePageName"]}Controller {{

    private final {ctx["vuePageName"]}Service service;

    public {ctx["vuePageName"]}Controller({ctx["vuePageName"]}Service service) {{
        this.service = service;
    }}

    @PostMapping("/search")
    public List<{ctx["vuePageName"]}Row> search(@RequestBody {ctx["vuePageName"]}SearchCondition request) {{
        // Legacy chain: {ctx["legacyChain"] or 'manual trace review required'}
        // Legacy route: {ctx["legacyUrl"] or 'manual review required'}
        return service.search(request);
    }}

{lookup_methods or ''}
}}
"""


def _generate_service_interface(ctx: dict[str, Any]) -> str:
    lookup_import = f"import com.example.am.{ctx['domainSlug']}.dto.{ctx['vuePageName']}LookupOption;\n" if ctx["lookupEndpoints"] else ""
    lookup_methods = "\n".join(f"    List<{ctx['vuePageName']}LookupOption> {item['serviceMethod']}();" for item in ctx["lookupEndpoints"])
    return f"""package com.example.am.{ctx["domainSlug"]}.service;

import java.util.List;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}Row;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}SearchCondition;
{lookup_import}
public interface {ctx["vuePageName"]}Service {{
    List<{ctx["vuePageName"]}Row> search({ctx["vuePageName"]}SearchCondition request);
{lookup_methods}
}}
"""


def _generate_service_impl(ctx: dict[str, Any]) -> str:
    lookup_import = f"import com.example.am.{ctx['domainSlug']}.dto.{ctx['vuePageName']}LookupOption;\n" if ctx["lookupEndpoints"] else ""
    lookup_methods = "\n\n".join(_service_lookup_method(item, ctx) for item in ctx["lookupEndpoints"])
    table_hint = ", ".join(ctx["tableCandidates"]) or "verify source tables"
    return f"""package com.example.am.{ctx["domainSlug"]}.service.impl;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}Row;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}SearchCondition;
{lookup_import}import com.example.am.{ctx["domainSlug"]}.mapper.{ctx["vuePageName"]}Mapper;
import com.example.am.{ctx["domainSlug"]}.service.{ctx["vuePageName"]}Service;

@Service
public class {ctx["vuePageName"]}ServiceImpl implements {ctx["vuePageName"]}Service {{

    private final {ctx["vuePageName"]}Mapper mapper;

    public {ctx["vuePageName"]}ServiceImpl({ctx["vuePageName"]}Mapper mapper) {{
        this.mapper = mapper;
    }}

    @Override
    public List<{ctx["vuePageName"]}Row> search({ctx["vuePageName"]}SearchCondition request) {{
        // Legacy controller/service/dao chain: {ctx["legacyChain"] or 'manual trace review required'}
        // SQL hint: {ctx["querySummary"] or 'manual review required'}
        // Table candidates: {table_hint}
        return mapper.search(request);
    }}

{lookup_methods or ''}
}}
"""


def _generate_mapper_interface(ctx: dict[str, Any]) -> str:
    lookup_import = f"import com.example.am.{ctx['domainSlug']}.dto.{ctx['vuePageName']}LookupOption;\n" if ctx["lookupEndpoints"] else ""
    lookup_methods = "\n".join(f"    List<{ctx['vuePageName']}LookupOption> {item['mapperMethod']}();" for item in ctx["lookupEndpoints"])
    return f"""package com.example.am.{ctx["domainSlug"]}.mapper;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}Row;
import com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}SearchCondition;
{lookup_import}
@Mapper
public interface {ctx["vuePageName"]}Mapper {{
    List<{ctx["vuePageName"]}Row> search({ctx["vuePageName"]}SearchCondition request);
{lookup_methods}
}}
"""


def _generate_dto(domain_slug: str, vue_page_name: str, suffix: str, fields: list[dict[str, Any]]) -> str:
    fields = fields[:20]
    decls = "\n".join(f"    private {item['javaType']} {item['name']};" for item in fields) or "    // TODO: add inferred fields"
    accessors = "\n\n".join(_java_accessor(item["javaType"], item["name"]) for item in fields) or "    // TODO: add accessors"
    return f"""package com.example.am.{domain_slug}.dto;

public class {vue_page_name}{suffix} {{
{decls}

{accessors}
}}
"""


def _generate_lookup_dto(ctx: dict[str, Any]) -> str:
    return f"""package com.example.am.{ctx["domainSlug"]}.dto;

public class {ctx["vuePageName"]}LookupOption {{

    private String value;
    private String label;

    public String getValue() {{
        return value;
    }}

    public void setValue(String value) {{
        this.value = value;
    }}

    public String getLabel() {{
        return label;
    }}

    public void setLabel(String label) {{
        this.label = label;
    }}
}}
"""


def _generate_mapper_xml(ctx: dict[str, Any]) -> str:
    extra_tables = ", ".join(ctx["tableCandidates"][1:])
    comments = [
        f"Legacy chain: {ctx['legacyChain']}" if ctx["legacyChain"] else "",
        f"Legacy SQL map: {ctx['sqlMapId']}" if ctx["sqlMapId"] else "",
        f"Legacy query hint: {ctx['querySummary']}" if ctx["querySummary"] else "",
        f"Verify joins for additional tables: {extra_tables}" if extra_tables else "",
    ]
    comments = "\n  ".join(f"<!-- {_xml_comment(text)} -->" for text in comments if text)
    lookup_selects = "\n\n".join(_lookup_mapper_select(item, ctx) for item in ctx["lookupEndpoints"])
    prefix = f"com.example.am.{ctx['domainSlug']}.dto.{ctx['vuePageName']}"
    search_sql = _render_search_sql(ctx)
    return f"""<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
  PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.am.{ctx["domainSlug"]}.mapper.{ctx["vuePageName"]}Mapper">

  {comments}
  <select id="search" parameterType="{prefix}SearchCondition" resultType="{prefix}Row">
{search_sql}
  </select>

{lookup_selects or ''}
</mapper>
"""


def _augment_prompt(base: str, ctx: dict[str, Any], target: str) -> str:
    lines = [
        f"Primary dataset: {ctx['primaryDatasetId'] or 'manual review required'}",
        f"Legacy endpoint: {ctx['legacyUrl'] or 'manual review required'}",
        f"Search fields: {', '.join(item['name'] for item in ctx['searchFields']) or 'none inferred'}",
        f"Grid columns: {', '.join(item['name'] for item in ctx['tableColumns']) or 'none inferred'}",
    ]
    if target == "frontend" and ctx["lookupEndpoints"]:
        lines.append("Lookup loaders: " + ", ".join(item["fieldName"] for item in ctx["lookupEndpoints"]))
    if target == "backend" and ctx["sqlMapId"]:
        lines.append(f"Legacy SQL map id: {ctx['sqlMapId']}")
    return base.rstrip() + "\n\nContract summary:\n- " + "\n- ".join(lines)


def _render_search_field(field: dict[str, Any]) -> str:
    if field["controlType"] == "select":
        return f"""      <label class="search-field">
        <span>{field["label"]}</span>
        <select v-model="state.searchForm.{field["name"]}">
          <option value="">{field["placeholder"]}</option>
          <option v-for="option in state.lookups.{field["name"]}" :key="option.value" :value="option.value">
            {{{{ option.label }}}}
          </option>
        </select>
      </label>"""
    input_type = "checkbox" if field["controlType"] == "checkbox" else "text"
    return f"""      <label class="search-field">
        <span>{field["label"]}</span>
        <input v-model="state.searchForm.{field["name"]}" type="{input_type}" placeholder="{field["placeholder"]}" />
      </label>"""


def _render_action_button(action: dict[str, Any]) -> str:
    css = "secondary" if action["kind"] != "search" else ""
    button_type = "submit" if action["methodName"] == "search" else "button"
    click = "" if action["methodName"] == "search" else f' @click="actions.{action["methodName"]}()"'
    return f'        <button type="{button_type}" class="{css}"{click} :disabled="state.loading || state.bootstrapping">{action["label"]}</button>'


def _render_related_hint(action: dict[str, Any]) -> str:
    related = action["relatedPage"]
    target = _gv(related, "pageId", "") or _gv(related, "target", "")
    status = _gv(related, "resolutionStatus", "") or "manual review required"
    return f"      <ul><li><strong>{action['label']}</strong>: {target or 'unresolved target'} ({status})</li></ul>"


def _render_lookup_loader(item: dict[str, Any]) -> str:
    return f"""  async function {_loader_name(item)}() {{
    state.lookups.{item["fieldName"]} = await {item["methodName"]}();
  }}"""


def _render_action_handler(item: dict[str, Any]) -> str:
    if item["kind"] == "popup":
        related = item["relatedPage"]
        page_id = _gv(related, "pageId", "") or _gv(related, "target", "")
        route_hint = f"/{slug(page_id)}" if page_id else "/"
        popup_features = _popup_window_features(related)
        popup_param_hint = _popup_param_hint(related)
        return f"""  function {item["methodName"]}() {{
    const popupUrl = {json.dumps(route_hint)};
    {popup_param_hint}
    window.open(popupUrl, '_blank', {json.dumps(popup_features)});
  }}"""
    if item["kind"] == "subview":
        target = _gv(item["relatedPage"], "target", "") or "manual review required"
        return f"""  function {item["methodName"]}() {{
    console.info({json.dumps(f"TODO: mount related subview contract for {target}.")});
  }}"""
    if item["kind"] == "transaction":
        endpoint = _gv(item["endpoint"], "url", "") or "manual review required"
        return f"""  async function {item["methodName"]}() {{
    console.info({json.dumps(f"TODO: port secondary transaction mapped from {endpoint}.")});
  }}"""
    return f"""  function {item["methodName"]}() {{
    console.info({json.dumps(f"TODO: port custom legacy action {item['handlerFunction']}.")});
  }}"""


def _related_literal(item: dict[str, Any]) -> str:
    related = item["relatedPage"]
    return (
        "{ "
        f"kind: {json.dumps(item['kind'])}, "
        f"target: {json.dumps(_gv(related, 'pageId', '') or _gv(related, 'target', ''))}, "
        f"status: {json.dumps(_gv(related, 'resolutionStatus', 'manual review required'))} "
        "}"
    )


def _render_lookup_fetcher(ctx: dict[str, Any], item: dict[str, Any]) -> str:
    return f"""export async function {item["methodName"]}(): Promise<{ctx["vuePageName"]}LookupOption[]> {{
  const rows = await requestJson<{ctx["vuePageName"]}BackendLookupOption[]>({json.dumps(item["path"])});
  return rows.map((row) => ({{
    value: String(row.value ?? ''),
    label: String(row.label ?? row.value ?? ''),
    raw: row as Record<string, unknown>,
  }}));
}}"""


def _controller_lookup_method(item: dict[str, Any], ctx: dict[str, Any]) -> str:
    sub_path = item["path"].replace(f"/api/{ctx['apiSlug']}", "")
    return f"""    @GetMapping("{sub_path}")
    public List<{ctx["vuePageName"]}LookupOption> {item["serviceMethod"]}() {{
        // Legacy lookup route: {item["legacyUrl"] or 'manual review required'}
        return service.{item["serviceMethod"]}();
    }}"""


def _service_lookup_method(item: dict[str, Any], ctx: dict[str, Any]) -> str:
    return f"""    @Override
    public List<{ctx["vuePageName"]}LookupOption> {item["serviceMethod"]}() {{
        // Legacy SQL map: {item["sqlMapId"] or 'manual review required'}
        return mapper.{item["mapperMethod"]}();
    }}"""


def _lookup_mapper_select(item: dict[str, Any], ctx: dict[str, Any]) -> str:
    comments = [
        f"Legacy lookup route: {item['legacyUrl']}" if item["legacyUrl"] else "",
        f"Legacy SQL map: {item['sqlMapId']}" if item["sqlMapId"] else "",
        f"Query hint: {item['querySummary']}" if item["querySummary"] else "",
    ]
    comment_block = "\n  ".join(f"<!-- {_xml_comment(text)} -->" for text in comments if text)
    lookup_sql = _render_lookup_sql(item)
    return f"""  {comment_block}
  <select id="{item["mapperMethod"]}" resultType="com.example.am.{ctx["domainSlug"]}.dto.{ctx["vuePageName"]}LookupOption">
{lookup_sql}
  </select>"""


def _java_accessor(java_type: str, field_name: str) -> str:
    method = _pascal(field_name)
    return f"""    public {java_type} get{method}() {{
        return {field_name};
    }}

    public void set{method}({java_type} {field_name}) {{
        this.{field_name} = {field_name};
    }}"""


def _render_search_sql(ctx: dict[str, Any]) -> str:
    legacy_sql = _normalize_legacy_sql(ctx.get("legacySql", ""))
    if legacy_sql:
        return _indent_block(legacy_sql, 4)

    base_table = ctx["tableCandidates"][0] if ctx["tableCandidates"] else "TODO_PRIMARY_TABLE"
    select_cols = ",\n      ".join(item["name"] for item in ctx["tableColumns"]) or "*"
    where = "\n".join(
        f"      <if test=\"{item['name']} != null and {item['name']} != ''\">AND {item['name']} = #{{{item['name']}}}</if>"
        for item in ctx["searchFields"]
    ) or "      <!-- TODO: add search predicates from legacy contract -->"
    return "\n".join(
        [
            "    SELECT",
            f"      {select_cols}",
            f"    FROM {base_table}",
            "    <where>",
            where,
            "    </where>",
        ]
    )


def _render_lookup_sql(item: dict[str, Any]) -> str:
    table = item["tableCandidates"][0] if item["tableCandidates"] else "TODO_LOOKUP_TABLE"
    return "\n".join(
        [
            "    SELECT",
            f"      {item['valueField']} AS value,",
            f"      {item['labelField']} AS label",
            f"    FROM {table}",
            f"    GROUP BY {item['valueField']}, {item['labelField']}",
            f"    ORDER BY {item['valueField']} ASC",
        ]
    )


def _extract_legacy_sql(trace: Any) -> str:
    sql_map_file = getattr(trace, "sqlMapFile", "") if trace is not None else ""
    sql_map_id = getattr(trace, "sqlMapId", "") if trace is not None else ""
    if not sql_map_file or not sql_map_id:
        return ""

    path = Path(sql_map_file)
    if not path.exists():
        return ""

    raw = _read_text_with_fallbacks(path)
    if not raw:
        return ""

    pattern = re.compile(rf"<select[^>]*id=\"{re.escape(sql_map_id)}\"[^>]*>(.*?)</select>", re.IGNORECASE | re.DOTALL)
    match = pattern.search(raw)
    if match is None:
        return ""
    return textwrap.dedent(match.group(1)).strip()


def _normalize_legacy_sql(sql: str) -> str:
    text = str(sql or "").strip()
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"#([A-Za-z_][A-Za-z0-9_]*)#", r"#{\1}", text)
    return text


def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" if line else "" for line in text.splitlines())


def _read_text_with_fallbacks(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp949", "euc-kr", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def _gv(value: Any, key: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _find_dataset(datasets: list[DatasetModel], dataset_id: str) -> DatasetModel | None:
    return next((item for item in datasets if item.datasetId == dataset_id), None)


def _find_primary_trace(package: PageConversionPackage, primary_tx_ids: list[str]) -> Any:
    traces = list(getattr(package, "backendTraces", []))
    for tx_id in primary_tx_ids:
        trace = next((item for item in traces if getattr(item, "transactionId", "") == tx_id), None)
        if trace is not None:
            return trace
    return traces[0] if traces else None


def _binding_dataset(component_id: str, bindings: list[Any]) -> str:
    for binding in bindings:
        if _gv(binding, "componentId", "") == component_id and _gv(binding, "datasetId", ""):
            return str(_gv(binding, "datasetId", ""))
    return ""


def _binding_column(component_id: str, bindings: list[Any]) -> str:
    for binding in bindings:
        if _gv(binding, "componentId", "") != component_id:
            continue
        column_name = _gv(binding, "columnName", "")
        if column_name:
            return str(column_name)
    return ""


def _first_col(dataset: DatasetModel | None) -> str:
    columns = list(getattr(dataset, "columns", [])) if dataset is not None else []
    return columns[0].name if columns else ""


def _second_col(dataset: DatasetModel | None) -> str:
    columns = list(getattr(dataset, "columns", [])) if dataset is not None else []
    return columns[1].name if len(columns) > 1 else _first_col(dataset)


def _component_text(component: Any) -> str:
    props = _gv(component, "properties", {})
    if not isinstance(props, dict):
        return ""
    for key in ("Text", "Caption", "title"):
        value = props.get(key)
        if value:
            return str(value)
    return ""


def _adjacent_static_label(component: Any, components: Any) -> str:
    if component is None:
        return ""
    target_parent = _gv(component, "parentId", "")
    target_left = _as_float(_gv(component, "properties", {}).get("Left"))
    target_top = _as_float(_gv(component, "properties", {}).get("Top"))
    best_distance: float | None = None
    best_label = ""
    for other in components:
        if _gv(other, "componentId", "") == _gv(component, "componentId", ""):
            continue
        if _gv(other, "parentId", "") != target_parent:
            continue
        if _gv(other, "componentType", "") not in {"Static", "Label"}:
            continue
        label = _component_text(other)
        if not label:
            continue
        other_props = _gv(other, "properties", {})
        left_gap = target_left - _as_float(other_props.get("Left"))
        top_gap = abs(target_top - _as_float(other_props.get("Top")))
        if left_gap < 0 or left_gap > 220 or top_gap > 24:
            continue
        distance = (left_gap * 1.5) + top_gap
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_label = label
    return best_label


def _control_type(component_type: str) -> str:
    normalized = (component_type or "").lower()
    if normalized in {"combo", "combobox"}:
        return "select"
    if normalized in {"checkbox", "check"}:
        return "checkbox"
    if normalized in {"calendar", "date", "datepicker"}:
        return "date"
    return "text"


def _placeholder(control_type: str, label: str) -> str:
    if control_type == "select":
        return f"Select {label}"
    if control_type == "date":
        return f"Choose {label}"
    return f"Enter {label}"


def _grid_labels(grid_component: Any) -> dict[str, str]:
    grid_meta = _gv(_gv(grid_component, "properties", {}), "gridMeta", {})
    body_columns = list(_gv(grid_meta, "bodyColumns", []))
    head_columns = list(_gv(grid_meta, "headColumns", []))
    head_by_col = {str(_gv(item, "col", "")): str(_gv(item, "text", "")) for item in head_columns if _gv(item, "col", "")}
    labels: dict[str, str] = {}
    for item in body_columns:
        column_name = str(_gv(item, "columnName", ""))
        col_index = str(_gv(item, "col", ""))
        if not column_name:
            continue
        labels[column_name] = _clean(head_by_col.get(col_index, ""), _humanize(column_name))
    return labels


def _humanize(value: str) -> str:
    if not value:
        return ""
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    normalized = normalized.replace("_", " ").replace("-", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:1].upper() + normalized[1:] if normalized else value


def _clean(value: str, default: str = "") -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text or default


def _pascal(value: str) -> str:
    parts = re.split(r"[^0-9A-Za-z]+", value or "")
    compact = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return compact or "LegacyPage"


def _ts_type(value: str) -> str:
    normalized = (value or "").lower()
    if any(token in normalized for token in ("int", "long", "double", "decimal", "float", "number")):
        return "number"
    if "bool" in normalized:
        return "boolean"
    return "string"


def _java_type(value: str) -> str:
    normalized = (value or "").lower()
    if any(token in normalized for token in ("int", "long")):
        return "Long"
    if any(token in normalized for token in ("double", "decimal", "float", "number")):
        return "BigDecimal"
    if "bool" in normalized:
        return "Boolean"
    return "String"


def _legacy_chain(trace: Any) -> list[str]:
    if trace is None:
        return []
    items = [
        ".".join(filter(None, [getattr(trace, "controllerClass", ""), getattr(trace, "controllerMethod", "")])),
        ".".join(filter(None, [getattr(trace, "serviceImplClass", "") or getattr(trace, "serviceInterface", ""), getattr(trace, "serviceMethod", "")])),
        ".".join(filter(None, [getattr(trace, "daoClass", ""), getattr(trace, "daoMethod", "")])),
        getattr(trace, "sqlMapId", ""),
    ]
    return [item for item in items if item]


def _collect_txs(function_name: str, funcs: dict[str, Any]) -> list[str]:
    visited: set[str] = set()
    tx_ids: list[str] = []

    def walk(name: str) -> None:
        if not name or name in visited:
            return
        visited.add(name)
        fn = funcs.get(name)
        if fn is None:
            return
        for tx_id in getattr(fn, "callsTransactions", []) or []:
            if tx_id and tx_id not in tx_ids:
                tx_ids.append(tx_id)
        for callee in getattr(fn, "callsFunctions", []) or []:
            walk(callee)

    walk(function_name)
    return tx_ids


def _xml_comment(text: str) -> str:
    return str(text or "").replace("--", " ")


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _find_dataset(datasets: list[DatasetModel], dataset_id: str) -> DatasetModel | None:
    return next((item for item in datasets if item.datasetId == dataset_id), None)


def _find_primary_trace(package: PageConversionPackage, primary_tx_ids: list[str]) -> Any:
    if not package.backendTraces:
        return None
    for tx_id in primary_tx_ids:
        trace = next((item for item in package.backendTraces if item.transactionId == tx_id), None)
        if trace is not None:
            return trace
    for tx_id in package.page.primaryTransactionIds:
        trace = next((item for item in package.backendTraces if item.transactionId == tx_id), None)
        if trace is not None:
            return trace
    return package.backendTraces[0]


def _binding_column(component_id: str, bindings: list[Any]) -> str:
    for binding_type in ("code-data", "input", "value", "two-way"):
        for item in bindings:
            if _gv(item, "componentId", "") == component_id and _gv(item, "bindingType", "") == binding_type and _gv(item, "columnName", ""):
                return _gv(item, "columnName", "")
    return next(
        (_gv(item, "columnName", "") for item in bindings if _gv(item, "componentId", "") == component_id and _gv(item, "columnName", "")),
        "",
    )


def _binding_dataset(component_id: str, bindings: list[Any]) -> str:
    return next(
        (_gv(item, "datasetId", "") for item in bindings if _gv(item, "componentId", "") == component_id and _gv(item, "datasetId", "")),
        "",
    )


def _component_text(component: Any) -> str:
    return _clean(_gv(_gv(component, "properties", {}), "Text", ""), "")


def _adjacent_static_label(component: Any, candidates: Any) -> str:
    target_top = _to_int(_gv(_gv(component, "properties", {}), "Top", ""))
    target_left = _to_int(_gv(_gv(component, "properties", {}), "Left", ""))
    if target_top is None or target_left is None:
        return ""
    labels: list[tuple[int, str]] = []
    for item in candidates:
        if _gv(item, "componentType", "") != "Static":
            continue
        props = _gv(item, "properties", {})
        top = _to_int(_gv(props, "Top", ""))
        left = _to_int(_gv(props, "Left", ""))
        if top is None or left is None or left > target_left or abs(top - target_top) > 16:
            continue
        text = _clean(_gv(props, "Text", ""), "")
        if text:
            labels.append((target_left - left, text))
    labels.sort(key=lambda pair: pair[0])
    return labels[0][1] if labels else ""


def _grid_labels(grid_comp: Any) -> dict[str, str]:
    props = _gv(grid_comp, "properties", {})
    meta = _gv(props, "gridMeta", {})
    body = list(_gv(meta, "bodyColumns", []))
    head = list(_gv(meta, "headColumns", []))
    labels: dict[str, str] = {}
    for idx, column in enumerate(body):
        name = _gv(column, "columnName", "")
        text = _clean(_gv(head[idx], "text", "") if idx < len(head) else "", "")
        if name:
            labels[name] = text or _humanize(name)
    return labels


def _collect_txs(function_name: str, funcs: dict[str, Any], seen: set[str] | None = None) -> set[str]:
    if not function_name or function_name not in funcs:
        return set()
    seen = seen or set()
    if function_name in seen:
        return set()
    seen.add(function_name)
    func = funcs[function_name]
    txs = set(_gv(func, "callsTransactions", []))
    for nested in _gv(func, "callsFunctions", []):
        txs.update(_collect_txs(nested, funcs, seen))
    return txs


def _gv(subject: Any, key: str, default: Any = "") -> Any:
    if subject is None:
        return default
    if isinstance(subject, dict):
        return subject.get(key, default)
    return getattr(subject, key, default)


def _first_col(dataset: DatasetModel | None) -> str:
    if dataset is None or not getattr(dataset, "columns", []):
        return ""
    return dataset.columns[0].name


def _second_col(dataset: DatasetModel | None) -> str:
    if dataset is None or len(getattr(dataset, "columns", [])) < 2:
        return ""
    return dataset.columns[1].name


def _control_type(component_type: str) -> str:
    if component_type in {"combo", "combolist", "select"}:
        return "select"
    if component_type in {"checkbox", "check"}:
        return "checkbox"
    if component_type in {"calendar", "dateedit", "maskedit"}:
        return "date"
    return "text"


def _placeholder(control_type: str, label: str) -> str:
    if control_type == "select":
        return f"Select {label}"
    if control_type == "date":
        return f"Choose {label}"
    return f"Enter {label}"


def _ts_type(column_type: str) -> str:
    lowered = (column_type or "").lower()
    if lowered in {"int", "integer", "long", "short", "double", "float", "number", "decimal"}:
        return "number"
    if lowered in {"bool", "boolean"}:
        return "boolean"
    return "string"


def _java_type(column_type: str) -> str:
    lowered = (column_type or "").lower()
    if lowered in {"int", "integer", "long", "short"}:
        return "Integer"
    if lowered in {"double", "float", "number", "decimal"}:
        return "Double"
    if lowered in {"bool", "boolean"}:
        return "Boolean"
    return "String"


def _pascal(value: str) -> str:
    tokens = re.split(r"[^0-9A-Za-z]+|(?<=[a-z0-9])(?=[A-Z])", value or "")
    return "".join(token[:1].upper() + token[1:] for token in tokens if token)


def _humanize(value: str) -> str:
    tokens = re.split(r"[_\-\s]+|(?<=[a-z0-9])(?=[A-Z])", value or "")
    return " ".join(token.capitalize() for token in tokens if token) or value


def _clean(text: str, fallback: str) -> str:
    cleaned = " ".join((text or "").replace("\n", " ").split())
    return cleaned or fallback


def _loader_name(item: dict[str, Any]) -> str:
    return f"load{_pascal(item['fieldName'])}Options"


def _popup_window_features(related: Any) -> str:
    bindings = [str(item) for item in _gv(related, "parameterBindings", [])]
    numbers = [item for item in bindings if item.isdigit()]
    width = numbers[0] if len(numbers) >= 1 else "960"
    height = numbers[1] if len(numbers) >= 2 else "720"
    features = [f"width={width}", f"height={height}"]
    options = " ".join(bindings).lower()
    if "resize=false" in options:
        features.append("resizable=no")
    return ",".join(features)


def _popup_param_hint(related: Any) -> str:
    bindings = [str(item) for item in _gv(related, "parameterBindings", [])]
    param_binding = next((item for item in bindings if "=" in item), "")
    if not param_binding:
        return "// Legacy popup parameters were not inferred."
    return f"// TODO: port legacy popup parameter binding: {param_binding}"


def _legacy_chain(trace: Any) -> str:
    if trace is None:
        return ""
    parts = [
        f"{trace.controllerClass}.{trace.controllerMethod}" if trace.controllerClass or trace.controllerMethod else "",
        f"{trace.serviceImplClass}.{trace.serviceMethod}" if trace.serviceImplClass or trace.serviceMethod else "",
        f"{trace.daoClass}.{trace.daoMethod}" if trace.daoClass or trace.daoMethod else "",
    ]
    return " -> ".join(part for part in parts if part)


def _xml_comment(text: str) -> str:
    return (text or "").replace("--", "  ")


def _to_int(value: Any) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None
