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

## Implementation Role Harnesses

When moving from platform decision to code changes, use the role documents under `agents/`:

- `agents/cube-component-implementer.md`: CUBE component replacement, props/events/slots/v-model, data binding, validation, i18n.
- `agents/menu-layout-implementer.md`: menu, route, page frame, action area, permission, layout placement.
- `agents/component-style-implementer.md`: design tokens, spacing, typography, component variants, local CSS limits, i18n overflow.

Do not create additional reference documents just to restate these rules. The implementation guidance belongs in the role harnesses, and the workflow should only point to the relevant role.

## Platform Gap Format

When CUBE does not provide a needed feature, record:

- feature needed
- source evidence
- expected CUBE equivalent
- temporary local workaround if allowed
- owner for final decision
- risk if duplicated locally
