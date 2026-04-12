# Internal Bundle Update Journal

## Current Release

- Version: `2026.04.12.2`
- Date: `2026-04-12`
- Impact level: `3`
- Recommended action: `fresh reinstall`

### Why This Release Is A Reinstall

- Older internal workspaces do not contain the update-decision metadata files.
- Older internal workspaces do not know the new `am-bridge.config.local.json` override rule.
- The report workflow now assumes a stronger English main report contract and a Korean derived-summary flow.

### What Changed

- Added `bundle-version.json` for machine-readable install impact decisions.
- Added `update-playbook.md` so the internal AI can decide whether a future bundle needs rebootstrap or partial update.
- Added `am-bridge.config.local.json` support in the runtime config loader.
- Added `am-bridge.config.local.example.json` to show what should stay local in the internal environment.
- Strengthened the English canonical main report and Korean derived-summary guidance.

## Future Release Policy

Use `bundle-version.json` first.

- `installImpactLevel = 0`
  docs/checklists only
- `installImpactLevel = 1`
  prompt/skill/harness rules only
- `installImpactLevel = 2`
  runner/runtime/report generator changed, but rebootstrap is not required
- `installImpactLevel = 3`
  bootstrap/runtime/update structure changed enough that fresh reinstall is safer

If `requiresRebootstrap = true`, reinstall from a fresh bundle.
If `requiresRebootstrap = false`, follow `update-playbook.md` and preserve the local config plus internal artifacts.
