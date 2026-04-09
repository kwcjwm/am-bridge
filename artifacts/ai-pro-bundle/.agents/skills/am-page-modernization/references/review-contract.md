# Review Contract

## Purpose

The review JSON is the correction layer between deterministic extraction and staged planning.

## What May Be Corrected

- `primaryDatasetId`
- `secondaryDatasetIds`
- `primaryTransactionIds`
- `interactionPattern`
- `mainGridComponentId`
- per-dataset `role`, `primaryUsage`, `salienceScore`, `boundComponents`, `salienceReasons`
- per-transaction backend trace fields

## Rule

Do not silently override stage 1 in free-form prose if the correction should affect stage 2 or stage 3.
Write the correction into the review JSON so the next stage can reuse it.

## Review Loop

When the deterministic analyzer gets a page concept wrong, the AI review pass becomes the authoritative correction layer for later stages.

Typical examples:

- change the dominant dataset from a lookup dataset to the real grid/result dataset
- demote a view-state dataset out of primary flow
- replace an incomplete backend trace with the correct controller/service/DAO/SQL chain
- carry that decision into stage 2 and stage 3 without re-explaining the page every time
