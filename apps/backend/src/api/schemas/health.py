"""Schemas for health endpoint responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health-check payload returned by the backend service.

    Status values:
        - ``"ok"``: model is loaded and the service is ready to serve
          inference requests. This is the value assessors / automation
          checks expect when testing the endpoint.
        - ``"loading"``: the backend is up but the model has not
          finished loading yet. Emitted during the window between
          container start and the lifespan loading the checkpoint.
    """

    status: Literal["ok", "loading"]
    model_loaded: bool
    model_version: str | None = None
    pipeline_version: str
    serving_mode: Literal["local", "azure_ml"] | None = None
    # True only when the GitHub OAuth flow is fully configured. The login page
    # uses this to decide whether to render a sign-in link, so an unconfigured
    # deployment does not offer a button that lands on a 500.
    oauth_enabled: bool = False
    timestamp: datetime
