# Implementation Plan: Round 3 CRaC Sidecars and Compose Stack Helpers

## Technical Approach

The round-2 CRaC reusable workflow used GitHub Actions job services, which are
defined at job creation time and are not a good fit for per-matrix optional
topology. The workflow now resolves `matrix.sidecars` in an early step and
starts requested sidecars with Docker only when needed. Training still runs with
host networking and privileged Docker so existing CRaC/CRIU assumptions remain
unchanged.

Backward compatibility is preserved by treating a missing `sidecars` field as
the original full topology: Postgres, Valkey, and RabbitMQ. Consumers that need
less can opt in per matrix row.

The Docker Compose CI/system-test helper is design-first. It is represented by
a spec, a guarded composite-action skeleton, and generic fixtures. The skeleton
documents the planned interface but intentionally does not run `docker compose`
or app-specific hooks.

## Files

- `.github/workflows/crac-train.yml`: per-matrix CRaC sidecar resolution,
  conditional sidecar startup, conditional training environment variables, and
  cleanup.
- `actions/compose-system-test-stack/action.yml`: design-first composite action
  skeleton with planned inputs and a placeholder guard.
- `actions/compose-system-test-stack/fixtures/compose.stack.example.yml`:
  generic fixture showing the intended compose-file shape.
- `actions/compose-system-test-stack/fixtures/routes.example.txt`: generic
  route wait-list fixture.
- `tests/test_crac_train_workflow.py`: text-level workflow regression tests for
  CRaC sidecar defaults, explicit `none`, validation, and README examples.
- `README.md`: updated CRaC matrix documentation and design-first Compose
  helper documentation.

## Requirement Mapping

- FR-001, FR-002, FR-003, FR-004: `Resolve requested sidecars` step.
- FR-005: `Run training` environment argument assembly.
- FR-006: `actions/compose-system-test-stack/action.yml` and fixtures.
- SC-001..SC-005: `tests/test_crac_train_workflow.py`.
- SC-006..SC-008: spec, skeleton action, fixtures, and README.

## Verification

- Run `python3 -m unittest discover -s tests`.
- Run `python3 -m coverage run --source=scripts.check_migrations -m unittest discover -s tests`.
- Run `python3 -m coverage report --fail-under=80`.
- Run `actionlint .github/workflows/*.yml` when the binary is available.

## Deviations

The Compose system-test helper is intentionally not wired into CI and does not
perform Docker orchestration in this round because the assignment classifies it
as design-first only.
