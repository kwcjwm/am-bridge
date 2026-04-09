# AI Pro Tool Contract For am-bridge

Register `am-bridge` as deterministic tools.

Recommended public tool names:

- `am-bridge-stage1`
- `am-bridge-stage2`
- `am-bridge-stage3`

All of them should call [scripts/ai_pro_stage_runner.py](C:/workspace/am-bridge/scripts/ai_pro_stage_runner.py).

## Why Use The Runner

The normal CLI prints operator-oriented console text.
The runner prints structured JSON for model consumption.

## Expected Inputs

- `stage`
- `page_xml`
- `config_path`
- optional `review_path`

## Expected Outputs

The runner prints JSON including:

- stage name
- resolved input path
- generated artifact paths
- key page decisions
- compact backend trace summary
- frontend/backend file blueprints for later stages

## Recommended Registration Pattern

If AI Pro supports one tool with parameters, expose one `am-bridge-stage` tool.

If AI Pro prefers fixed commands, expose three tools:

- one with `stage1`
- one with `stage2`
- one with `stage3`
