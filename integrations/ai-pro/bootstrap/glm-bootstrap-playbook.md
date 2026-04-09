# GLM-4.7 Bootstrap Playbook For AI Pro

Use this document when the repository has been cloned into an AI Pro environment and `GLM-4.7` should perform the setup work.

The setup target has three layers:

1. global harness
2. project harness
3. deterministic `am-bridge` tools

The final outcome is:

- `/harness` works
- the project AM workflow is discoverable
- `am-bridge-stage1|2|3` can be called by the model
- the model can run staged AM work against `aaa.xml`

## Inputs GLM-4.7 Must Discover

Before changing anything, discover:

- the repository root
- the AI Pro home or config root
- whether AI Pro supports global slash commands
- whether AI Pro supports saved prompts or workflow definitions
- whether AI Pro supports tool registration through JSON, TOML, YAML, or another config file
- whether Python is available for running `scripts/ai_pro_stage_runner.py`

If one of those items is missing, report it instead of guessing.

## Phase 1: Global Harness

### Goal

Make `/harness` available in AI Pro.

### Source

- `integrations/ai-pro/global/harness-global.md`

### Actions

1. Find where AI Pro stores global commands, global prompts, or system command mappings.
2. Install the contents of `harness-global.md` into that location.
3. Prefer `/harness` as the command alias.
4. If slash commands are not supported, create the nearest equivalent named prompt:
   - name: `harness`
   - purpose: global harness bootstrap

### Success Criteria

- `/harness` or equivalent exists
- invoking it makes the model inspect workspace harness files
- it does not jump straight into AM implementation

## Phase 2: Project Harness

### Goal

Teach AI Pro how this AM project is supposed to operate.

### Primary Sources

- `AGENTS.md`
- `.agents/skills/am-page-modernization/SKILL.md`
- `integrations/ai-pro/project/am-page-modernization.md`
- `integrations/ai-pro/project/operator-prompts.md`

### Actions

1. Check whether AI Pro can read workspace files directly.
2. If yes:
   - keep `AGENTS.md` and `.agents/` as the primary project harness
   - make sure `/harness` reads them
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

## Phase 3: Tool Registration

### Goal

Expose `am-bridge` as callable deterministic tools.

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
5. Make sure the config file points at real legacy locations:
   - `<repo-root>/am-bridge.config.json`

### Success Criteria

- the model can call stage tools without parsing console prose
- tool output is JSON
- stage outputs include artifact paths and key decisions

## Phase 4: Target Project Wiring

Before claiming setup is complete, update:

- `am-bridge.config.json`

The operator must provide or confirm:

- `sourceRoots`
- `backendRoots`

Do not leave sample paths in place for production use.

## Phase 5: Validation

Run these checks:

1. `/harness`
   - confirm harness status
   - confirm project workflow
   - confirm tool status
2. `am-bridge-stage1` on a known page
   - confirm JSON output
   - confirm `primaryDatasetId`
   - confirm backend trace summary exists when possible
3. if stage1 passes, optionally run stage2 or stage3 on the sample page

### Expected Sample Validation Result

When run against the sample `form.xml`, stage1 should show:

- `primaryDatasetId = ds_scorechk`
- `mainGridComponentId = Grid0`
- backend trace to `sampleDAO.ScoreChk`

## Failure Handling

If setup cannot be completed:

- report the missing AI Pro capability
- report the exact file or registry that blocked setup
- do not fake success

## Final Report Format

When bootstrap is complete, report:

- global harness status
- project harness status
- tool registration status
- config status
- validation result
- next operator action
