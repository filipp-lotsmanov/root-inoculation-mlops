# Error codes

Every 4xx/5xx response - from both the CLI and the API - carries a
stable `error_code` alongside the human-readable `message`.
Clients should branch on the code, never on the message text (which
may be rephrased without notice).

Source of truth: {doc}`../reference/pipeline-contract` §5.

## The envelope

Every error response has this shape:

```json
{
  "error_code": "IMAGE_TOO_SMALL",
  "message": "Image 200x200 is below the 256x256 minimum.",
  "pipeline_version": "0.1.0",
  "timestamp": "2026-04-22T14:03:19+00:00",
  "request_id": "c3d4e5-..."
}
```

`request_id` echoes the `X-Request-ID` header and is useful for
cross-referencing server logs.

## Inference codes

These come from `cv_pipeline` validation and apply to `/infer` and
`/explain` alike — both routes share the same `error_code` to HTTP
status mapping.

```{list-table}
:widths: 22 8 40 30
:header-rows: 1

* - `error_code`
  - HTTP
  - When
  - What to do
* - `FILE_TOO_LARGE`
  - 413
  - Upload exceeds 50 MB
  - Downscale before upload; HADES images at 4096x4096 are under the limit
* - `UNSUPPORTED_FILE_TYPE`
  - 422
  - Extension not in `.png/.jpg/.jpeg/.tif/.tiff`
  - Convert the file (`.bmp`, `.webp` not accepted)
* - `UNSUPPORTED_COLOR_MODE`
  - 422
  - Image is CMYK or palette-indexed
  - Re-save as RGB or grayscale
* - `IMAGE_TOO_SMALL`
  - 422
  - Either dimension under 256 px
  - The U-Net will not see enough features at that size
* - `IMAGE_TOO_LARGE`
  - 422
  - Either dimension over 8192 px
  - Even with patch-based inference this overflows practical RAM
* - `CORRUPT_FILE`
  - 422
  - Decoder cannot read the file, or path is not a file
  - Verify the file isn't truncated; recheck the path
* - `MODEL_NOT_READY`
  - 503
  - Backend is running but the model hasn't loaded yet, or the
    Azure ML endpoint is unreachable in cloud serving mode
  - Retry after 5-10 s; startup usually takes < 30 s
* - `INTERNAL_SERVER_ERROR`
  - 500
  - Unexpected failure in the pipeline
  - Look up `request_id` in the backend logs; file an issue
```

### Explanation-specific

```{list-table}
:widths: 22 8 40 30
:header-rows: 1

* - `error_code`
  - HTTP
  - When
  - What to do
* - `EXPLAIN_FAILED`
  - 500
  - Saliency generation failed after inference succeeded
  - The prediction is still valid; retry the explanation
* - `EXPLAIN_TIMEOUT`
  - 504
  - Explanation exceeded its time budget
  - Retry, or use a smaller image
```

## Auth and access codes

```{list-table}
:widths: 22 8 40 30
:header-rows: 1

* - `error_code`
  - HTTP
  - When
  - What to do
* - `UNAUTHORIZED`
  - 401
  - No valid credential on a route that requires one, or a bearer
    token that failed verification
  - Log in, or send a valid `X-API-Key`; see {doc}`security-model`
* - `FORBIDDEN`
  - 403
  - Authenticated, but the route requires the `admin` role
  - Request admin access; 403 means the credential was valid
* - `INVALID_CREDENTIALS`
  - 401
  - Email/password login failed
  - Check the credentials; the message does not disclose which field
* - `EMAIL_TAKEN`
  - 409
  - Registration with an already-registered email
  - Log in instead, or use another address
* - `OAUTH_FAILED`
  - 400
  - GitHub OAuth callback could not be completed
  - Restart the login flow from `/auth/github/login`
* - `RATE_LIMITED`
  - 429
  - Per-IP request rate exceeded (20/minute)
  - Back off and retry; see {doc}`security-model`
```

## Resource and configuration codes

```{list-table}
:widths: 22 8 40 30
:header-rows: 1

* - `error_code`
  - HTTP
  - When
  - What to do
* - `NOT_FOUND`
  - 404
  - Requested resource does not exist
  - Check the identifier
* - `INVALID_PREDICTION_ID`
  - 422
  - Feedback references a prediction id that isn't a valid UUID
    or doesn't exist
  - Use the `id` returned by `/infer`
* - `MISCONFIGURED` /
    `SERVER_MISCONFIGURED`
  - 500
  - A required environment variable or backing service is absent
  - An operator problem, not a client one; check backend logs
* - `HTTP_ERROR`
  - varies
  - Fallback envelope for an unmapped HTTP error
  - Treat by status code
```

## Why this design

We separated code from message because:

1. **Stable contract.** Translating messages, rewording errors for
   UX, or appending debug info never changes the code. Clients can
   build switch statements against codes without breaking on
   cosmetic changes.

2. **Programmatic handling.** A robotic platform should re-upload
   on `CORRUPT_FILE` (probably a transient SD-card read) but not
   on `IMAGE_TOO_SMALL` (a real user error). Switching on message
   substrings is fragile.

3. **Observability.** The same codes appear in backend logs and
   monitoring dashboards. Grep-ability across CLI stderr, API
   response bodies, and server logs is a feature.

## When a code doesn't cover the case

If the pipeline hits something we didn't anticipate (an OOM inside
torch, a segfault from opencv) - the global exception handler in
`api.middleware.exception_handlers` catches it and returns
`INTERNAL_SERVER_ERROR`. The full traceback goes to backend logs
with the same `request_id`, so you can still trace it.

We explicitly don't raise `INTERNAL_SERVER_ERROR` from our own
code. It's the signal of "something we didn't plan for" - if a new
failure mode becomes common, it gets its own code in a spec bump
(`MODEL_NOT_READY` was added in pipeline contract v0.2.1 after exactly
this pattern).

## Adding a new code

1. Add the row to {doc}`../reference/pipeline-contract` §5 in a minor
   version bump (e.g. 0.2.1 -> 0.2.2).
2. Add the code to `cv_pipeline.validation.ValidationError` or the
   appropriate raise site.
3. If HTTP-visible, add the mapping in `api.routers.infer._ERROR_STATUS`.
4. Add a test that exercises the new path.
5. Mention it in the error table above.

The whole round-trip is a 30-minute PR.
