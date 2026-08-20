# Architecture

:::{note}
**Explanation** pages discuss concepts and design decisions. If you
want to do something specific, see [How-to](../how-to/index). If you
want the formal spec, see {doc}`../reference/pipeline-contract`.
:::

Visual diagrams for the system, the deployment topology, and the MLOps
retraining loop live in `docs/architecture.md`, rendered as Mermaid on
GitHub.

## Three delivery forms, one pipeline

The system exposes inference three ways, but there is only one
inference code path:

```
+--------------+   +--------------+   +--------------+
|   CLI        |   |   FastAPI    |   |  Azure ML    |
| cv-pipeline  |   |  backend     |   |  scoring     |
|   infer      |   |  /infer      |   |  endpoint    |
+------+-------+   +------+-------+   +------+-------+
       |                  |                  |
       +------------------+------------------+
                          |
                          v
                +-------------------+
                |   cv_pipeline     |
                |    .infer()       |
                +-------------------+
```

The CLI, the API, and the Azure ML scoring script
(`infra/cloud/endpoint/score.py`) all call the same
`cv_pipeline.infer()` with the same arguments. **There is no
duplicated inference code.**

This matters because:

- One test suite validates all three paths.
- Bug fixes propagate automatically.
- The pipeline version string in responses comes from one source
  (`cv_pipeline.__version__`), so a client can cross-reference.

### Local vs. cloud serving

The backend resolves a `serving_mode` at startup — either `local` or
`azure_ml`. In `local` mode inference runs in-process through the
packaged `cv_pipeline`. In `azure_ml` mode the backend delegates to a
managed scoring endpoint via `api.services.endpoint_client`, and
`/health` reports which mode is active.

Both modes return the same response schema, so a client cannot tell
them apart from the payload. That is deliberate: the serving topology
is an operational decision, not part of the API contract.

## Why FastAPI

FastAPI over Flask or Django-REST, for three reasons:

1. **Native async support.** Long-running inference runs in a
   threadpool while the event loop continues serving `/health` and
   other concurrent requests.
2. **Automatic OpenAPI.** `/docs` is generated from Pydantic response
   models — no hand-written schema to drift.
3. **Pydantic everywhere.** Request validation, response
   serialisation, and error envelopes all flow through one type
   system, giving a single source of truth for the API contract
   ({doc}`../reference/pipeline-contract` §4).

## Why U-Net for segmentation

The NPEC brief targets root tissue segmentation on lab-taken plates —
high resolution, controlled lighting, binary foreground versus
background. U-Net's symmetric encoder-decoder with skip connections is
the textbook match:

- Pixel-level precision, which landmark extraction depends on.
- Small enough for a consumer GPU (batch size 1, ~180 MB weights).
- Well-studied for biomedical imagery, so improvement work has plenty
  of priors to draw on.

Alternatives considered and rejected:

- **Mask R-CNN** — adds instance segmentation the problem doesn't need
  (one plate is one connected root system).
- **SAM (Segment Anything)** — foundation model, too heavy for
  on-premise serving, licence friction.

## Why patch-based inference

Whole-image inference on a HADES plate (up to 8192×8192) would exhaust
GPU memory. The image is tiled into 1024×1024 patches at 50% overlap,
the model runs on each, and the probability maps are stitched back
together.

Overlap is required because root tissue near a patch edge would
otherwise show a discontinuity where adjacent patches disagree. At 50%
overlap each output pixel is covered by 2–4 patches, whose
probabilities are averaged before thresholding.

The trade-off is 2–4× the FLOPs of naive tiling in exchange for
visually seamless masks. Gaussian-weighted overlap blending would
smooth this further and is the obvious next refinement.

## The frontend

A Next.js 16 / React 19 application serving the NPEC researcher UI:
upload a plate image, review the predicted mask, flag the prediction as
good or bad.

It is a thin client. It POSTs to `/infer` and renders the returned
`InferenceResult` — a base64-encoded PNG mask plus landmark
coordinates with confidence scores. Feedback submitted from the review
UI is stored by the backend and becomes training data for the
retraining loop, which is what closes the MLOps cycle from production
use back to model improvement.

Routes are `/` (upload and inference), `/login`, and `/dashboard`. The
dashboard also renders operational metrics read server-side from
Prometheus; the address comes from `PROMETHEUS_URL`, which is never
exposed to the browser. If it is unset, the dashboard shows a "not
configured" note and everything else keeps working.

## Containerisation

`docker compose up` in `infra/local/` brings up four services on a
shared network:

- **backend** (FastAPI, port 8000) — inference service
- **frontend** (Next.js, port 3000) — researcher UI
- **db** (Postgres 16, port 5432) — predictions, feedback, users
- **prometheus** (port 9090) — scrapes the backend's `/metrics`

Database tables are created by Alembic migrations and populated by a
seed script on first startup. The `predictions` table is written on
every successful `/infer` call.

Services are health-checked via `/health` (backend) and `pg_isready`
(db). The frontend polls `/health` on load and shows a red/green
indicator so users know when the stack is up.

## Deployment targets

The same images run in three places.

**Local** — `infra/local/docker-compose.yml`, images built from source.
This is the reproducible path: a clean clone to a running stack in one
command.

**On-premise** — a Portainer stack on a shared GPU server, defined by
`infra/server/docker-compose.portainer.yml`. Images are built by GitHub
Actions and pulled from GHCR; the compose file in git is the source of
truth, so structural changes deploy without manual Portainer edits.

**Cloud** — Azure Container Apps for backend and frontend, with
Azure ML for training and scoring. Deployment was automated through
`cd.yml` via `az containerapp update` on merge to `main`.

:::{note}
The Azure and on-premise environments were provisioned for a
university project and have since been decommissioned. Their
definitions are preserved here as the production deployment layer; the
local stack is the reproducible path.
:::

## CI/CD

Pull requests trigger linting, the test suite, and a docs build. Merges
to `main` build container images, scan them with Trivy, publish to
GHCR, and — when a deployment target is configured — roll out to
on-premise and cloud with a smoke-test gate.

Rollout used a blue-green strategy: a new revision is created at 0%
traffic, health-checked, and only then given a traffic split. A failing
smoke test leaves the previous revision serving.

## Monitoring and the retraining loop

The backend exposes Prometheus metrics at `/metrics` via
`prometheus-fastapi-instrumentator`, and runs a rolling-confidence
drift detector (`api.services.drift_detector`) that compares recent
prediction confidence against a baseline window.

Retraining is orchestrated by Airflow DAGs in `infra/airflow/dags/`:
preprocessing (full and incremental), hyperparameter tuning, and a
champion-challenger promotion gate that scores a candidate model
against the currently serving one on a held-out smoke asset before
deciding whether to promote it.

The loop closes through feedback. Corrections submitted in the UI land
in the `feedback` table; when accumulated feedback crosses a configured
threshold, `feedback_retrain_trigger` fires the retraining path, and a
new model is registered only if it clears the evaluation gate.
