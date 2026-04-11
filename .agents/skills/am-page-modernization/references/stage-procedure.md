# Stage Procedure

## Goal

Provide a repeatable procedure for AI Pro acting as PL on AM work.

## Procedure

1. Receive the target page from the PM.
2. Decide whether the page needs `UI Shell First` before behavior is locked.
3. If yes, create a shell blueprint that fixes block placement, button placement, grid/detail areas, and popup anchors with explicit placeholder actions.
4. Run stage 1.
5. Save and inspect the detailed legacy analysis report, not just the summary package.
6. Review the package, especially dataset salience, backend trace quality, and related popup/subview screens.
7. If wrong or weak, update the review JSON.
8. If the stage 1 evidence changed materially, rerun stage 1 or continue with the saved review JSON as the correction layer.
9. Run stage 2.
10. Emit the Vue page config JSON and treat it as the implementation contract.
11. Emit the PM-facing test checklist and treat it as the validation contract.
12. Validate file ownership and platform boundary.
13. Run stage 3 only when the PM wants scaffold/starter code.
14. Report what is locked, what is still uncertain, and what should happen next.

## Red Flags

- A large result grid exists but a small search or code dataset was chosen as primary.
- A dynamic wrapper transaction was treated as a resolved backend endpoint.
- A controller trace exists but DAO / SQL map is still missing and nobody wrote a review correction.
- A popup or subview target was merged into the current page instead of being treated as a separate related screen.
- Shared platform behavior was pulled into local page scope.
- A `UI Shell` placeholder was presented as if the real behavior was already implemented.
- Stage 2 or 3 was run before review corrections were applied.
- The PM checklist does not reflect the primary dataset, key transactions, or related screen validation points.
