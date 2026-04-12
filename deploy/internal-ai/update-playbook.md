# Internal Bundle Update Playbook

Use this file when a new exported bundle has been copied into the company environment as a separate extracted directory.

## Goal

Decide whether the new bundle requires:

- `fresh reinstall`
- `runtime update only`
- `docs/prompt update only`

## Required Inputs

Read these files from the new extracted bundle:

- `bundle-version.json`
- `update-journal.md`
- `operator-script.md`
- `WORKFLOW.md`
- `REPORT-CONTRACT.md`

If the current live workspace also has `bundle-version.json`, compare the two versions.
If the current live workspace does not have `bundle-version.json`, treat the current live workspace as `legacy pre-update-structure`.

## Decision Rules

### Fresh Reinstall

Choose fresh reinstall when one or more of these are true:

- `requiresRebootstrap = true`
- the live workspace has no prior `bundle-version.json`
- the default operating model changed materially
- the workspace structure changed materially

### Runtime Update Only

Choose runtime update only when all of these are true:

- `requiresRebootstrap = false`
- optional deterministic support code changed, but the docs-first operating model is still compatible
- preserved local files can remain in place

Typical changed files:

- `scripts/ai_pro_stage_runner.py`
- `src/am_bridge/**`
- support-oriented prompt files
- report helper logic

### Docs / Prompt Update Only

Choose docs/prompt update only when:

- `installImpactLevel` is `0` or `1`
- optional support code did not change materially
- the report and workflow contracts remain compatible

## Local Files To Preserve

Do not overwrite these local files during an update unless explicitly intended:

- `inputs/`
- `artifacts/`
- `prompts/amprompt.md`
- `am-bridge.config.local.json`
- internal operator notes or locally added documents

## Internal AI Prompt For Update Judgment

```text
You are reviewing a newly extracted AM bundle update.

Read:
1. bundle-version.json
2. update-journal.md
3. update-playbook.md
4. WORKFLOW.md
5. REPORT-CONTRACT.md

Then decide one of:
- fresh reinstall
- runtime update only
- docs/prompt update only

Output:
1. decision
2. reason
3. which local files must be preserved
4. whether any optional support smoke test is required
5. exact next steps
```
