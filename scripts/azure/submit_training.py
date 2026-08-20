"""Submit a single training job to Azure ML by hand.

The supported path is the ``data_pipeline`` Airflow DAG, which resolves the
latest registered environment and data-asset versions before submitting. This
script is the manual escape hatch: it pins an environment version and installs
the wheel at job start instead. Prefer the DAG unless you specifically need a
one-off run.

Job assets (``cloud_train.py`` and the wheel) live in
``infra/cloud/training_jobs/``, which must stay in sync with
``infra/airflow/training_code/cloud_train.py`` -- the two drifted once before,
and the stale copy computed test F1 per batch rather than over the dataset.

1. Build the cv-pipeline wheel:
     cd packages/cv-pipeline && uv build
2. Copy the .whl into infra/cloud/training_jobs/ next to cloud_train.py.

Usage:
    python scripts/azure/submit_training.py
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from azure.ai.ml import Input, MLClient, command
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse arguments for job submission."""
    parser = argparse.ArgumentParser(description="Submit training job to Azure ML.")
    parser.add_argument(
        "--data-version",
        type=str,
        required=True,
        help="Version of hades-train and hades-val data assets.",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--run-name", type=str, default=None)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument(
        "--min-f1",
        type=float,
        default=0.75,
        help="Minimum val F1 to register model. Default 0.75.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="hades-unet",
        help="Name for the registered model in Azure ML.",
    )
    return parser.parse_args()


def main() -> None:
    """Build and submit the training command job."""
    load_dotenv()
    args = parse_args()

    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_WORKSPACE_NAME"],
    )
    logger.info("Connected to workspace: %s", ml_client.workspace_name)

    # Job assets live in infra/cloud/training_jobs, not beside this script.
    # This resolved to scripts/training_jobs before, which does not exist, so
    # the wheel glob below always came back empty and the script exited early.
    repo_root = Path(__file__).resolve().parents[2]
    script_dir = repo_root / "infra" / "cloud" / "training_jobs"
    wheels = list(script_dir.glob("cv_pipeline-*.whl"))
    if not wheels:
        logger.error(
            "No cv_pipeline wheel found in %s. "
            "Run 'uv build' in packages/cv-pipeline and copy the .whl here.",
            script_dir,
        )
        return
    wheel_name = wheels[0].name
    logger.info("Using wheel: %s", wheel_name)

    # Build the command string
    run_name_arg = f"--run-name {args.run_name}" if args.run_name else ""

    job = command(
        display_name=f"cv-pipeline-train-v{args.data_version}",
        description="Train U-Net segmentation model on HADES plant images.",
        code=str(script_dir),
        command=(
            f"pip install --no-deps {wheel_name} && "
            "python cloud_train.py "
            "--train-dir ${{inputs.train_data}} "
            "--val-dir ${{inputs.val_data}} "
            "--output-dir ${{outputs.model_output}} "
            f"--epochs {args.epochs} "
            f"--batch-size {args.batch_size} "
            f"--lr {args.lr} "
            f"--device {args.device} "
            f"--min-f1 {args.min_f1} "
            f"--model-name {args.model_name} "
            f"--num-workers {args.num_workers} "
            f"{run_name_arg}"
        ),
        inputs={
            "train_data": Input(
                type=AssetTypes.URI_FOLDER,
                path=f"azureml:hades-train:{args.data_version}",
            ),
            "val_data": Input(
                type=AssetTypes.URI_FOLDER,
                path=f"azureml:hades-val:{args.data_version}",
            ),
        },
        outputs={
            "model_output": {"type": "uri_folder"},
        },
        # Pinned, unlike the DAG which resolves the latest version. Bump this
        # after registering a new training environment or the job runs against
        # a stale image.
        environment="azureml:cv-pipeline-training:4",
        compute="lambda-0",
        resources={"instance_type": "gpu"},
        experiment_name="cv-pipeline-training",
    )

    submitted = ml_client.jobs.create_or_update(job)
    logger.info("Job submitted: %s", submitted.name)
    logger.info("Studio URL: %s", submitted.studio_url)


if __name__ == "__main__":
    main()
