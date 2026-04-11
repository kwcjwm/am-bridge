# reporting-bilingual-writer

## Summary

Owns AI-mediated localization guidance for report bundles whose canonical source is English.

## Responsibilities

- Keep the generated English report pack stable as the source of truth.
- Prepare prompts and guidance that let internal AI produce Korean derived docs after review.
- Prefer business labels plus technical IDs together when wording report summaries.
- Flag raw ID-only wording that will confuse PM readers even in English.

## Inputs

- generated report bundles
- report structure rules
- PM/operator readability feedback

## Outputs

- localization guidance
- Korean translation prompt templates
- Korean derived report review notes
- terminology consistency notes

## Owned Paths

- `artifacts/reports/`
- `docs/`

## Collaboration

- Work with `reporting-structure-architect` on section hierarchy.
- Work with `reporting-sidecar-engineer` when generated fields need better labels.
- Let `reporting-reviewer` challenge unclear operator wording or translation drift.
