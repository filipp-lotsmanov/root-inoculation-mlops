# Add a new model version

When retraining produces a better checkpoint, register it so the CLI
and the API can serve it without code changes.

## Two registries, two purposes

There are deliberately two:

**The Azure ML model registry** holds versions produced by cloud
training. The Airflow DAGs register a candidate there automatically
when it clears the evaluation gate, and the champion-challenger
promotion step in `infra/airflow/dags/promotion.py` decides whether it
takes traffic on the scoring endpoint. Nothing manual is involved —
that path is described in {doc}`../explanation/architecture`.

**The package registry** is a Python dict in
`packages/cv-pipeline/src/cv_pipeline/weights.py` mapping a version
string to a download URL:

```python
REGISTRY: dict[str, str] = {
    "unet-v1": "https://.../unet-v1.pth?download=1",
}
```

This one exists so that the CLI and any local install can fetch weights
without Azure credentials. The package must work standalone — that is
the point of shipping it as an installable library — so it cannot
depend on an Azure ML client at import time.

This page covers the second case: making a checkpoint available to the
package.

## Steps

### 1. Upload the checkpoint

Put the `.pth` somewhere that returns raw binary over HTTPS. Any host
works; the requirement is that the URL serves the file itself, not an
HTML preview page.

```bash
az storage blob upload \
    --account-name <account> \
    --container-name model-weights \
    --name unet-v2.pth \
    --file ./best_model.pth
```

For SharePoint or OneDrive share links, append `&download=1` to force a
direct download.

### 2. Add the entry

```python
REGISTRY: dict[str, str] = {
    "unet-v1": "https://.../unet-v1.pth?download=1",
    "unet-v2": "https://.../unet-v2.pth?download=1",
}
```

Open it as a PR. The dict is import-time typo-checked, which a JSON
file shipped alongside the package would not be.

### 3. Set the default, if needed

If `unet-v2` should be served when no `--version` is passed, put it
first. Python dicts preserve insertion order and the CLI falls back to
`next(iter(REGISTRY))`.

### 4. Test

```bash
uv run cv-pipeline infer --image test.png --output results/ --version unet-v2
```

The weights download on first use and cache in
`~/.cache/cv-pipeline/models/` (override with `CV_PIPELINE_CACHE_DIR`).
Downloads stream in 1 MB chunks and write to a temp file that is
renamed on success, so an interrupted download cannot leave a corrupt
file in the cache. If the host returns HTML instead of binary, the
download fails loudly rather than caching the error page.

:::{note}
The package registry does not verify checksums. Integrity rests on
HTTPS and the binary-content check. Recording the SHA-256 alongside the
URL, and verifying after download, is the natural hardening step:

```bash
sha256sum best_model.pth
```
:::

### 5. Point the backend at it

The API serves whichever version is named by `SERVING_MODEL_VERSION`.
Update that environment variable and restart, then confirm via
`/health`, which reports the loaded `model_version` and the active
`serving_mode`.
