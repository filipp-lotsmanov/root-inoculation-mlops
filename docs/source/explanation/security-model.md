# Security model

How authentication and authorization work in the deployed system.

The backend supports three credential types against a single user
identity, resolved in one place. This page explains what each is for,
why the design is shaped this way, and what is deliberately out of
scope.

## Three credentials, one identity

A route handler never inspects credentials directly. It declares which
*tier* of access it needs, and the auth layer resolves whichever
credential the caller presented into a `User`:

| Credential | Header / cookie | Intended caller |
|---|---|---|
| JWT | `Authorization: Bearer <jwt>` | OAuth web flow |
| Session | `session_id` cookie | Email + password web flow |
| API key | `X-API-Key` | CLI, service accounts, robotic platform |

`optional_user` in `api.auth.dependencies` resolves them in that order
and returns `User | None`.

Why multiplex in one dependency rather than run parallel auth paths?
The handler only cares about *who the user is*, not how they proved it.
Resolving in one place keeps routers clean and means the entire auth
decision is auditable in a single file.

### Fail-closed on JWT, fall through on the rest

The three branches deliberately fail differently:

- **JWT present but invalid → 401 immediately.** A bearer token is an
  explicit assertion of identity. If it does not verify, silently
  downgrading the caller to anonymous would mask expired-token bugs and
  hide credential problems from clients.
- **Session cookie or API key invalid → fall through.** These are
  convenience mechanisms. A stale cookie left in a browser should not
  hard-fail a request that would otherwise succeed anonymously; the
  caller simply continues as anonymous.

## Three access tiers

Routes choose one of three dependencies:

| Dependency | Returns | Failure | Used by |
|---|---|---|---|
| `optional_user` | `User \| None` | never | `/infer`, `/explain` |
| `require_user` | `User` | 401 | `/feedback`, `/stats` |
| `require_admin` | `User` | 403 | `/users`, `/monitoring`, feedback review |

`require_admin` layers on `require_user` so a *missing* credential still
returns 401 rather than 403. That distinction is load-bearing for the
frontend: 401 redirects to login, 403 renders a "forbidden" page.

Anonymous inference is intentional. `/infer` accepts unauthenticated
callers and writes the prediction row with `user_id = NULL`; when a
caller *is* authenticated, the prediction is attributed to them. This
keeps the demo path frictionless without losing attribution for real
users.

## API key verification is constant-time and O(1)

Keys are stored as bcrypt hashes, so verifying a key naively would mean
running bcrypt against every user row until one matches — O(n) in users,
with a deliberately slow hash each time.

`api.auth.api_key` uses the two-step pattern that Stripe and GitHub use:

1. Compute SHA-256 of the incoming key and look up the indexed
   `key_sha256` column — a single O(1) database hit.
2. Run `bcrypt.checkpw` once, against that one row.

SHA-256 is safe as an *index* here precisely because it is fast and
deterministic; the security property still comes from bcrypt on step 2.
Verification cost stays constant regardless of how many users exist.

## Sessions over JWT for the password flow

The email/password flow issues a server-side session, not a token. The
cookie carries only the session UUID; the row in `sessions` is the
source of truth.

This is a revocation argument. Deleting a session row is instant and
complete. Revoking a JWT before its expiry requires a blacklist table
consulted on every request — the same database hit, plus signature
verification on top. Default TTL is 7 days.

Sliding expiry is deliberately not implemented: it adds a write to every
authenticated request and makes test fixtures timing-dependent. It is
easy to add if session lifetime becomes a real complaint.

JWTs are still used for the OAuth flow, signed HS256 with minimal claims
(`sub`, `role`, `iat`, `exp`). HS256 rather than RS256 because one
service both issues and verifies — there is no third party that needs
verify-without-issue. Name and email are read from the database on
resolve rather than embedded, so a role change takes effect at the next
token issuance instead of lingering until the old token expires.

## OAuth

GitHub sign-in runs through Authlib, configured in `api.auth.oauth` with
one `oauth.register(...)` block. Adding Google or any other OIDC
provider is another registration block with no frontend change. The
OAuth state nonce is carried across the `/auth/github/login` →
`/auth/github/callback` redirect by Starlette's `SessionMiddleware`.

## Rate limiting

Per-IP limiting is enforced in-process via `slowapi` at 20 requests per
minute, returning a JSON `RATE_LIMITED` error envelope rather than
slowapi's default plaintext.

The threat this addresses is a leaked key being used in a hammer loop
against `/infer`, where each request costs GPU time. It is a fixed-window
limiter backed by in-memory storage, which means limits are per-process
and reset on restart — adequate for single-replica deployment, and the
thing to replace with a shared Redis backend before running multiple
replicas behind a load balancer.

## Why `/health` is unauthenticated

Container orchestrators — Compose, Portainer, Container Apps — must probe
`/health` to decide whether to route traffic. Giving them a credential
would mean distributing a secret to the orchestration layer, which is the
wrong place for it, and a separate auth path just for probes is more
machinery than the problem justifies.

`/health` exposes only readiness state: `status`, `model_loaded`, and
serving mode. It returns 503 until the model finishes loading, which is
what makes the compose healthcheck meaningful.

## Cookie flags

Session cookies are set `httponly`, `samesite=lax`, and `secure`
controlled by the `COOKIE_SECURE` environment variable — false for local
HTTP development, true wherever the deployment terminates TLS.
`samesite=lax` permits the cookie on top-level navigation, which the
OAuth redirect requires, while still blocking cross-site POST.

## Threat model

**In scope**

- Preventing unauthenticated *privileged* access (feedback, stats, user
  administration, monitoring).
- Bounding the cost of a leaked credential via rate limiting.
- Keeping secrets out of orchestration logs and image layers.
- Per-user attribution on predictions, so a bad prediction traces to a
  caller.

**Out of scope**

- **TLS termination** — handled by the reverse proxy on-premise and by
  Container Apps ingress in cloud; the application speaks HTTP behind them.
- **Audit logging of auth failures** — failures are logged, but there is
  no queryable audit trail.
- **CSRF tokens** — the API is header- and JSON-driven; the session
  cookie is `samesite=lax`, and no state-changing endpoint accepts a
  form post.
- **Distributed rate limiting** — see the in-memory caveat above.

## Handling secrets

:::{warning}
Never bake credentials into client code, frontend bundles, or
Dockerfiles. Locally they belong in `configs/env/.env`, which is not
committed. In CI use GitHub Secrets. For Portainer use its secret
management rather than plain environment values in compose — those are
visible to `docker inspect`.
:::

:::{warning}
`configs/env/env.example` is committed and must contain placeholders
only. Real values never go in it.
:::

The auth-related variables are `API_KEY` and `ADMIN_API_KEY` (which seed
the default researcher and admin users), `SESSION_SECRET`, and
`GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET`.

## Related

- Users and sessions schema: pipeline contract §10.
- Error envelope and `error_code` values: {doc}`error-codes`.
