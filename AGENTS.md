# AM Bridge Support Harness

## Trigger Rules

- Use `/harness` when the user wants to design, audit, or extend the external Codex support workspace for AM preparation.
- Use `/harness` when the user wants to refine the internal single-model bundle that will be exported into the company environment.
- Use `$am-page-modernization` when simulating or reviewing the internal PL workflow from the external support workspace.
- Treat the human user as `PM`.
- Treat the AI assistant in this root workspace as the external support `PL`.
- Treat the company-side AI runtime as a separate single-model deployment target.

## Layout

- `.agents/agents/`
- `.agents/skills/`
- `deploy/internal-ai/`
- `exports/`
- `integrations/ai-pro/`
- `artifacts/analysis/`
- `artifacts/packages/`
- `artifacts/plans/`
- `artifacts/reviews/`
- `artifacts/starter/`

## Current Components

- Codex support agents: `am-planner`, `am-ai-engineer`, `am-tool-developer`, `am-reviewer`
- reporting support agents: `reporting-artifact-explorer`, `reporting-structure-architect`, `reporting-sidecar-engineer`, `reporting-reviewer`, `reporting-bilingual-writer`, `reporting-navigation-auditor`
- internal runtime reference: `am-pl`
- internal bundle source: `deploy/internal-ai/AGENTS.md`
- internal skill/runtime assets: `am-page-modernization`, `integrations/ai-pro/*`, `scripts/export_ai_pro_bundle.py`
- internal update assets: `deploy/internal-ai/bundle-version.json`, `deploy/internal-ai/update-journal.md`, `deploy/internal-ai/update-playbook.md`
- dual-lane operating model:
  - `UI Shell First` for early layout signoff
  - `Behavior / Contract Lock` for staged AM correctness
- internal default operating model:
  - `AI-first`
  - `docs-first`
  - deterministic support only when it materially helps completeness or traceability

## Execution Entry Points

- Use `/harness` in Codex to evolve the support project and the exportable internal bundle.
- Use `am-planner` for project shaping, `am-ai-engineer` for harness and prompt design, `am-tool-developer` for tool implementation, and `am-reviewer` for quality gates and rework requests in the external Codex workspace.
- Use `docs/codex-support-orchestration.md` as the default rule for how the four Codex support agents are spawned and closed.
- Use `scripts/export_ai_pro_bundle.py` to build the internal workspace that will be copied into the company environment.
- The default generated bundle path is `exports/internal-ai-workspace`.
- Inside the company environment, open the exported bundle root, not this repository root.
- The internal bundle's entry document is `deploy/internal-ai/AGENTS.md`, exported as bundle-root `AGENTS.md`.

## Working Rule

- Keep planning, harness design, tool implementation, and review as separate responsibilities in the external Codex support flow.
- Keep the external support workspace and the internal runtime bundle physically separate.
- If a document is intended for the internal AI, source it under `deploy/internal-ai/` or the export allowlist.
- Do not expose Codex-side support-agent instructions in the exported internal bundle.
- Let the reviewer request rework instead of silently changing another role's deliverable.
- Do not design the internal company workflow around sub-agent features that do not exist there.
- Do not confuse `UI Shell` signoff with behavior/API/SQL completion.
- Keep customer-facing layout alignment and behavior contract locking as separate lanes.
- Do not make deterministic analyzers or starter generators the default internal workflow if the internal AI can do the work directly.

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-04-12 | Added internal bundle update metadata, update playbook, and local config override support | Let the company-side single-model runtime judge future bundle updates without assuming a full reinstall every time |
| 2026-04-11 | Formalized `UI Shell First` and `Behavior / Contract Lock` as separate AM lanes inside the support harness | Align the external preparation workspace with real customer-facing AM execution pressure and single-model internal runtime limits |
| 2026-04-10 | Split the root workspace into an external Codex support harness and a separately exported internal AI bundle source | Prevent internal-model confusion and keep Codex support instructions out of the carry-in workspace |
| 2026-04-10 | Added four Codex-side support sub-agents for planning, AI engineering, tool development, and review | Prepare the internal single-model AM environment from an external high-capability workspace |
| 2026-04-09 | Added AM page modernization harness, stage workflow, and review loop | Let AI Pro act as PL on top of deterministic AM tools |
