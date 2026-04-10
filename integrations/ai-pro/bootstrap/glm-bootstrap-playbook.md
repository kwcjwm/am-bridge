# GLM-4.7 Bootstrap Playbook For AI Pro

Use this document when the exported internal workspace has been opened in an AI Pro environment and `GLM-4.7` should perform the setup work.

The practical setup target has three layers:

1. project harness
2. a runnable deterministic `am-bridge` path
3. optional admin conveniences such as global `/harness` and registered tools

The final outcome is:

- the AM page workflow is discoverable from workspace files
- at least one real execution path works for `stage1`, `stage2`, and `stage3`
- the model can run staged AM work against `aaa.xml`
- stage1 emits a detailed integrated legacy analysis report
- stage2 emits a Vue page config JSON for implementation
- stage2 emits a PM-facing test checklist

## Inputs GLM-4.7 Must Discover

Before changing anything, discover:

- the current workspace root
- whether the current workspace is the exported internal bundle root
- whether AI Pro can read workspace files directly
- whether direct command execution or shell execution is possible
- whether Python is available for running `scripts/ai_pro_stage_runner.py`
- whether AI Pro supports global slash commands
- whether AI Pro supports saved prompts or workflow definitions
- whether AI Pro supports tool registration through JSON, TOML, YAML, or another config file

If one of those items is missing, report it instead of guessing.
If the current workspace is not the exported internal bundle root, stop and ask the operator to open the exported bundle instead of the external support repository.

## Phase 1: Project Harness

### Goal

Teach AI Pro how this AM project is supposed to operate.

### Primary Sources

- `AGENTS.md`
- `bootstrap-initial-prompt.md`
- `no-admin-runtime-prompt.md`
- `.agents/skills/am-page-modernization/SKILL.md`
- `integrations/ai-pro/project/am-page-modernization.md`
- `integrations/ai-pro/project/operator-prompts.md`

### Actions

1. Check whether AI Pro can read workspace files directly.
2. If yes:
   - keep `AGENTS.md` and `.agents/` as the primary project harness
   - use `bootstrap-initial-prompt.md` as the first operator message
3. If no:
   - register `integrations/ai-pro/project/am-page-modernization.md` as the project workflow prompt
   - optionally register the prompts in `operator-prompts.md` as saved prompts
4. Keep the PM/PL contract intact:
   - human operator = PM
   - GLM-4.7 = PL
   - `am-bridge` = deterministic tool layer

### Success Criteria

- the project workflow is discoverable without re-explaining it every session
- the model knows that stage 1 is not final truth
- the model knows to use `review.json` as the correction layer

## Phase 2: Runtime Capability

### Goal

Select at least one runnable deterministic execution path that does not rely on admin-only features.

### Primary Sources

- `scripts/am_stage.ps1`
- `scripts/ai_pro_stage_runner.py`
- `am-bridge.config.json`

### Actions

1. Check these candidate runtime paths in order:
   - `scripts/am_stage.ps1`
   - `python scripts/ai_pro_stage_runner.py ...`
   - registered `am-bridge-stage1|2|3`
   - `am-bridge-analyze ...`
2. Prefer the simplest path that does not depend on admin features.
3. Confirm the selected path can see:
   - `scripts/ai_pro_stage_runner.py`
   - `src/am_bridge`
   - `am-bridge.config.json`
4. If all runtime paths are blocked, stop and report the exact blocker.

### Success Criteria

- one default runtime path is selected
- that path can resolve the page path
- that path can emit the expected stage artifacts

## Phase 3: Optional Global Harness

### Goal

Make `/harness` available in AI Pro when the platform allows it.

### Source

- `integrations/ai-pro/global/harness-global.md`

### Actions

1. Find where AI Pro stores global commands, global prompts, or system command mappings.
2. Install the contents of `harness-global.md` only if the environment permits it.
3. Prefer `/harness` as the command alias.
4. If slash commands are not supported but saved prompts are supported, create the nearest equivalent named prompt:
   - name: `harness`
   - purpose: global harness inspection

### Success Criteria

- `/harness` or equivalent exists when the platform allows it
- invoking it makes the model inspect workspace harness files
- it does not jump straight into AM implementation

If this phase is blocked by server-side policy, do not stop the whole bootstrap.

## Phase 4: Optional Tool Registration

### Goal

Expose `am-bridge` as callable deterministic tools when the platform allows it.

### Primary Sources

- `scripts/ai_pro_stage_runner.py`
- `integrations/ai-pro/tools/tool-contract.md`
- `integrations/ai-pro/tools/tool-registry.example.json`
- `integrations/ai-pro/tools/tool-registry.single-tool.example.json`

### Actions

1. Find AI Pro's tool registration format.
2. If AI Pro prefers one tool per command:
   - register `am-bridge-stage1`
   - register `am-bridge-stage2`
   - register `am-bridge-stage3`
3. If AI Pro prefers one parameterized tool:
   - register one `am-bridge-stage` tool with `stage` as a required argument
4. Point every tool at:
   - `python <repo-root>/scripts/ai_pro_stage_runner.py ...`
5. Make sure the config file points at:
   - `<repo-root>/am-bridge.config.json`

### Success Criteria

- the model can call stage tools without parsing console prose
- tool output is JSON
- stage outputs include artifact paths and key decisions

If this phase is blocked by server-side policy, continue with the direct runtime path chosen in Phase 2.

## Phase 5: Target Project Wiring

Before claiming setup is complete, update:

- `am-bridge.config.json`

The operator must provide or confirm:

- `sourceRoots`
- `backendRoots`

Do not leave sample paths in place for production use.

## Phase 6: Validation

Run these checks:

1. confirm the project workflow is loaded from workspace files
2. confirm the selected runtime path still works
3. run `stage1` on a known page through the selected runtime path
   - confirm artifact generation
   - confirm `primaryDatasetId`
   - confirm backend trace summary exists when possible
4. run `stage2` on the same known page
   - confirm `...-vue-config.json` is created
   - confirm `...-pm-checklist.md` is created
5. if stage2 passes, optionally run stage3 on the same known page

### Expected Sample Validation Result

When run against the bundled sample `form.xml`, stage1 should show:

- `primaryDatasetId = ds_scorechk`
- `mainGridComponentId = Grid0`
- backend trace to `sampleDAO.ScoreChk`

## Failure Handling

If setup cannot be completed:

- report the missing AI Pro capability
- report the exact file, command, or registry that blocked setup
- do not fake success

## Final Report Format

When bootstrap is complete, report:

- project harness status
- default runtime path
- global harness status
- tool registration status
- config status
- validation result
- next operator action
