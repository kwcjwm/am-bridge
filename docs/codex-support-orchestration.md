# Codex Support Orchestration

This document explains how the external Codex support sub-agents are meant to operate in this repository.

## Persistent vs Ephemeral

The following role definitions are persistent project assets:

- `.agents/agents/am-planner.md`
- `.agents/agents/am-ai-engineer.md`
- `.agents/agents/am-tool-developer.md`
- `.agents/agents/am-reviewer.md`

These files do not disappear.
They define the long-lived support roles for the external Codex workspace.

Actual spawned sub-agent instances are ephemeral.
They are created only when a task benefits from parallel support work and are usually closed after their results are integrated.

## Why Spawned Instances Are Closed

- avoid stale context carrying over between unrelated tasks
- avoid duplicate background work
- keep the support flow explicit and reviewable
- prevent confusion with the internal single-model AI runtime, which has no sub-agent feature

## Default Orchestration Policy

Use the four support roles like this:

- `am-planner`
  Use for framing goals, scope, sequencing, and acceptance criteria.
- `am-ai-engineer`
  Use for harness, prompt, bootstrap, and model-operating rules.
- `am-tool-developer`
  Use for runner, exporter, registry, and code-level tool concerns.
- `am-reviewer`
  Use for independent criticism, drift detection, and readiness gates.

Do not keep them running continuously.
Spawn them when a concrete side task is worth parallelizing, integrate the result, then close them.

## Practical Rule

For this repository, the best default is:

1. keep role definitions in `.agents/agents/`
2. spawn temporary instances only for bounded support work
3. integrate the result into source files
4. close the temporary instances

This means "the sub-agents exist" at the project level, but "their runtime workers are temporary" at the session level.
