# Stage Procedure

## Goal

Provide a repeatable procedure for AI Pro acting as PL on AM work.

## Procedure

1. Receive the target page from the PM.
2. Run stage 1.
3. Review the package, especially dataset salience and backend trace quality.
4. If wrong or weak, update the review JSON.
5. If the stage 1 evidence changed materially, rerun stage 1 or continue with the saved review JSON as the correction layer.
6. Run stage 2.
7. Validate file ownership and platform boundary.
8. Run stage 3 only when the PM wants scaffold/starter code.
9. Report what is locked, what is still uncertain, and what should happen next.

## Red Flags

- A large result grid exists but a small search or code dataset was chosen as primary.
- A dynamic wrapper transaction was treated as a resolved backend endpoint.
- A controller trace exists but DAO / SQL map is still missing and nobody wrote a review correction.
- Shared platform behavior was pulled into local page scope.
- Stage 2 or 3 was run before review corrections were applied.
