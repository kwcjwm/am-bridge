# Internal Bundle Update Journal

## Current Release

- Version: `2026.04.12.3`
- Date: `2026-04-12`
- Impact level: `3`
- Recommended action: `fresh reinstall`

### Why This Release Is A Reinstall

- The internal bundle is no longer organized around tool-first staged execution.
- Core operator guidance, bundle manifest shape, and default workspace expectations changed materially.
- The internal AI is now expected to lead analysis, reporting, and shell generation directly.

### What Changed

- Added `WORKFLOW.md`, `REPORT-CONTRACT.md`, `KOREAN-DELIVERY.md`, and `OPTIONAL-COMPLETENESS-SUPPORT.md`.
- Reframed the internal harness so the AI writes the main report and shell directly.
- Kept deterministic support only as optional completeness/cross-check support.
- Reduced the export surface by removing admin/bootstrap/tool-registry material from the internal bundle.

## Future Release Policy

Use `bundle-version.json` first.

- `installImpactLevel = 0`
  docs/checklists only
- `installImpactLevel = 1`
  prompt/skill/harness rules only
- `installImpactLevel = 2`
  optional support code or report helpers changed, but rebootstrap is not required
- `installImpactLevel = 3`
  bundle structure or default operating model changed enough that fresh reinstall is safer

If `requiresRebootstrap = true`, reinstall from a fresh bundle.
If `requiresRebootstrap = false`, follow `update-playbook.md` and preserve local inputs, artifacts, and prompts.
