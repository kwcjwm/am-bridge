# Phase 2 Implementation Contract

## Contract Rule

Phase 2 implementation must be traceable to accepted evidence:

- Phase 1 report
- Phase 1.5 QA result
- legacy FE source
- backend source
- screenshots
- CUBE platform references
- explicit PM/architect decision

If a behavior is not traceable, mark it as unresolved instead of inventing behavior.

## Responsibility Boundary

| Target Layer | Owns |
| --- | --- |
| CUBE platform | layout frame, menu, auth, permission, common controls, common popup, common message/error shell, common code lookup, i18n mechanism, design tokens |
| Vue page | page state, component composition, user interaction, UI validation, API call timing, local loading/error/empty state |
| API client | typed request/response bridge, endpoint calls, CUBE API wrapper usage |
| Spring controller | endpoint boundary, request parsing, response shape, permission annotation/filter hook |
| Spring service | business rule, authoritative validation, transaction orchestration, defaulting, save/search decisions |
| Mapper/query | SQL and persistence mapping |

## Implementation Quality Rules

- No hard-coded user-facing text except temporary unresolved notes.
- No local replacement for CUBE common features.
- No direct copy of MiPlatform transaction naming without target naming review.
- No FE-only business rule when the rule must be enforced server-side.
- No hidden API contract mismatch between Vue payload and Spring DTO.
- No shell-only mock data left in final implementation except explicit test fixtures.

## Required Traceability

Every API must trace:

- Vue caller
- target endpoint
- request DTO
- response DTO
- Spring controller method
- service method
- mapper/query candidate
- legacy transaction or backend source
- related report section

Every screen behavior must trace:

- UI event
- source evidence
- target handler
- CUBE/platform dependency
- validation/message key if applicable

Every CUBE UI implementation must trace:

- shell region or screenshot area
- CUBE component used
- props/events/slots/v-model mapping
- page state key
- API/DTO field if data-bound
- i18n key if user-facing
- style token or component variant
- local CSS exception if any

Every menu/layout implementation must trace:

- menu key
- route path/name
- permission key
- page frame usage
- action area placement
- button visible/enabled rule
- source evidence or PM decision
