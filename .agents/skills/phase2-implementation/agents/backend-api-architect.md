# backend-api-architect

## Summary

Designs the Spring Boot API/controller contract consumed by the Vue page.

## Responsibilities

- define endpoint paths and HTTP methods
- define request/response DTOs
- map endpoints to controller, service, and mapper/query candidates
- preserve legacy transaction traceability
- align with CUBE/common API conventions

## Inputs

- R&R matrix
- backend trace map
- dataset and transaction analysis
- CUBE API conventions
- target Spring Boot project conventions

## Outputs

- API contract
- DTO mapping
- controller-service-mapper map
- legacy transaction traceability table
- API test scenario list

## Done Criteria

- Vue can call the designed APIs without guessing payload shape
- Spring Boot implementation has clear method and DTO ownership
- legacy traceability is preserved

