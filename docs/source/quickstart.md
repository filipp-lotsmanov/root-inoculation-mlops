# Quick start: your first inference in 5 minutes

:::{note}
This is a **tutorial**. You will be guided through a complete worked
example with all commands to run and what to expect. If you already
know what you're doing and just need syntax, go to
[How-to guides](../how-to/index).
:::

By the end of this tutorial you will have:

1. Cloned the repo and installed dependencies.
2. Run the CLI on a sample image.
3. Inspected the mask and landmarks output.
4. Called the same pipeline through the HTTP API.

You do not need a GPU. Inference on CPU is slower (about 20 seconds
for a 640x640 image) but works exactly the same.

## Prerequisites

- Python 3.11.9
- [`uv`](https://docs.astral.sh/uv/) 0.5 or newer
- git
- (Optional) Docker Desktop if you want to try the full stack later

## Step 1 - Clone and install

```bash
git clone https://github.com/filipp-lotsmanov/root-inoculation-mlops.git
cd root-inoculation-mlops
uv sync
```

The first `uv sync` downloads PyTorch and takes 2-3 minutes. Subsequent
runs are cached and take under 10 seconds.

## Step 2 - Get the model weights

The trained U-Net checkpoint is not stored in the repo (it's about
93 MB). It is published as a GitHub Release asset and the pipeline
downloads it automatically the first time you run inference, verifying
it against the SHA-256 digest recorded in
`cv_pipeline.weights.REGISTRY`. To trigger the download explicitly:

```python
from cv_pipeline.weights import get_weights
get_weights("unet-v1")
# Saved to ~/.cache/cv-pipeline/models/unet-v1.pth
```

The file is cached under `~/.cache/cv-pipeline/models/` (override
with the `CV_PIPELINE_CACHE_DIR` environment variable). Subsequent
runs reuse the cached file - no re-download.

## Step 3 - Run your first inference

The sample images used in this tutorial ship with the documentation at
`docs/source/_static/sample_plate.png`. Copy it somewhere convenient
or use any `.png`/`.tif` image of your own:

```bash
uv run cv-pipeline infer \
    --image docs/source/_static/sample_plate.png \
    --output results/
```

:::{note}
Step 2 is optional. By default, this command uses the `unet-v1`
model, and if its weights are not already cached they will be
downloaded automatically on first run.
:::

You should see:

```
Inference complete: 0 landmark(s) detected.
  Result: results/sample_plate_result.json
  Mask:   results/sample_plate_mask.png
```

Zero landmarks is the correct, expected result for this input, and it is
not a broken install. The sample plate that ships with these docs is a
web-downscaled copy, and `unet-v1` only resolves roots at the scale it
was trained on. [Why the sample returns an empty
mask](#why-the-sample-returns-an-empty-mask) below measures this and
explains what to feed the pipeline instead. The rest of this tutorial —
output layout, the result schema, the API call — is unaffected.

## Step 4 - Inspect the output

Open `results/sample_plate_mask.png` - it's a black-and-white image
the same size as the input. White pixels mark predicted root tissue.
For this input every pixel is black, for the reason above.

### What the target looks like

Below: an NPEC plant image and the human **ground-truth** annotation for
it. Red traces mark the annotated root tissue. This is the target the
model is trained against, not a prediction from this run — see the note
below the table. The pipeline only segments roots; shoots and seeds are
out of scope for this package.

:::{list-table}
:header-rows: 1
:widths: 50 50

* - Input image
  - Ground-truth root annotation
* - ![Sample NPEC plate - input to the pipeline](../_static/sample_plate.png)
  - ![Human ground-truth root annotation for the sample plate](../_static/sample_mask.png)
:::

:::{note}
The sample files `docs/source/_static/sample_plate.png` and
`docs/source/_static/sample_mask.png` ship with this repository.
The plate image is `train_Alican_244760_im1.png` from the BUas
Y2B_25 dataset; the overlay is the corresponding **ground-truth
root annotation**, drawn by a human — not model output. Both
downscaled from 4202x3006 px to 1500x1073 px for web delivery. Used
with permission of BUas/NPEC for documentation purposes.
:::

### Inspect the result JSON

Open `results/sample_plate_result.json` in any editor. You'll see:

```json
{
  "pipeline_version": "0.1.0",
  "model_version": "unet-v1",
  "timestamp": "2026-04-22T14:03:19+00:00",
  "image_filename": "sample_plate.png",
  "image_width_px": 1500,
  "image_height_px": 1073,
  "mask_b64": "<base64-encoded PNG>",
  "mask_confidence": 0.0,
  "landmark_count": 0,
  "landmarks": [],
  "metadata": {...}
}
```

The `landmarks` array holds detected root tips in pixel coordinates; on
a plate where the model does fire, each entry looks like
`{"id": 0, "x": 1059, "y": 875, "confidence": 0.997}`.

`mask_confidence` is the mean probability over the pixels classified as
root — **not** over the whole image — and is exactly `0.0` when no pixel
clears the threshold, which is the case here. So read it as two
different signals: `0.0` means "found nothing", while a low-but-nonzero
value (below about 0.6) means "found something and is unsure about it".

## Why the sample returns an empty mask

`unet-v1` is scale-sensitive, and the pipeline does not hide it: there
is **no resize step anywhere** in `preprocessing.py` or
`segmentation.py`. An image is cropped to the dish and then cut directly
into 256x256 patches (the checkpoint records `image_size: 256`) at
whatever resolution it arrived at. So the apparent width of a root, in
pixels, inside each patch is decided entirely by the resolution of the
file you hand in.

The Y2B_25 plates were acquired at roughly 4202x3006 px, where a primary
root is a few pixels wide. The sample that ships with these docs was
downscaled 2.8x for web delivery, which shrinks root width proportionally
and takes it below what this checkpoint responds to. It does not degrade
gracefully; it returns nothing at all.

Measured on the committed sample, both figures produced with the same
cached `unet-v1` checkpoint:

| Input | Max probability | Pixels >= 0.5 | Landmarks | `mask_confidence` |
|---|---|---|---|---|
| As shipped, 1500x1073 | 0.0092 | 0.000000 | 0 | 0.0 |
| Resampled to 4202x3006 | 0.99997 | 0.0012 | 5 | 0.9585 |

The model's single most confident pixel in the downscaled image scores
0.0092 — nowhere near the 0.5 threshold. Restore the original pixel
dimensions and the same weights segment the plate and place five root
tips. You can reproduce both rows with only the files in this
repository:

```bash
uv run python -c "
from PIL import Image
Image.open('docs/source/_static/sample_plate.png') \
     .resize((4202, 3006), Image.BICUBIC) \
     .save('plate_native.png')
"
uv run cv-pipeline infer --image plate_native.png --output results_native/
```

:::{important}
Resampling upward restores the **scale** the model expects; it does not
restore the detail the downscale discarded. It is a demonstration that
scale is the operative variable, not a substitute for a real
full-resolution plate.
:::

This repository cannot ship a native-resolution plate. The Y2B_25
dataset is proprietary to BUas/NPEC, and the permission covering these
docs extends to the web-downscaled copy above. To get a real
segmentation, point the CLI at your own plate image at native
acquisition resolution:

```bash
uv run cv-pipeline infer --image /path/to/your_plate.png --output results/
```

The practical rule: feed the pipeline images at the resolution they were
acquired at. Do not pre-downscale to save time — resize is not a
neutral preprocessing step for this model. The 256x256 minimum enforced
in {doc}`error codes <../explanation/error-codes>` is a hard floor on
image dimensions, not a statement that any image above it is
in-distribution.

Making the model scale-invariant (multi-scale training augmentation, or
normalising input resolution inside `preprocessing.py` before patching)
is a known gap rather than a solved problem in this version.

## Step 5 - Call the same code through the API

:::{important}
The API requires a running database. The easiest way to get the
full stack (backend + frontend + Postgres) is Docker Compose. The
seed script runs automatically on first startup and creates default
users from the `API_KEY` and `ADMIN_API_KEY` environment variables.
**You must set these before the first start** - the seed is
idempotent and skipped on subsequent restarts.
:::

### 5.1 Configure environment variables

Copy the env template and fill in the required values:

```bash
cp configs/env/env.example configs/env/.env
```

Edit `configs/env/.env` and set:

```
API_KEY=<32-character-hex-string-of-your-choice>
ADMIN_API_KEY=<another-32-character-hex-string>
POSTGRES_PASSWORD=<any-password-for-the-local-db>
```

To generate keys on Linux/macOS:

```bash
openssl rand -hex 32
```

To generate keys on Windows PowerShell:

```powershell
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
```

### 5.2 Start the full stack

```bash
cd infra/local
docker compose up --build
```

On first startup you should see the backend container run migrations
and then:

```
INFO: Seeded default researcher and admin users.
```

Wait until the health check passes and you see `Uvicorn running on
http://0.0.0.0:8000`. The frontend is available at
<http://localhost:3000> and the API at <http://localhost:8000/docs>.

### 5.3 Make an authenticated request

Open a second terminal from the repo root:

```bash
export API_KEY=$(grep ^API_KEY= configs/env/.env | cut -d= -f2)

curl -X POST http://localhost:8000/infer \
    -H "X-API-Key: $API_KEY" \
    -F "image=@docs/source/_static/sample_plate.png" \
    | python -m json.tool
```

PowerShell equivalent:

```powershell
$env:API_KEY = (Get-Content configs/env/.env | Select-String '^API_KEY=').ToString().Split('=')[1]

curl.exe -X POST http://localhost:8000/infer `
    -H "X-API-Key: $env:API_KEY" `
    -F "image=@docs/source/_static/sample_plate.png" `
    | python -m json.tool
```

The response body is identical to the CLI's `result.json` — including
the empty mask and `landmark_count: 0` for this sample, for the reason
in [Why the sample returns an empty
mask](#why-the-sample-returns-an-empty-mask). That identity is the
point: the API and the CLI share the same pipeline, so there is only one
code path and one set of behaviours to reason about.

To stop the stack, press `Ctrl+C` in the compose terminal or run
`docker compose down` from `infra/local/`. Add `-v` to also wipe
the database volume.

## What next

- Learn to call the API from Python, curl, or the Next.js frontend:
  {doc}`../how-to/call-the-api`
- Understand how error codes work:
  {doc}`../explanation/error-codes`
- Register a new model version:
  {doc}`../how-to/add-a-new-model-version`

## Troubleshooting

**"`ModuleNotFoundError: No module named 'cv_pipeline'`"**
You ran `python` instead of `uv run python`. Everything must go
through `uv run` unless you've activated the venv manually.

**"`MODEL_NOT_READY`"**
The weights download failed or the cache is corrupted. Re-trigger the
download with `from cv_pipeline.weights import get_weights; get_weights("unet-v1")`,
or pass `--version unet-v1` explicitly to re-attempt.

**"`IMAGE_TOO_SMALL`"**
Your image is under 256x256. The pipeline requires at least that
size - see {doc}`../explanation/error-codes` for the full list.

**The mask is entirely black and `landmark_count` is 0**
Expected on the shipped sample, and usually a resolution problem on your
own images. `unet-v1` only resolves roots at native acquisition
resolution (~4202x3006); a downscaled plate returns nothing. See [Why
the sample returns an empty
mask](#why-the-sample-returns-an-empty-mask). Check that you have not
resized the image before passing it in.

**"`UNAUTHORIZED`" even though I set API_KEY**
The seed script ran with different keys than the ones in your current
`.env`. Either clear the users table (`docker compose exec db psql -U
cvuser -d cvdb -c "TRUNCATE users CASCADE;"`) and restart the backend, or
use the keys from when the database was first initialised.
