# Architecture

Three views of the system: how a request flows through it, how it is
built and deployed, and how it retrains itself.

Diagrams render as Mermaid on GitHub. For the reasoning behind these
choices — why FastAPI, why U-Net, why patch-based inference — see the
architecture page in the documentation site.

---

## System

Data flow for a single inference request, plus the feedback write-path
that feeds retraining.

```mermaid
flowchart TD
    frontend["Next.js UI (apps/frontend)<br/>Upload · results · feedback · dashboard"]
    auth["Auth layer<br/>session · JWT · X-API-Key"]
    backend["FastAPI service (apps/backend)<br/>/infer · /explain · /feedback · /stats<br/>/monitoring · /users · /auth · /health"]
    model["cv-pipeline (packages/cv-pipeline)<br/>U-Net segmentation & landmark detection"]
    endpoint["Azure ML scoring endpoint<br/>(serving_mode = azure_ml)"]
    db[("Postgres 16<br/>predictions · feedback · users · sessions")]
    prom["Prometheus<br/>scrapes /metrics"]
    drift["Drift detector<br/>rolling confidence"]

    frontend -- "1. POST /infer (image)" --> auth
    auth -- "2. resolve identity" --> backend
    backend -- "3a. in-process (serving_mode = local)" --> model
    backend -. "3b. delegate (serving_mode = azure_ml)" .-> endpoint
    model -- "4. mask & landmarks" --> backend
    backend -- "5. log prediction + user_id" --> db
    backend -- "6. JSON response" --> frontend

    frontend -- "flag / correct prediction" --> backend
    backend -- "write feedback row" --> db

    backend -- "exposes /metrics" --> prom
    db -- "recent confidence" --> drift
    prom -- "queried server-side" --> frontend
```

Both serving modes return the same response schema, so a client cannot
tell them apart from the payload. Anonymous callers are allowed on
`/infer`; the prediction is stored with a null user id.

---

## Deployment

From a merge on `main` to running containers, and the monitoring path.

```mermaid
flowchart LR
    github["GitHub Actions<br/>cd.yml"]
    build["build-and-push<br/>images to GHCR"]
    scan["scan-images<br/>Trivy"]
    ghcr["GHCR<br/>(GitHub Container Registry)"]

    subgraph Local ["Local (reproducible)"]
        compose["docker compose<br/>backend · frontend · db · prometheus"]
    end

    subgraph OnPremise ["On-premise (decommissioned)"]
        portainer["Portainer stack<br/>shared GPU server"]
        smoke["smoke-test<br/>gate"]
    end

    subgraph Cloud ["Azure (decommissioned)"]
        aca["Azure Container Apps<br/>blue-green revisions"]
        aml["Azure ML<br/>training · registry · endpoint"]
    end

    github --> build --> scan
    build --> ghcr
    github -- "deploy-portainer" --> portainer
    portainer --> smoke
    github -- "deploy-azure<br/>(az containerapp update)" --> aca

    portainer -. "pulls" .-> ghcr
    aca -. "pulls" .-> ghcr
    compose -. "builds from source" .-> compose

    subgraph Monitoring ["Monitoring"]
        metrics["/metrics<br/>(Prometheus Instrumentator)"]
        promsvc["Prometheus service<br/>scrape + retain"]
        azuremon["Azure Monitor<br/><i>(planned)</i>"]
    end

    compose -. "exposes" .-> metrics
    portainer -. "exposes" .-> metrics
    aca -. "exposes" .-> metrics
    metrics --> promsvc
    promsvc -. "ingested by<br/>(planned)" .-> azuremon

    classDef planned fill:#f1f3f5,stroke:#adb5bd,stroke-dasharray: 5 5
    classDef gone fill:#f8f9fa,stroke:#ced4da,stroke-dasharray: 3 3
    class azuremon planned
    class portainer,smoke,aca,aml gone
```

The same four services run everywhere: backend, frontend, Postgres, and
Prometheus. Only the orchestrator changes — Compose locally, a Portainer
stack on-premise, Container Apps in cloud.

Rollout to cloud used blue-green revisions: a new revision is created at
zero traffic, health-checked, and only then given a traffic split. On
on-premise, `smoke-test` runs against the deployed stack and a failure
leaves the previous containers serving.

:::{note}
The on-premise and Azure environments were provisioned for a university
project and have been decommissioned. Their definitions are preserved
in `infra/` as the production deployment layer; the local Compose stack
is the reproducible path.
:::

---

## MLOps retraining loop

The loop closes: user corrections become training data, a candidate is
trained and evaluated, and it only reaches production after beating the
model currently serving.

```mermaid
flowchart TD
    users["Researchers<br/>flag / relabel predictions"]
    fb[("feedback table<br/>Postgres")]
    trigger["feedback_retrain_trigger<br/>daily · threshold check"]
    bridge["feedback_to_raw_upload<br/>stage images + masks"]
    asset["hades-feedback<br/>data asset"]
    inc["preprocessing_incremental<br/>merge · test set frozen"]
    full["preprocessing_pipeline<br/>clean-slate split"]
    hp["hyperparameter_tuning<br/>Azure ML sweep (manual)"]
    hpvar["Airflow Variable<br/>hades_best_hparams"]
    train["data_pipeline<br/>weekly · train + evaluate"]
    gate{"meets evaluation<br/>threshold?"}
    registry["Azure ML model registry<br/>hades-unet"]
    promo["promotion<br/>champion vs challenger<br/>on hades-smoke"]
    serve["Scoring endpoint<br/>traffic split"]

    users --> fb
    fb --> trigger
    trigger -- "threshold reached" --> bridge
    bridge --> asset --> inc --> train
    full --> train
    hp --> hpvar -.-> train
    train --> gate
    gate -- "no" --> stop["discard candidate"]
    gate -- "yes" --> registry --> promo
    promo -- "candidate wins" --> serve
    promo -- "champion holds" --> stop
    serve -- "serves predictions" --> users
```

Two triggers drive retraining, whichever comes first: `data_pipeline`
runs weekly on a schedule, and `feedback_retrain_trigger` fires the
feedback bridge once accumulated corrections cross a configured
threshold.

`preprocessing_incremental` keeps the test set frozen while re-splitting
train and validation, so models stay comparable across versions.
`preprocessing_pipeline` is the clean-slate alternative for a fresh
dataset.

Registration is conditional — a candidate enters the registry only if it
clears the evaluation gate on a held-out test set. Promotion is a second,
independent gate: `promotion.py` scores the candidate against the current
champion on the `hades-smoke` asset and only then flips endpoint traffic.

### DAG inventory

| DAG | Schedule | Purpose |
|---|---|---|
| `data_pipeline` | Weekly (Mon 02:00) | Train, evaluate, conditionally register |
| `preprocessing_pipeline` | Manual / scheduled | Clean-slate preprocessing and split |
| `preprocessing_incremental` | Triggered | Merge new data, frozen test set |
| `hyperparameter_tuning` | Manual | Azure ML sweep, writes winning hparams |
| `feedback_retrain_trigger` | Daily | Fire the bridge on threshold |
| `feedback_to_raw_upload` | Triggered | Feedback to registered data asset |
