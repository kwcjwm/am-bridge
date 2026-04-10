# Reporting TF

This document defines the external Codex support task force for improving AM reporting artifacts.

## Goal

Keep AM analysis depth high, but make the outputs much easier for humans to scan and act on.

The guiding rule is:

- summary Markdown for decisions and reading order
- compact sidecar CSV for repeated list-heavy data
- full registry exports for exhaustive machine-oriented detail

## TF Roles

- `reporting-artifact-explorer`
  Finds the cleanest insertion points in the current artifact pipeline.
- `reporting-structure-architect`
  Defines the human-facing report structure and section rules.
- `reporting-sidecar-engineer`
  Implements CSV/JSON sidecars and runtime wiring.
- `reporting-reviewer`
  Checks readability, consistency, and operator usefulness.

## Current Layout Rule

Per-page reporting bundles should live under:

- `artifacts/reports/<legacy-page-path>/stage1/`
- `artifacts/reports/<legacy-page-path>/stage2/`

Each stage directory should contain:

- `README.md`
- compact `*.csv`
- `registries/`
- `ai-prompts.md` for stage2 when the prompt pack is emitted

## Priority Order

1. Keep stage1/stage2 summary Markdown stable and decision-first.
2. Move repeated enumerations out of Markdown when they make the report hard to scan.
3. Prefer automatic emission over extra CLI flags.
4. Keep internal AI Pro runtime usage unchanged.
5. Validate outputs on the sample pages before expanding scope.

## Review Standard

The TF is not done when the data is merely complete.

It is done when:

- a PM can find the core decision points quickly
- a PL can jump from summary Markdown into the right CSV or registry file
- the internal single-model operator can use the artifacts without extra hidden context
