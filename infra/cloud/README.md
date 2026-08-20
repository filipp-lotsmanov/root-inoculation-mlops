# Cloud deployment (Azure)

Assets for the Azure targets: Container Apps for the web tier, and
Azure ML for training, the model registry, and the managed scoring
endpoint.

:::note
This environment was provisioned for a university project and has been
decommissioned. These definitions are preserved as the production
deployment layer.
:::

## Contents

**`endpoint/`** — the Azure ML managed online endpoint.

- `score.py` — scoring script. Handles `mode="infer"` and
  `mode="explain"`, calling the same `cv_pipeline` code as the CLI and
  the backend.
- `Dockerfile`, `conda.yml` — the inference environment.
- `cv_pipeline-0.1.0-py3-none-any.whl` — the packaged pipeline
  installed into that environment.
- `sample_request.json` — a request body for smoke-testing the
  deployed endpoint.

**`train_environment/`** — the Azure ML training environment.

- `Dockerfile`, `conda.yml` — image definition.
- `env_registration.py` — registers the environment with the workspace.
- `cv_pipeline-0.1.0-py3-none-any.whl` — the pipeline wheel. NOTE: this copy
  differs from the identical wheels in `endpoint/` and `training_jobs/`
  despite carrying the same version string, so training and serving may not
  be running the same build. Rebuild all three from
  `packages/cv-pipeline` before trusting a comparison between them.

**`training_jobs/`** — assets for manual job submission via
`scripts/azure/submit_training.py`.

- `cloud_train.py` — the training job entry point. Must stay identical to
  `infra/airflow/training_code/cloud_train.py`, which is what the DAGs
  upload. The two drifted once: this copy imported a helper that had been
  renamed (so the job failed on import) and averaged test F1 per batch
  rather than over the dataset, which would have produced numbers not
  comparable to the ones in the root README.
- `cv_pipeline-0.1.0-py3-none-any.whl` — installed at job start by the
  manual path. The DAG path does not use it; the wheel is baked into the
  registered Azure ML training environment instead.

The Airflow DAGs are the supported submission path and live in
`infra/airflow/`. They resolve the latest registered environment and data
asset versions; the manual script pins them.

## Deploy ordering: endpoint before backend (required for explain)

The backend Container App and the Azure ML scoring endpoint deploy on
independent schedules. The backend's cloud explain path POSTs
`mode="explain"` and parses the reply as an `ExplanationResult`.

If a new backend revision rolls out **before** the new `score.py` is live
on the endpoint, the endpoint still answers with an `InferenceResult`
shape (no `heatmap_b64`), so every cloud `/explain` returns a hard 500
until the endpoint catches up. The frontend's 502/503/504 handler does
not mask this (it is a clean 500), and `_call_endpoint_explain` raises an
explicit "redeploy the endpoint first" error to make the cause obvious in
logs.

**Therefore, when shipping a change to the explain contract (`score.py`
or the `cv_pipeline` explain code):**

1. Run the **Deploy Endpoint** workflow first and confirm it is live
   (`mode="explain"` returns a heatmap). Use `rebuild_env=true` whenever
   the `cv_pipeline` wheel changed.
2. Only then let the backend Container App revision roll out (merge to
   `main`).
3. Commit the updated sentinel so CD's contract check goes green.

For a backwards-compatible change (the endpoint already supports
`explain`), ordering does not matter and the backend can roll out first.

## Why the endpoint deploys manually

Re-registering the inference environment triggers an ACR image build and
re-provisions the deployment — minutes per run. Doing that on every push
would be wasteful and risky, since it could re-roll a live endpoint
mid-demo. So `deploy-endpoint.yml` is `workflow_dispatch` only, taking
`model_version`, `traffic`, and `rebuild_env` as inputs. It is the only
thing that mutates the live endpoint.

Instead, CD runs `endpoint-contract-check` on every push. It hashes
`score.py`, the conda file, the Dockerfile, and the `cv_pipeline`
sources, compares them against a sentinel recorded at the last deploy,
and emits a warning naming the exact command to run — including whether
`rebuild_env` needs to be true (only `score.py` changed) or false. It
never deploys and never fails CD.

:::note
The sentinel lives at `infra/cloud/endpoint/.deployed-contract.json` and
is written by `scripts/azure/endpoint_contract.py write` after a deploy.
It is not present in this repository, so the check reports "never
deployed" until an endpoint deploy is run and the sentinel committed.
:::
