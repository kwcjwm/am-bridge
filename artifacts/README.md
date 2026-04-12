# External Work Artifacts

`artifacts/` is for AM work products created in the external Codex support workspace.

Keep only external execution outputs here, such as:

- `analysis/`
- `reports/`
- `raw/`

Optional local-only outputs may still be generated during experiments, but they are not the canonical tracked examples for this repository:

- `packages/`
- `plans/`
- `reviews/`
- `starter/`
- `target/`

Generated sample outputs should not be treated as canonical examples and should not be kept tracked in the repository by default.

Do not place exported internal AI workspaces under this directory.
The generated carry-in workspace now lives under `exports/internal-ai-workspace`.
