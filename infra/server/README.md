# On-premise deployment (Portainer)

Deployment assets for running the stack as a Portainer stack on a shared
GPU server.

:::note
This environment was provisioned for a university project and has been
decommissioned. The compose file is preserved as the production
deployment definition; `infra/local/` is the reproducible path.
:::

## Contents

- `docker-compose.portainer.yml` — the stack definition: backend,
  frontend, Postgres, and Prometheus.

## Ports

The stack runs behind a shared host, so every service is published on a
team-allocated port rather than its default:

| Service | Host port | Container port |
|---|---|---|
| backend | 2026 | 8000 |
| frontend | 2027 | 3000 |
| db | 2028 | 5432 |
| prometheus | 2029 | 9090 |

## How deployment works

Deployment is driven by the `deploy-portainer` job in
`.github/workflows/cd.yml` through the **Portainer REST API** — not a
webhook. The distinction matters, because it is what makes the compose
file in git the source of truth:

1. The job checks out the repo and reads
   `docker-compose.portainer.yml` from git.
2. It rewrites `:latest` to `:sha-<short-sha>` on every line containing
   `ghcr.io`, pinning the deployment to the images just built. Lines for
   third-party images such as `postgres:16` are deliberately untouched.
3. It fetches the stack's current environment variables via
   `GET /api/stacks/<id>`. Portainer stores stack env vars separately
   from the compose content, and the update endpoint clears them unless
   they are passed back.
4. It `PUT`s the updated stack with `pullImage: true` (forces a pull of
   the new sha-tagged layers even when a manifest is cached) and
   `prune: false` (leaves containers outside the compose file running).

Because the compose file is re-read from git on every deploy, structural
changes — new ports, new env vars, an added service — roll out
automatically. Nothing is edited by hand in the Portainer UI.

A `smoke-test` job runs afterwards against the deployed stack and fails
the pipeline if the backend or frontend does not answer, leaving the
previous containers serving.

## Runner requirement

The job runs on a self-hosted runner because the Portainer host is
reachable only from the campus network. Public GitHub runners cannot
reach it. Both `deploy-portainer` and `smoke-test` are gated behind the
`ENABLE_DEPLOY` repository variable, so they skip cleanly when no such
runner or target exists.

## Secrets

Runtime secrets — `POSTGRES_PASSWORD`, the JWT signing key, OAuth client
secret, blob connection string — live in Portainer's stack environment
variables, never in git. The compose file references them by name only.
