# Visual Shell Contract

Use this contract when the PM provides one or more legacy screen captures such as `.jpg` or `.png`.

## Why This Exists

The deterministic analyzer is useful for:

- datasets
- transactions
- backend traces
- repeatable stage artifacts

It is not reliable enough to recreate customer-facing layout from structure alone.
If legacy screen images exist, treat them as the primary visual source for `UI Shell First`.

## Core Rule

When a reviewed legacy screenshot exists:

1. use the screenshot to decide visible block placement, section ordering, and button presence
2. use stage1/stage2 artifacts to lock dataset, action, API, validation, and backend contracts
3. do not let stage3 starter layout silently override the reviewed visual shell

Do not hardcode one layout heuristic such as:

- search on top
- grid in the middle
- detail at the bottom

That may be common, but it is not a safe universal rule.

## Recommended Artifact

Before stage1 or before any mock UI generation, create:

`artifacts/visual/<page>/visual-shell-brief.md`

If the PM wants a structured companion file, also create:

`artifacts/visual/<page>/ui-shell-blueprint.yaml`

## Visual Shell Brief Structure

The brief should contain these sections:

1. `Visual Sources`
   - exact image paths
   - which screenshot is primary
   - cropped or partial regions if used
2. `Visible Blocks`
   - major sections visible on screen
   - approximate order and grouping
   - which blocks are clearly visible vs uncertain
3. `Placement Contract`
   - buttons, tabs, grids, forms, popup entry points
   - which controls must remain visible in the shell
4. `Placeholder Behavior`
   - which actions are dummy placeholders
   - exact placeholder labels or alerts when behavior is not locked
5. `Unresolved Visual Areas`
   - hidden tabs
   - collapsed panels
   - cropped regions
   - modal or popup content not visible in the source image
6. `Boundary To Behavior Lock`
   - what the screenshot proves
   - what still depends on stage1 review, stage2 contract lock, and backend tracing

## Prompting Rule For Internal AI

When the PM provides images, explicitly state:

- screenshot-driven shell first
- stage1/stage2 for behavior lock second
- stage3 starter is scaffold, not visual truth

## Safe Fallback

If no screenshot exists:

- use the existing `UI Shell First` flow
- treat analyzer-driven shell layout as provisional
- state lower confidence in the shell sections of the report
