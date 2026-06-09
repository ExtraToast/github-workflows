# Feature Specification: Round 3 CRaC Sidecars and Compose Stack Helpers

## User Stories & Testing

### User Story 1 - Select CRaC sidecars per service (Priority: P1)

A repository using the reusable CRaC training workflow can declare, per matrix
service, whether that service needs `postgres`, `valkey`, `rabbitmq`, or no
sidecars for checkpoint training.

**Success Criteria**

- SC-001: A matrix entry without `sidecars` keeps the round-2 behavior and
  starts Postgres, Valkey, and RabbitMQ.
- SC-002: A matrix entry can set `sidecars` to a list such as
  `["postgres", "valkey"]` and only those sidecars are started.
- SC-003: A matrix entry can set `sidecars` to `none`, `["none"]`, or `[]` and
  no sidecars are started.
- SC-004: Unsupported sidecar names fail before training starts.
- SC-005: Shared workflow defaults do not contain consumer service names,
  domains, hostnames, queue names, namespaces, image prefixes, or vendor URLs.

### User Story 2 - Design a Compose system-test stack helper (Priority: P2)

A repository maintainer can review a planned composite action surface for Docker
Compose CI/system-test stacks before a later production implementation.

**Success Criteria**

- SC-006: The action skeleton exposes inputs for compose files, service subsets,
  project name, wait strategy, diagnostics, cleanup, and migration checks.
- SC-007: The action skeleton is clearly marked as design-first and cannot be
  adopted accidentally as a working production helper.
- SC-008: Fixtures use generic service names and variable-based image names
  rather than copied application values.

## Functional Requirements

- FR-001: The CRaC workflow shall accept `matrix.sidecars` as either a JSON
  string or a JSON list.
- FR-002: Missing `matrix.sidecars` shall default to
  `postgres,valkey,rabbitmq` for backward compatibility.
- FR-003: Explicit `none`, `["none"]`, or `[]` shall disable all sidecars.
- FR-004: `none` shall not be accepted when combined with another sidecar.
- FR-005: The training container shall only receive sidecar environment
  variables for sidecars that were enabled.
- FR-006: The Compose helper skeleton shall define the planned composite action
  inputs without implementing real `docker compose` orchestration this round.

## Constraints

- Do not modify `/workspace/personal-stack` or `/workspace/website`; they are
  read-only reference repositories.
- Do not centralize application-specific compose files, route lists, migration
  assertions, queue names, hostnames, IPs, domains, namespaces, Vault paths, or
  image prefixes in this repository.
- Keep the existing CI shape, including the terminal `Pipeline Complete` job and
  Python coverage gate.
- Avoid networked local verification; the external orchestrator runs full CI.

## Out of Scope

- Implementing a production Docker Compose stack runner in this round.
- Copying consumer compose files or app-specific bootstrap scripts.
- Adding a new package, service repository, or non-GitHub CI integration.
