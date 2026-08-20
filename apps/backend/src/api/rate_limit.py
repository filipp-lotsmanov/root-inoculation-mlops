"""The application's single rate limiter.

Lives in its own module rather than in ``main.py`` because the routers need
to import it to decorate their handlers, and ``main.py`` imports the routers.

Why one instance matters
------------------------
``SlowAPIMiddleware`` reads ``app.state.limiter`` and applies
``default_limits`` to any route it does not consider exempt. Its exemption
check is ``name in limiter._route_limits`` on *that* object. A route
decorated with a different ``Limiter`` is therefore not exempt, so both the
decorator's limit and the middleware's per-IP default apply to it.

That is what used to happen here: ``/infer`` and ``/explain`` each built
their own ``Limiter``, so their per-credential buckets were silently stacked
on top of a per-IP default, and the "a logged-in user cannot be locked out by
anonymous scrapers on the same IP" property their docstrings claimed was not
true. Sharing this instance restores it: the middleware sees the decorated
routes in ``_route_limits`` and defers to the decorator.

Layering
--------
- Undecorated routes get ``default_limits``, keyed per IP. This is the
  backstop that matters for ``/auth/login`` and ``/auth/register``, where
  per-credential bucketing would be meaningless against a brute-force
  attempt that varies the credential every request.
- ``/infer`` and ``/explain`` pass ``credential_key`` to the decorator, so an
  authenticated caller gets their own bucket.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from api.auth.dependencies import SESSION_COOKIE_NAME

__all__ = ["DEFAULT_LIMIT", "credential_key", "limiter"]

# Applied per IP to every route without its own decorator.
DEFAULT_LIMIT = "20/minute"


def credential_key(request: Request) -> str:
    """Bucket per credential when one is presented, per IP otherwise.

    slowapi calls this on every request to a decorated route to decide which
    counter to increment. The credential is NOT validated here: that would
    cost a database round trip on the hot path, and the auth dependency
    already validates downstream. A forged cookie simply lands in its own
    bucket and still gets a 401 from the dependency.

    Only a prefix of the credential is used, so distinct sessions and keys do
    not collide while the full token never reaches slowapi's storage keys.

    Args:
        request: The incoming request.

    Returns:
        A stable bucket label for this caller.
    """
    sid = request.cookies.get(SESSION_COOKIE_NAME)
    if sid:
        return f"sid:{sid[:16]}"
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key[:16]}"
    return f"ip:{get_remote_address(request)}"


# storage_uri is in-memory, so counters are per process. Behind more than one
# replica the effective limit is multiplied by the replica count; point this
# at Redis if that ever matters.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[DEFAULT_LIMIT],
    storage_uri="memory://",
    strategy="fixed-window",
)
