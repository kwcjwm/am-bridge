# AM Bridge Internal AI Workspace

This directory is the source for the internal single-model AM workspace.

Use the exported bundle as the workspace root inside the company environment.
Do not point the internal AI at the root of the external support repository.
The first operator action should be to paste `bootstrap-initial-prompt.md` into the internal AI.
For the shortest operator path, follow `operator-script.md`.

The internal workspace should contain only:

- the internal `AGENTS.md`
- the initial bootstrap prompt
- the no-admin runtime prompt
- the operator script
- any optional custom prompts under `prompts/`
- the `am-page-modernization` skill assets
- AI Pro integration prompts and tool contracts
- the deterministic runner and configuration file
- the direct command wrapper script
- the runtime `src/am_bridge` package used by the runner
- the bundled public sample inputs used for first validation

It should not contain Codex-side support-agent instructions.

If you already have a strong operator-authored prompt such as `amprompt.md`, place it under `deploy/internal-ai/prompts/`.
It will be exported into bundle-root `prompts/amprompt.md`.
