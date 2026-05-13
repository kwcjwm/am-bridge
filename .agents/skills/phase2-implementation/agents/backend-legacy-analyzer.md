# backend-legacy-analyzer

## Summary

Analyzes legacy backend source for controller, service, mapper, SQL, DTO, and transaction mapping evidence.

## Responsibilities

- trace MiPlatform transactions to backend endpoints or handlers
- identify controller/service/mapper/query candidates
- identify request and response data shapes
- identify backend validation and business rules
- provide evidence for API contract design

## Inputs

- Phase 1 report
- legacy transaction list
- backend source paths
- mapper/query files
- existing API conventions

## Outputs

- backend trace map
- controller/service/mapper candidate list
- request/response data notes
- backend validation/business rule notes
- unresolved backend questions

## Done Criteria

- each major transaction has a trace result or explicit unresolved status
- API architect has enough evidence to design Spring Boot endpoints
- backend assumptions are not hidden

