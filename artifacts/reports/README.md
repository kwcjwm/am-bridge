# Reports

Human-readable reporting sidecars live here.

Use this directory for per-page report bundles that keep repeated, high-cardinality data in CSV while the main Markdown reports stay summary-oriented.

Recommended layout:

- `artifacts/reports/<legacy-page-path>/stage1/`
- `artifacts/reports/<legacy-page-path>/stage2/`

Each stage directory should contain:

- `README.md` for a short summary and table index
- compact `*.csv` files for repeated datasets, actions, grids, endpoints, related pages, and similar list-heavy artifacts
- `registries/` for fuller machine-oriented CSV exports when the compact view is not enough
- `ai-prompts.md` in `stage2/` when a prompt pack should travel with the plan

Keep narrative reports in:

- `artifacts/packages/*.md`
- `artifacts/plans/*.md`
