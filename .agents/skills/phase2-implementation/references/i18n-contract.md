# Phase 2 i18n Contract

## Default Rule

All user-facing labels and messages must use the CUBE/platform i18n mechanism.

## i18n Targets

- page title
- section labels
- field labels
- grid headers
- button labels
- validation messages
- confirmation messages
- error messages
- empty/loading/success messages
- popup titles and action labels

## Non-i18n Targets

- internal constants
- API field names
- route names
- technical log messages unless the platform requires localization
- mapper/query identifiers

## Key Design

Use a stable page-scoped key pattern unless the project defines another standard.

Example:

```text
pages.<pageId>.title
pages.<pageId>.search.<fieldName>
pages.<pageId>.grid.<columnName>
pages.<pageId>.button.<actionName>
pages.<pageId>.message.<messageName>
pages.<pageId>.validation.<ruleName>
```

## Required Output

- `i18n-key-plan.csv`
- locale file changes
- list of unresolved translations
- list of intentionally non-localized technical strings

