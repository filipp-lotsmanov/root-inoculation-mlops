# Root Inoculation MLOps

End-to-end MLOps platform for plant organ segmentation and root-tip
detection on *Arabidopsis thaliana* seedling images — trained, served,
monitored, and retrained from user feedback.

Built for the Netherlands Plant Eco-phenotyping Centre (NPEC) as a
university capstone. The model is a U-Net that segments root tissue and
extracts root-tip landmarks; the interesting part is everything around
it — the pipeline that trains it, the service that serves it, the
metrics that watch it, and the loop that retrains it when researchers
correct its mistakes.

## What's in here

| Layer | Implementation |
|---|---|
| **Model** | U-Net (`resnet34` encoder), BCE + Dice loss, AdamW, cosine schedule, early stopping on validation F1 — see [Models and provenance](#models-and-provenance) for which checkpoint each serving mode actually loads |
| **Package** | `cv-pipeline` — installable Python library with an `infer` and `train` CLI |
| **Serving** | FastAPI backend, 8 routers, three auth mechanisms, in-process or Azure ML endpoint |
| **Orchestration** | 6 Airflow DAGs submitting jobs to Azure ML |
| **Monitoring** | Prometheus metrics, rolling-confidence drift detection |
| **Retraining** | Feedback flywheel with conditional registration and champion-challenger promotion |
| **Delivery** | GitHub Actions CI/CD, Trivy scanning, GHCR, blue-green rollout with smoke-test gate |
| **UI** | Next.js 16 / React 19 researcher frontend |

## My contribution

This was a five-person team project. My work was:

- **Airflow orchestration and the Azure ML pipelines** — the DAGs, the
  job submission and monitoring layer, the feedback-to-retraining
  flywheel, and the champion-challenger promotion gate.
- **Most of the `cv-pipeline` package** — the inference path, training
  loop, validation, weights handling, and CLI.
- **An equal share of the backend/API and the infrastructure** —
  co-owned with teammates.

The frontend was built by other team members.

## Architecture

Three diagrams — request flow, deployment topology, and the retraining
loop — are in [`docs/architecture.md`](docs/architecture.md). Design
rationale (why FastAPI, why U-Net, why patch-based inference) lives in
the documentation site.

The short version: one inference code path serves three delivery forms.
The CLI, the HTTP API, and the Azure ML scoring script all call the same
`cv_pipeline.infer()`. There is no duplicated inference logic, so one
test suite validates all three and a fix propagates everywhere.

## Quick start

**Prerequisites:** Python 3.11, [`uv`](https://docs.astral.sh/uv/),
Docker Compose. A GPU is optional — inference falls back to CPU.

```bash
git clone https://github.com/filipp-lotsmanov/root-inoculation-mlops.git
cd root-inoculation-mlops
uv sync
```

### Run the full stack

```bash
./scripts/start.sh          # Linux/macOS
.\scripts\start.ps1         # Windows
```

`start.sh` copies `configs/env/env.example` to `configs/env/.env`, generates the
required secrets with `openssl rand -hex 32`, and starts the stack. To drive
compose yourself, pass the env file explicitly — the compose file lives in
`infra/local/` but reads its variables from `configs/env/.env`, so a bare
`docker compose up` fails on the `POSTGRES_PASSWORD` guard:

```bash
docker compose --env-file configs/env/.env -f infra/local/docker-compose.yml up --build
```

| Service | URL |
|---|---|
| Frontend | <http://localhost:3000> |
| Backend API (Swagger) | <http://localhost:8000/docs> |
| Prometheus | <http://localhost:9090> |
| Postgres | `localhost:5433` |

`docker compose down` stops everything; add `-v` to wipe the volumes.

### Inference without a server

```bash
uv run cv-pipeline infer \
    --image path/to/plate.png \
    --output results/
```

Writes a binary mask PNG and a result JSON containing the mask,
root-tip landmarks with pixel coordinates, and confidence scores.
Weights download on first run and cache under
`~/.cache/cv-pipeline/models/`.

### Training

```bash
uv run cv-pipeline train \
    --data-dir data/processed/train \
    --val-dir data/processed/val \
    --output-dir models/run_local
```

The same package trains and serves, so architecture and pre/post-processing
stay in lockstep by construction.

## Models and provenance

Two serving modes load two different checkpoints, and the distinction matters
when reading the numbers below.

| Serving mode | Selected by | Checkpoint |
|---|---|---|
| `local` (default) | `MODEL_VERSION` | `unet-v1` from the weight registry |
| `azure_ml` | `MODEL_ENDPOINT_URL` | `hades-unet:<version>` from the Azure ML registry |

`unet-v1` is the project's original baseline. It predates the packaged
`train.py` and is carried forward unchanged as a fixed serving artifact, which
is why `docker compose up` gives you the baseline rather than the best model.

The packaged `train.py` is what produced the Azure ML models. The weekly
`data_pipeline` DAG submits a training job, the run registers a new
`hades-unet` version if it clears the test-F1 gate, and the champion-challenger
promotion step decides whether it takes traffic. The most recent recorded run:

| | |
|---|---|
| Run | `airflow-weekly-training`, 2026-08-10 |
| Registered as | `hades-unet` version 18 |
| Best validation F1 | 0.8524 (epoch 28 of 43, early-stopped) |
| **Held-out test F1** | **0.8371** (test IoU 0.7199, 20,512 patches) |
| Data | 40,870 val / 20,512 test patch pairs; 58,646 train kept from 111,046 available |
| Learning rate | 3.929e-4, chosen by the `hyperparameter_tuning` sweep |

Quote the test F1, not the validation F1: the split is at source-image level
before patching, and empty-patch balancing is applied to the training set only,
so validation and test keep the natural background-heavy distribution.

The train figure above is post-balancing. Source images are split 70/20/10, but
training then drops surplus background-only patches (33,512 root + 25,134 empty
kept, ratio 0.75), so the raw patch counts read as a smaller train share than
the image-level ratios suggest.

The baseline checkpoint carries its own `val_f1` of 0.848, but it was measured
on a different validation set with different hyperparameters and is **not
comparable** to the numbers above. Neither is a claim that one model beats the
other.

The Azure ML workspace belongs to the university and is not publicly reachable,
so the registered `hades-unet` artifacts cannot be pulled by anyone cloning this
repository. The training log for the run above is preserved under
`docs/evidence/` as the durable record. Everything under `infra/airflow/`,
`infra/cloud/`, and `scripts/azure/` is readable but not runnable without that
workspace; `docker compose up` exercises the local path end to end.

## The retraining loop

The part I'd point at first. Researchers flag or correct predictions in
the UI; corrections land in Postgres. A daily DAG counts the ready set
and, once it crosses a threshold, fires a chain that stages the
corrections as a versioned Azure ML data asset, merges them into the
training data **while keeping the test set frozen**, and retrains.

A candidate model then passes two independent gates:

1. **Conditional registration** — it enters the model registry only if
   it clears an F1 threshold on the held-out test set.
2. **Promotion** — it is scored against the model currently serving
   traffic on a dedicated smoke asset. Only if it wins is a deployment
   created, health-checked at 0% traffic, and given a traffic split.

A model can register and still lose promotion. That separation is
deliberate: passing an offline threshold is not the same as being better
than what's already in production.

Retraining fires weekly on a schedule or on accumulated feedback,
whichever comes first. See
[`infra/airflow/README.md`](infra/airflow/README.md) for the DAG
inventory.

## Evaluation note

`val_f1` and `test_f1` are computed at the **dataset level** — true and
false positives accumulated across the whole set, then scored once — not
averaged per batch. Patches are mostly background, so a per-batch F1
collapses toward zero even for a strong model.

Data is split at the **source-image level before patching**, so
overlapping patches from one image can never straddle the train/val/test
boundary.

## API

All endpoints are documented interactively at `/docs` when the backend
is running, and in the [API reference](docs/source/reference/backend-api.md).

`POST /infer` runs segmentation and landmark detection. `POST /explain`
returns a saliency heatmap. `POST /feedback` flags a prediction with an
optional corrected mask. `/stats` and `/monitoring` back the dashboard.
`/auth` and `/users` handle registration, login, and administration.
`GET /health` is the only unauthenticated route — orchestrators need to
probe it without a credential.

Three credential types resolve to one identity: session cookie, JWT
bearer token, and `X-API-Key`. API keys are verified in constant time
via an indexed SHA-256 lookup followed by a single bcrypt check, so
verification cost does not grow with user count. Details in the
[security model](docs/source/explanation/security-model.md).

## Testing

```bash
uv run pytest                    # backend + cv-pipeline
uv run ruff check . && uv run ruff format --check .
```

53 test files — 11 for `cv-pipeline`, 29 for the backend, 11 for the
frontend, plus Airflow helper tests. CI enforces an 85% coverage floor
on `cv_pipeline` and `api`; a PR cannot merge below it.

## Deployment

The same images run in three places: locally via Compose, on-premise as
a Portainer stack, and in Azure on Container Apps with Azure ML for
training and scoring.

Merges to `main` build images, scan them with Trivy, publish to GHCR,
and roll out with a smoke-test gate. Cloud rollout used blue-green
revisions — a new revision starts at zero traffic and only takes a
split after passing health checks.

> **Note on environments.** The Azure and on-premise environments were
> provisioned for a university project and have been decommissioned.
> Their definitions are preserved in `infra/` as the production
> deployment layer, and the cloud deploy jobs in CI are gated behind an
> `ENABLE_DEPLOY` variable so they skip cleanly. **The local Compose
> stack is the reproducible path** — a clean clone to a running,
> instrumented stack in one command.

## Documentation

The Sphinx site covers tutorials, how-to guides, the API reference, and
design rationale, with API docs generated from source docstrings.

- [Quickstart](docs/source/tutorials/quickstart.md) — first inference in
  five minutes
- [Pipeline contract](docs/source/reference/pipeline-contract.md) — the
  formal package and API specification
- [Architecture diagrams](docs/architecture.md)
- [Contributing](CONTRIBUTING.md) — conventions and CI checks

## Repository layout

```
apps/
  backend/         FastAPI service — auth, routers, services, metrics
  frontend/        Next.js researcher UI
packages/
  cv-pipeline/     Installable package: infer, train, CLI, weights
infra/
  local/           Docker Compose stack (backend, frontend, db, prometheus)
  airflow/         6 DAGs, Azure ML job code, promotion gate
  cloud/           Azure ML scoring endpoint and training environment
  server/          Portainer stack definition
  monitoring/      Prometheus image with env-rendered scrape config
scripts/azure/     Data staging, environment registration, endpoint deploy
docs/              Architecture diagrams + Sphinx source
```
