"""Rate limiting must actually enforce, and must bucket per credential.

These tests exist because the suite previously had no assertion that a 429
is ever returned. Two real defects lived in that blind spot:

1. ``/infer`` and ``/explain`` each built their own ``Limiter``, so
   ``SlowAPIMiddleware`` did not consider them exempt and stacked a per-IP
   default on top of their per-credential buckets. Distinct callers on one
   IP could lock each other out, which is the opposite of the documented
   behaviour.

2. On FastAPI releases where ``include_router`` stops flattening routes into
   ``app.routes``, slowapi's ``_find_route_handler`` returns ``None``, every
   route is treated as exempt, and rate limiting silently stops enforcing
   with no error anywhere. ``test_default_limit_enforced_on_undecorated_route``
   fails loudly if that happens again.
"""

from __future__ import annotations

import pytest
from api.rate_limit import DEFAULT_LIMIT, credential_key, limiter
from fastapi.testclient import TestClient

pytestmark = pytest.mark.unit


def _limit_count(limit_string: str) -> int:
    """Return the request allowance from a slowapi limit string.

    Args:
        limit_string: A limit such as ``"20/minute"``.

    Returns:
        The integer allowance.
    """
    return int(limit_string.split("/")[0])


@pytest.fixture(autouse=True)
def _reset_limiter():
    """Clear counters between tests so one test cannot exhaust another."""
    limiter.reset()
    yield
    limiter.reset()


class TestLimiterWiring:
    """The decorator and the middleware must share one Limiter instance."""

    def test_decorated_routes_registered_on_the_app_limiter(
        self, client_with_user: TestClient
    ):
        """/infer and /explain register on the same limiter the middleware reads.

        If they register elsewhere, slowapi's ``_should_exempt`` will not find
        them and will apply the per-IP default on top of their own limit.
        """
        registered = set(client_with_user.app.state.limiter._route_limits)
        assert "api.routers.infer.run_inference" in registered
        assert "api.routers.explain.explain_image" in registered

    def test_app_limiter_is_the_shared_instance(self, client_with_user: TestClient):
        """``app.state.limiter`` is the module-level limiter, not a copy."""
        assert client_with_user.app.state.limiter is limiter

    def test_routes_are_discoverable_by_slowapi(self, client_with_user: TestClient):
        """slowapi must be able to resolve a handler from ``app.routes``.

        When it cannot, every route is silently treated as exempt and no limit
        is ever enforced.
        """
        from slowapi.middleware import _find_route_handler

        scope = {
            "type": "http",
            "path": "/infer",
            "method": "POST",
            "headers": [],
            "root_path": "",
            "query_string": b"",
            "path_params": {},
        }
        assert _find_route_handler(client_with_user.app.routes, scope) is not None


class TestEnforcement:
    """A 429 must actually be returned once a limit is exceeded."""

    def test_default_limit_enforced_on_undecorated_route(
        self, client_with_user: TestClient
    ):
        """An undecorated route is limited per IP by ``default_limits``.

        ``/auth/login`` is the case that matters: per-credential bucketing
        would be useless against a brute-force attempt that varies the
        credential on every request.
        """
        allowance = _limit_count(DEFAULT_LIMIT)
        codes = [
            client_with_user.post(
                "/auth/login",
                json={"email": "nobody@example.com", "password": "wrong-password"},
            ).status_code
            for _ in range(allowance + 5)
        ]
        assert 429 in codes, (
            f"no 429 in {allowance + 5} requests; rate limiting is not enforcing"
        )

    def test_rate_limited_response_uses_the_error_envelope(
        self, client_with_user: TestClient
    ):
        """A 429 carries the same JSON shape as other error responses."""
        allowance = _limit_count(DEFAULT_LIMIT)
        response = None
        for _ in range(allowance + 5):
            candidate = client_with_user.post(
                "/auth/login",
                json={"email": "nobody@example.com", "password": "wrong-password"},
            )
            if candidate.status_code == 429:
                response = candidate
                break

        assert response is not None
        body = response.json()
        assert body["error_code"] == "RATE_LIMITED"
        assert "message" in body
        assert "request_id" in body


class TestCredentialBucketing:
    """Decorated routes bucket per credential, not per IP."""

    def test_distinct_api_keys_get_distinct_buckets(self):
        """Two API keys on one IP must not share a counter."""

        class _Req:
            def __init__(self, key):
                self.cookies = {}
                self.headers = {"X-API-Key": key}
                self.client = type("C", (), {"host": "10.0.0.1"})()

        assert credential_key(_Req("key-aaaa")) != credential_key(_Req("key-bbbb"))

    def test_session_cookie_takes_precedence_over_api_key(self):
        """A session cookie identifies the caller even if a key is also sent."""

        class _Req:
            cookies = {"session_id": "session-value-here"}
            headers = {"X-API-Key": "some-key"}
            client = type("C", (), {"host": "10.0.0.1"})()

        assert credential_key(_Req()).startswith("sid:")

    def test_anonymous_callers_fall_back_to_ip(self):
        """With no credential the bucket is the client IP."""

        class _Req:
            cookies: dict[str, str] = {}
            headers: dict[str, str] = {}
            client = type("C", (), {"host": "10.0.0.1"})()

        assert credential_key(_Req()) == "ip:10.0.0.1"

    def test_credential_is_truncated_in_the_bucket_label(self):
        """The full credential never reaches slowapi's storage keys."""
        secret = "s" * 200

        class _Req:
            cookies: dict[str, str] = {}
            headers = {"X-API-Key": secret}
            client = type("C", (), {"host": "10.0.0.1"})()

        assert secret not in credential_key(_Req())
