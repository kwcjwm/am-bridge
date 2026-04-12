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
- `integrations/ai-pro/project/operator-prompts.md`

If the current live workspace also has `bundle-version.json`, compare the two versions.
If the current live workspace does not have `bundle-version.json`, treat the current live workspace as `legacy pre-update-structure`.

## Decision Rules

### Fresh Reinstall

Choose fresh reinstall when one or more of these are true:

- `requiresRebootstrap = true`
- the live workspace has no prior `bundle-version.json`
- bootstrap flow, workspace structure, or tool registration rules changed materially
- local runtime assumptions are no longer clearly compatible

### Runtime Update Only

Choose runtime update only when all of these are true:

- `requiresRebootstrap = false`
- runtime files changed, but the bootstrap/update structure is still compatible
- preserved local files can remain in place

Typical changed files:

- `scripts/ai_pro_stage_runner.py`
- `src/am_bridge/**`
- skill docs
- operator prompts
- report generation logic

Run the sample smoke test after updating:

```text
python scripts/ai_pro_stage_runner.py stage2 DefApp/Win32/form.xml --config am-bridge.config.json
```

### Docs / Prompt Update Only

Choose docs/prompt update only when:

- `installImpactLevel` is `0` or `1`
- runtime code did not change
- no smoke test is required by the release metadata

## Local Files To Preserve

Do not overwrite these local files during an update unless explicitly intended:

- `am-bridge.config.local.json`
- `artifacts/`
- `prompts/amprompt.md`
- internal operator notes or locally added documents

## Local Config Rule

The runtime now supports:

- base config: `am-bridge.config.json`
- local override: `am-bridge.config.local.json`

If `am-bridge.config.local.json` exists, it overrides matching keys from the base config.
Use that file for internal `sourceRoots`, `backendRoots`, and any local path changes that should survive future bundle updates.

## Internal AI Prompt For Update Judgment

```text
You are reviewing a newly extracted AM bundle update.

Read:
1. bundle-version.json
2. update-journal.md
3. update-playbook.md
4. operator-script.md

Then decide one of:
- fresh reinstall
- runtime update only
- docs/prompt update only

Output:
1. decision
2. reason
3. which local files must be preserved
4. whether smoke test is required
5. exact next steps
```
