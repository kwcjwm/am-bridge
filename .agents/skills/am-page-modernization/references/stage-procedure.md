# Stage Procedure

## Goal

Provide a repeatable procedure for AI Pro acting as PL on AM work.

## Procedure

1. Receive the target page from the PM.
2. Run stage 1.
3. Save and inspect the detailed legacy analysis report, not just the summary package.
4. Review the package, especially dataset salience, backend trace quality, and related popup/subview screens.
5. If wrong or weak, update the review JSON.
6. If the stage 1 evidence changed materially, rerun stage 1 or continue with the saved review JSON as the correction layer.
7. Run stage 2.
8. Emit the Vue page config JSON and treat it as the implementation contract.
9. Emit the PM-facing test checklist and treat it as the validation contract.
10. Validate file ownership and platform boundary.
11. Run stage 3 only when the PM wants scaffold/starter code.
12. Report what is locked, what is still uncertain, and what should happen next.

## Red Flags

- A large result grid exists but a small search or code dataset was chosen as primary.
- A dynamic wrapper transaction was treated as a resolved backend endpoint.
- A controller trace exists but DAO / SQL map is still missing and nobody wrote a review correction.
- A popup or subview target was merged into the current page instead of being treated as a separate related screen.
- Shared platform behavior was pulled into local page scope.
- Stage 2 or 3 was run before review corrections were applied.
- The PM checklist does not reflect the primary dataset, key transactions, or related screen validation points.
