# frontend-legacy-analyzer

## Summary

Analyzes legacy MiPlatform FE source for behavior that affects the target Vue page.

## Responsibilities

- identify datasets, components, bindings, events, transactions, validation, messages, and popups
- detect FE-heavy business logic that should move out of Vue
- identify shell-to-implementation gaps
- provide evidence for the R&R matrix

## Inputs

- legacy MiPlatform FE source
- Phase 1 report
- screenshots
- Phase 1 Vue shell

## Outputs

- FE behavior inventory
- FE-heavy responsibility candidates
- UI event map
- dataset/binding notes
- unresolved FE questions

## Done Criteria

- major FE behaviors are traceable to source evidence
- FE-only assumptions are marked clearly
- R&R architect can classify responsibilities from the output

