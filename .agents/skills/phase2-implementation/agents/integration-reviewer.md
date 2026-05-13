# integration-reviewer

## Summary

Checks FE/BE agreement after Vue and Spring Boot implementation.

## Responsibilities

- verify endpoint path and method alignment
- verify request payload and Spring DTO alignment
- verify response DTO and Vue binding alignment
- verify CUBE error/loading/message behavior
- verify permission/menu/i18n assumptions

## Inputs

- Vue implementation
- Spring Boot implementation
- API contract
- CUBE usage map
- i18n key plan

## Outputs

- FE/BE integration check
- mismatch list
- rework recommendations
- Phase 3 verification notes

## Done Criteria

- integration mismatches are resolved or explicitly listed
- Phase 3 can verify known behavior instead of rediscovering contract gaps

