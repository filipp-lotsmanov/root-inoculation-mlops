# Airflow orchestration

Airflow is the orchestrator for the data and training pipelines. It does
not do the compute — every heavy step is submitted to Azure ML and
monitored from here. That split keeps the DAGs thin and testable, and
keeps GPU work on cluster hardware.

## Contents

- `dags/` — DAG definitions plus two helper modules
- `training_code/` — job entry points submitted to Azure ML compute
  (`cloud_train.py`, `cloud_preprocess.py`,
  `cloud_preprocess_incremental.py`)
- `smoke_code/smoke_eval.py` — champion-vs-challenger scoring job
- `tests/` — unit tests for the helper logic
- `Dockerfile`, `docker-compose.yaml`, `pyproject.toml` — the local
  Airflow stack

## DAG inventory

| DAG | Trigger | What it does |
|---|---|---|
| `data_pipeline` | Weekly, Mon 02:00 | Ingest versioned assets, preprocess, train, evaluate on a held-out test set, register the model if it clears the threshold |
| `preprocessing_pipeline` | Manual / scheduled | Clean-slate preprocessing: patches raw images, produces a fresh train/val/test split, chains into training |
| `preprocessing_incremental` | Triggered by the feedback bridge | Merges new pairs into existing assets while keeping the **test set frozen**, so models stay comparable across versions |
| `hyperparameter_tuning` | Manual | Submits an Azure ML sweep; writes the winning `lr` and `batch_size` to the Airflow Variable `hades_best_hparams` |
| `feedback_retrain_trigger` | Daily | Counts approved and relabelled feedback not yet exported; fires the bridge once the retrain threshold is reached |
| `feedback_to_raw_upload` | Triggered | Assembles images and corrected masks, registers a new `hades-feedback` data asset version, marks rows exported, triggers incremental preprocessing |

Two helper modules sit alongside the DAGs rather than inside them, so
they stay unit-testable and the DAG files remain thin wiring layers:

- `azure_helpers.py` — credential and client factories, threshold
  resolution
- `promotion.py` — the champion-challenger gate: resolve the currently
  serving model and the latest registered candidate, submit the smoke
  evaluation, read the verdict, and on promotion create the deployment,
  health-check it at 0% traffic, then flip the traffic split

## Two retraining triggers

The model retrains on a weekly schedule **or** when enough user feedback
accumulates, whichever comes first. `data_pipeline`'s schedule owns the
first; `feedback_retrain_trigger` owns the second.

The feedback path chains:
`feedback_retrain_trigger` → `feedback_to_raw_upload` →
`preprocessing_incremental` → `data_pipeline`.

## Two independent gates

A new model passes through two checks before it serves traffic:

1. **Conditional registration** — `data_pipeline` registers the
   candidate only if it meets the evaluation criteria on the held-out
   test set.
2. **Promotion** — `promotion.py` scores the candidate against the
   current champion on the `hades-smoke` asset and only then flips
   endpoint traffic. A candidate that registers can still lose here.

## Running locally

```bash
cd infra/airflow
docker compose up -d
```

All three services load `env_file: .env`, so create that file first. It
is not committed and there is no template in this folder — the values it
needs are the Azure and feedback-storage keys listed under
[Configuration](#configuration) below.

The webserver is at <http://localhost:8080>, seeded with an `admin` /
`admin` account by the `airflow-init` service. `dags/`, `logs/`, and
`plugins/` are bind-mounted, so DAG edits appear without a rebuild.

Services: `airflow-postgres` (metadata DB), `airflow-init` (one-shot
migrate and user creation), `airflow-webserver`, `airflow-scheduler`.

:::note
This stack is separate from `infra/local/docker-compose.yml`, which runs
the application. Airflow needs Azure credentials to do anything useful;
the application stack does not.
:::

## Configuration

Credentials resolve from the Airflow connection `azure_ml_conn` (its
Extra JSON), falling back to environment variables when a key is absent.
Managed deployments use the connection; local Docker runs use `.env`.

The Extra holds the service-principal and workspace keys
(`tenant_id`, `client_id`, `client_secret`, `subscription_id`,
`resource_group`, `workspace_name`) plus the feedback storage values
(`FEEDBACK_DB_URL`, `FEEDBACK_BLOB_CONNECTION_STRING`,
`FEEDBACK_BLOB_CONTAINER`) and `RETRAIN_FEEDBACK_THRESHOLD`.

Azure named resources: model `hades-unet`, endpoint
`hades-unet-endpoint`, compute `lambda-0`, smoke asset `hades-smoke`,
training environment `cv-pipeline-training`.

## Tests

```bash
uv run pytest infra/airflow/tests
```

Tests cover the pure helper logic — `compute_traffic_split` and the
feedback export path — rather than DAG execution. Azure SDK imports are
local to each function so the modules import cleanly without
`azure-ai-ml` installed.
