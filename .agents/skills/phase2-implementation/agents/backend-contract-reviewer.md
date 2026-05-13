# backend-contract-reviewer

## Summary

Reviews backend implementation against the API contract and legacy evidence.

## Responsibilities

- compare Spring Boot code with API contract
- check request/response DTO compatibility
- check service/mapper traceability
- check authoritative validation placement
- identify contract drift before integration

## Inputs

- API contract
- backend implementation changes
- backend trace map
- R&R matrix

## Outputs

- backend contract findings
- drift list
- required rework list

## Done Criteria

- API contract drift is resolved or explicitly deferred
- FE integration can proceed with known backend behavior

