# Preserved training log — hades-unet v18

Azure ML job output from the weekly `data_pipeline` DAG run on 2026-08-10.
Kept here because the workspace that produced it is university-owned and not
publicly reachable; this is the durable record behind the figures quoted in
the README's "Models and provenance" section.

Subscription id, resource group, workspace name and Azure response headers
have been replaced with placeholders. Metrics, hyperparameters, dataset sizes
and the registered model version are unmodified.

---

```
2026-08-10 00:01:04,379 INFO azureml.mlflow._internal.utils: Parsing tracking uri /mlflow/v1.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>
2026-08-10 00:01:04,379 INFO azureml.mlflow._internal.utils: Tracking uri /mlflow/v1.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace> has sub id <subscription-id>, resource group <resource-group>, and workspace <workspace>
2026-08-10 00:01:04,389 INFO azureml.mlflow._common._cloud.cloud: Fetched cloud name from environment variable AZUREML_CURRENT_CLOUD
2026-08-10 00:01:05,448 INFO __main__: Starting training on Azure ML cluster.
2026-08-10 00:01:05,448 INFO __main__:   train-dir:  /tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_train_data
2026-08-10 00:01:05,448 INFO __main__:   val-dir:    /tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_val_data
2026-08-10 00:01:05,448 INFO __main__:   test-dir:   /tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_test_data
2026-08-10 00:01:05,448 INFO __main__:   output-dir: outputs
2026-08-10 00:01:06,838 INFO cv_pipeline.train: Starting training run '20260810-000106' — epochs=50, batch_size=16, lr=0.0003929, weight_decay=0.0001, device=cuda.
2026-08-10 00:26:46,068 INFO cv_pipeline.train: Empty-patch balancing: 33512 root + 25134 empty kept (of 111046 empty available), ratio=0.75.
2026-08-10 00:26:46,222 INFO cv_pipeline.train: Dataset loaded: 58646 pairs from '/tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_train_data' (augment=True).
2026-08-10 00:26:54,525 INFO cv_pipeline.train: Dataset loaded: 40870 pairs from '/tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_val_data' (augment=False).
2026-08-10 00:26:54,529 INFO cv_pipeline.train: Data loaded — 58646 training pairs, 40870 validation pairs.
2026-08-10 00:26:55,010 INFO httpx: HTTP Request: HEAD https://huggingface.co/smp-hub/resnet34.imagenet/resolve/7a57b34f723329ff020b3f8bc41771163c519d0c/config.json "HTTP/1.1 307 Temporary Redirect"
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-08-10 00:26:55,011 WARNING huggingface_hub.utils._http: Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-08-10 00:26:55,120 INFO httpx: HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/smp-hub/resnet34.imagenet/7a57b34f723329ff020b3f8bc41771163c519d0c/config.json "HTTP/1.1 200 OK"
2026-08-10 00:26:55,234 INFO httpx: HTTP Request: GET https://huggingface.co/api/resolve-cache/models/smp-hub/resnet34.imagenet/7a57b34f723329ff020b3f8bc41771163c519d0c/config.json "HTTP/1.1 200 OK"
2026-08-10 00:26:55,342 INFO httpx: HTTP Request: HEAD https://huggingface.co/smp-hub/resnet34.imagenet/resolve/7a57b34f723329ff020b3f8bc41771163c519d0c/model.safetensors "HTTP/1.1 302 Found"
2026-08-10 00:26:55,452 INFO httpx: HTTP Request: GET https://huggingface.co/api/models/smp-hub/resnet34.imagenet/xet-read-token/7a57b34f723329ff020b3f8bc41771163c519d0c "HTTP/1.1 200 OK"
2026-08-10 00:26:58,215 INFO cv_pipeline.train: Model created — 24,430,097 parameters.
2026-08-10 00:40:48,500 INFO cv_pipeline.train: Epoch 1/50 — loss=0.1420, val_f1=0.8228, val_iou=0.6989, lr=3.93e-04 (828.6s)
2026-08-10 00:40:49,072 INFO cv_pipeline.train: New best model at epoch 1 — val_f1=0.8228.
2026-08-10 00:45:08,120 INFO cv_pipeline.train: Epoch 2/50 — loss=0.1059, val_f1=0.8336, val_iou=0.7146, lr=3.91e-04 (258.5s)
2026-08-10 00:45:08,572 INFO cv_pipeline.train: New best model at epoch 2 — val_f1=0.8336.
2026-08-10 00:49:31,789 INFO cv_pipeline.train: Epoch 3/50 — loss=0.1031, val_f1=0.8305, val_iou=0.7102, lr=3.89e-04 (262.4s)
2026-08-10 00:54:01,709 INFO cv_pipeline.train: Epoch 4/50 — loss=0.0998, val_f1=0.8432, val_iou=0.7290, lr=3.87e-04 (269.3s)
2026-08-10 00:54:02,072 INFO cv_pipeline.train: New best model at epoch 4 — val_f1=0.8432.
2026-08-10 00:58:24,628 INFO cv_pipeline.train: Epoch 5/50 — loss=0.0986, val_f1=0.8416, val_iou=0.7265, lr=3.83e-04 (261.7s)
2026-08-10 01:02:53,620 INFO cv_pipeline.train: Epoch 6/50 — loss=0.0973, val_f1=0.8408, val_iou=0.7253, lr=3.79e-04 (268.4s)
2026-08-10 01:07:18,789 INFO cv_pipeline.train: Epoch 7/50 — loss=0.0965, val_f1=0.8462, val_iou=0.7334, lr=3.74e-04 (264.4s)
2026-08-10 01:07:19,267 INFO cv_pipeline.train: New best model at epoch 7 — val_f1=0.8462.
2026-08-10 01:11:44,452 INFO cv_pipeline.train: Epoch 8/50 — loss=0.0960, val_f1=0.8447, val_iou=0.7312, lr=3.69e-04 (264.6s)
2026-08-10 01:16:09,694 INFO cv_pipeline.train: Epoch 9/50 — loss=0.0949, val_f1=0.8379, val_iou=0.7210, lr=3.62e-04 (264.4s)
2026-08-10 01:20:35,644 INFO cv_pipeline.train: Epoch 10/50 — loss=0.0939, val_f1=0.8431, val_iou=0.7287, lr=3.55e-04 (265.4s)
2026-08-10 01:25:01,791 INFO cv_pipeline.train: Epoch 11/50 — loss=0.0939, val_f1=0.8418, val_iou=0.7267, lr=3.48e-04 (265.3s)
2026-08-10 01:29:21,823 INFO cv_pipeline.train: Epoch 12/50 — loss=0.0931, val_f1=0.8431, val_iou=0.7288, lr=3.40e-04 (259.4s)
2026-08-10 01:33:41,638 INFO cv_pipeline.train: Epoch 13/50 — loss=0.0929, val_f1=0.8430, val_iou=0.7286, lr=3.31e-04 (259.0s)
2026-08-10 01:38:10,985 INFO cv_pipeline.train: Epoch 14/50 — loss=0.0921, val_f1=0.8494, val_iou=0.7383, lr=3.22e-04 (268.8s)
2026-08-10 01:38:11,774 INFO cv_pipeline.train: New best model at epoch 14 — val_f1=0.8494.
2026-08-10 01:42:36,595 INFO cv_pipeline.train: Epoch 15/50 — loss=0.0915, val_f1=0.8472, val_iou=0.7349, lr=3.12e-04 (264.0s)
2026-08-10 01:47:02,824 INFO cv_pipeline.train: Epoch 16/50 — loss=0.0915, val_f1=0.8465, val_iou=0.7338, lr=3.02e-04 (263.9s)
2026-08-10 01:51:26,953 INFO cv_pipeline.train: Epoch 17/50 — loss=0.0913, val_f1=0.8411, val_iou=0.7258, lr=2.91e-04 (263.3s)
2026-08-10 01:55:50,982 INFO cv_pipeline.train: Epoch 18/50 — loss=0.0903, val_f1=0.8466, val_iou=0.7340, lr=2.80e-04 (263.4s)
2026-08-10 02:00:15,813 INFO cv_pipeline.train: Epoch 19/50 — loss=0.0902, val_f1=0.8503, val_iou=0.7397, lr=2.69e-04 (263.9s)
2026-08-10 02:00:17,174 INFO cv_pipeline.train: New best model at epoch 19 — val_f1=0.8503.
2026-08-10 02:04:44,696 INFO cv_pipeline.train: Epoch 20/50 — loss=0.0901, val_f1=0.8490, val_iou=0.7376, lr=2.58e-04 (266.9s)
2026-08-10 02:09:13,889 INFO cv_pipeline.train: Epoch 21/50 — loss=0.0897, val_f1=0.8470, val_iou=0.7346, lr=2.46e-04 (268.5s)
2026-08-10 02:13:41,495 INFO cv_pipeline.train: Epoch 22/50 — loss=0.0892, val_f1=0.8499, val_iou=0.7389, lr=2.34e-04 (267.0s)
2026-08-10 02:18:09,957 INFO cv_pipeline.train: Epoch 23/50 — loss=0.0889, val_f1=0.8440, val_iou=0.7302, lr=2.22e-04 (267.7s)
2026-08-10 02:22:38,818 INFO cv_pipeline.train: Epoch 24/50 — loss=0.0885, val_f1=0.8413, val_iou=0.7261, lr=2.09e-04 (268.3s)
2026-08-10 02:27:07,152 INFO cv_pipeline.train: Epoch 25/50 — loss=0.0880, val_f1=0.8445, val_iou=0.7308, lr=1.97e-04 (267.7s)
2026-08-10 02:31:36,017 INFO cv_pipeline.train: Epoch 26/50 — loss=0.0879, val_f1=0.8487, val_iou=0.7372, lr=1.85e-04 (268.4s)
2026-08-10 02:36:05,712 INFO cv_pipeline.train: Epoch 27/50 — loss=0.0873, val_f1=0.8460, val_iou=0.7331, lr=1.72e-04 (268.6s)
2026-08-10 02:40:35,937 INFO cv_pipeline.train: Epoch 28/50 — loss=0.0872, val_f1=0.8524, val_iou=0.7428, lr=1.60e-04 (269.6s)
2026-08-10 02:40:36,277 INFO cv_pipeline.train: New best model at epoch 28 — val_f1=0.8524.
2026-08-10 02:45:02,515 INFO cv_pipeline.train: Epoch 29/50 — loss=0.0865, val_f1=0.8506, val_iou=0.7400, lr=1.48e-04 (265.5s)
2026-08-10 02:49:29,102 INFO cv_pipeline.train: Epoch 30/50 — loss=0.0862, val_f1=0.8508, val_iou=0.7403, lr=1.36e-04 (266.0s)
2026-08-10 02:53:50,704 INFO cv_pipeline.train: Epoch 31/50 — loss=0.0859, val_f1=0.8463, val_iou=0.7335, lr=1.25e-04 (260.8s)
2026-08-10 02:58:11,330 INFO cv_pipeline.train: Epoch 32/50 — loss=0.0856, val_f1=0.8516, val_iou=0.7416, lr=1.14e-04 (260.1s)
2026-08-10 03:02:31,952 INFO cv_pipeline.train: Epoch 33/50 — loss=0.0851, val_f1=0.8507, val_iou=0.7401, lr=1.03e-04 (260.0s)
2026-08-10 03:07:01,533 INFO cv_pipeline.train: Epoch 34/50 — loss=0.0848, val_f1=0.8502, val_iou=0.7395, lr=9.20e-05 (268.8s)
2026-08-10 03:11:27,220 INFO cv_pipeline.train: Epoch 35/50 — loss=0.0843, val_f1=0.8488, val_iou=0.7373, lr=8.18e-05 (265.1s)
2026-08-10 03:15:53,580 INFO cv_pipeline.train: Epoch 36/50 — loss=0.0840, val_f1=0.8517, val_iou=0.7417, lr=7.20e-05 (265.8s)
2026-08-10 03:20:17,966 INFO cv_pipeline.train: Epoch 37/50 — loss=0.0838, val_f1=0.8493, val_iou=0.7381, lr=6.28e-05 (263.8s)
2026-08-10 03:24:47,877 INFO cv_pipeline.train: Epoch 38/50 — loss=0.0833, val_f1=0.8490, val_iou=0.7377, lr=5.41e-05 (269.3s)
2026-08-10 03:29:16,990 INFO cv_pipeline.train: Epoch 39/50 — loss=0.0832, val_f1=0.8502, val_iou=0.7394, lr=4.60e-05 (268.6s)
2026-08-10 03:33:43,545 INFO cv_pipeline.train: Epoch 40/50 — loss=0.0829, val_f1=0.8495, val_iou=0.7384, lr=3.84e-05 (265.6s)
2026-08-10 03:38:08,447 INFO cv_pipeline.train: Epoch 41/50 — loss=0.0826, val_f1=0.8499, val_iou=0.7390, lr=3.15e-05 (264.4s)
2026-08-10 03:42:34,438 INFO cv_pipeline.train: Epoch 42/50 — loss=0.0825, val_f1=0.8507, val_iou=0.7402, lr=2.52e-05 (265.5s)
2026-08-10 03:46:54,087 INFO cv_pipeline.train: Epoch 43/50 — loss=0.0824, val_f1=0.8502, val_iou=0.7395, lr=1.96e-05 (259.0s)
2026-08-10 03:46:54,087 INFO cv_pipeline.train: Early stopping at epoch 43 — no val_f1 improvement for 15 epochs (best=0.8524).
2026-08-10 03:46:54,297 INFO cv_pipeline.train: Best checkpoint saved to 'outputs/best_model.pth'.
2026-08-10 03:46:54,298 INFO cv_pipeline.train: Run metrics saved to 'outputs/run_metrics.json'.
2026-08-10 03:46:54,299 INFO cv_pipeline.train: Training complete — best val_f1=0.8524 at epoch 28.
2026-08-10 03:46:55,185 INFO __main__: Training complete — best_val_f1=0.8524 at epoch 28.
2026-08-10 03:46:55,185 INFO __main__: Evaluating best checkpoint on test set: /tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_test_data
2026-08-10 03:47:00,576 INFO cv_pipeline.train: Dataset loaded: 20512 pairs from '/tmp/azureml/cr/j/0829d44ea33a443f83c4b7d79609fa36/cap/data-capability/wd/INPUT_test_data' (augment=False).
2026-08-10 03:49:15,465 INFO __main__: Test evaluation — test_f1=0.8371, test_iou=0.7199.
2026-08-10 03:49:16,230 INFO __main__: test_f1 0.8371 >= threshold 0.7500 — registering model.
2026-08-10 03:49:16,484 INFO azureml.mlflow._store.artifact.utils: Parsing artifact uri azureml://westeurope.api.azureml.ms/mlflow/v2.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>/experiments/cd50bb05-30ed-4806-b728-12c3d2243868/runs/clever_needle_1grscjk86f/artifacts
2026-08-10 03:49:16,484 INFO azureml.mlflow._store.artifact.utils: Artifact uri azureml://westeurope.api.azureml.ms/mlflow/v2.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>/experiments/cd50bb05-30ed-4806-b728-12c3d2243868/runs/clever_needle_1grscjk86f/artifacts info: {'sub-id': '<subscription-id>', 'res-grp': '<resource-group>', 'ws-name': '<workspace>', 'experiment': 'cd50bb05-30ed-4806-b728-12c3d2243868', 'runid': 'clever_needle_1grscjk86f'}
2026-08-10 03:49:16,486 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://westeurope.api.azureml.ms/history/v1.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>/experiments/cd50bb05-30ed-4806-b728-12c3d2243868/runs/clever_needle_1grscjk86f/artifacts/batch/metadata'
Request method: 'POST'
Request headers:
    'Content-Type': 'application/json'
    'Accept': 'application/json'
    'Content-Length': '45'
    'x-ms-<redacted>': 'REDACTED'
    'User-Agent': 'azsdk-python-mgmt-machinelearningservices/0.1.0 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'Authorization': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:16,766 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 200
Response headers:
    'Date': 'Mon, 10 Aug 2026 03:57:39 GMT'
    'Content-Type': 'application/json; charset=utf-8'
    'Transfer-Encoding': 'chunked'
    'Connection': 'keep-alive'
    'Vary': 'REDACTED'
    'Request-Context': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'mise-correlation-id': 'REDACTED'
    'Strict-Transport-Security': 'REDACTED'
    'X-Content-Type-Options': 'REDACTED'
    'azureml-served-by-cluster': 'REDACTED'
    'x-request-time': 'REDACTED'
    'Content-Encoding': 'REDACTED'
2026-08-10 03:49:16,774 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:16,953 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:39 GMT'
2026-08-10 03:49:16,956 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,043 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:39 GMT'
2026-08-10 03:49:17,046 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,144 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:39 GMT'
2026-08-10 03:49:17,146 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,244 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:39 GMT'
2026-08-10 03:49:17,246 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,346 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:39 GMT'
2026-08-10 03:49:17,347 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,472 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:17,473 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,644 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:17,646 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,734 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:17,736 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,855 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:17,857 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:17,971 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:17,972 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,120 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:18,122 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,210 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:18,211 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,317 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:40 GMT'
2026-08-10 03:49:18,318 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,414 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:18,416 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,505 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:18,507 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,618 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:18,620 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,711 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:18,712 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:18,843 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:18,845 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,042 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:19,043 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,153 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:19,155 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,274 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:19,276 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,376 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:41 GMT'
2026-08-10 03:49:19,377 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '4194304'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,480 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:42 GMT'
2026-08-10 03:49:19,483 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&blockid=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '1413268'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/octet-stream'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,521 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:42 GMT'
2026-08-10 03:49:19,522 INFO azure.core.pipeline.policies.http_logging_policy: Request URL: 'https://staswegend46479454361583.blob.core.windows.net/4fdce553-7c35-4ba7-a26f-80e77b6b3975-azureml/ExperimentRun/dcid.clever_needle_1grscjk86f/model/best_model.pth?comp=REDACTED&sv=REDACTED&sr=REDACTED&sig=REDACTED&skoid=REDACTED&sktid=REDACTED&skt=REDACTED&ske=REDACTED&sks=REDACTED&skv=REDACTED&st=REDACTED&se=REDACTED&sp=REDACTED'
Request method: 'PUT'
Request headers:
    'Content-Length': '2006'
    'If-None-Match': '*'
    'x-ms-<redacted>': 'REDACTED'
    'Content-Type': 'application/xml'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.27.1 Python/3.11.14 (Linux-5.15.0-185-generic-x86_64-with-glibc2.35)'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
A body is sent with the request
2026-08-10 03:49:19,536 INFO azure.core.pipeline.policies.http_logging_policy: Response status: 201
Response headers:
    'Content-Length': '0'
    'Last-Modified': 'Mon, 10 Aug 2026 03:57:42 GMT'
    'ETag': '"0x8DEF69387871BCA"'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'x-ms-content-crc64': 'REDACTED'
    'x-ms-<redacted>': 'REDACTED'
    'Date': 'Mon, 10 Aug 2026 03:57:42 GMT'
Registered model 'hades-unet' already exists. Creating a new version of this model...
2026/08/10 03:49:21 INFO mlflow.store.model_registry.abstract_store: Waiting up to 300 seconds for model version to finish creation. Model name: hades-unet, version 18
Created version '18' of model 'hades-unet'.
2026-08-10 03:49:21,775 INFO __main__: Model registered as 'hades-unet'.
🏃 View run airflow-weekly-training at: https://westeurope.api.azureml.ms/mlflow/v2.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>/#/experiments/cd50bb05-30ed-4806-b728-12c3d2243868/runs/clever_needle_1grscjk86f
🧪 View experiment at: https://westeurope.api.azureml.ms/mlflow/v2.0/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>/#/experiments/cd50bb05-30ed-4806-b728-12c3d2243868
```
