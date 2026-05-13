# CUBE Platform Adoption Guide

## Default Rule

CUBE is the default owner for common application behavior.

Phase 2 should reuse CUBE before creating page-local code.

## CUBE-Owned Areas

- application frame/layout
- menu and route integration
- auth and permission
- common buttons and action bars
- common grid/table components
- common form controls
- popup/modal shell
- common code lookup
- API client wrapper
- error and message handling
- loading/empty state pattern
- i18n mechanism
- design tokens and common style

## Page-Owned Areas

- page-specific field composition
- page-specific grid column selection
- page-specific search/save flow
- UI-level immediate validation
- row selection state
- popup invocation context
- API call timing
- mapping API result to page state

## Adoption Checklist

- Identify equivalent CUBE component before creating a local component.
- Use CUBE naming and style tokens before custom CSS.
- Use CUBE API wrapper before raw HTTP client calls.
- Use CUBE popup/message utilities before local modal/message code.
- Use CUBE i18n utilities before hard-coded labels.
- Record missing CUBE support as a platform gap, not as silent local duplication.

## Implementation Harnesses

Use these detailed harnesses when moving from platform decision to code changes:

- `cube-component-implementation-harness.md`: CUBE component replacement, props/events/slots/v-model, data binding, validation, i18n.
- `cube-menu-layout-implementation-harness.md`: menu, route, page frame, action area, permission, layout placement.
- `cube-style-implementation-harness.md`: design tokens, spacing, typography, component variants, local CSS limits, i18n overflow.

These harnesses are implementation documents. Their output must be reflected in Vue route/page/component/style changes, not only in design notes.

## Platform Gap Format

When CUBE does not provide a needed feature, record:

- feature needed
- source evidence
- expected CUBE equivalent
- temporary local workaround if allowed
- owner for final decision
- risk if duplicated locally
