# Reports

Human-readable reporting sidecars live here.

Use this directory for per-page report bundles that keep repeated, high-cardinality data in CSV while the human-facing Markdown guides stay summary-oriented.

Recommended layout:

- `artifacts/reports/<legacy-page-path>/README.md`
- `artifacts/reports/<legacy-page-path>/README.en.md`
- `artifacts/reports/<legacy-page-path>/translate-to-korean.md`
- `artifacts/reports/<legacy-page-path>/stage1/README.md`
- `artifacts/reports/<legacy-page-path>/stage1/README.en.md`
- `artifacts/reports/<legacy-page-path>/stage1/sections/*.md`
- `artifacts/reports/<legacy-page-path>/stage2/README.md`
- `artifacts/reports/<legacy-page-path>/stage2/README.en.md`
- `artifacts/reports/<legacy-page-path>/stage2/sections/*.md`

English is the canonical generated surface:

- `README.md`
- `sections/*.md`

Compatibility mirrors may still exist for older links:

- `README.en.md`
- `sections/*.en.md`

Korean should be derived by AI after the English pack is reviewed:

- use `translate-to-korean.md` inside each page report bundle
- translate the page hub plus PM-facing summary docs first
- keep deep section docs, CSVs, and registries in English unless explicitly requested
- keep translated links pointed at the English canonical docs by default
- keep technical IDs and paths in backticks
- do not treat AI-translated Korean docs as the canonical source over the English originals

Each stage directory should still contain:

- compact `*.csv` files for repeated datasets, actions, grids, endpoints, related pages, and similar list-heavy artifacts
- `registries/` for fuller machine-oriented CSV exports when the compact view is not enough
- `ai-prompts.md` in `stage2/` when a prompt pack should travel with the plan

Keep narrative reports in:

- `artifacts/packages/*.md`
- `artifacts/plans/*.md`
