"""Seed the users table with default accounts on first startup.

Called by entrypoint.sh after migrations. Idempotent — skips if any
user already exists. Reads API_KEY and ADMIN_API_KEY environment
variables and stores their bcrypt hashes so the auth module can
verify them.
"""

from __future__ import annotations

import hashlib
import logging
import os

import bcrypt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from api.db.models import User

logger = logging.getLogger(__name__)

# bcrypt hashes at most 72 bytes of input. `openssl rand -hex 32` yields 64
# characters, which fits; `-hex 64` yields 128 and would not.
_BCRYPT_MAX_KEY_BYTES = 72


def _sha256_hex(key: str) -> str:
    """Compute the SHA-256 hex digest of a plaintext API key.

    Args:
        key: The plaintext API key string.

    Returns:
        A 64-character lowercase hex string.
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def seed_default_user() -> None:
    """Create default researcher and admin users if the users table is empty.

    Reads ``API_KEY`` and ``ADMIN_API_KEY`` from the environment for
    the plaintext keys and ``DB_URL`` for the database connection. The
    async dialect suffix is stripped because this runs synchronously
    at startup.

    Raises:
        RuntimeError: If ``API_KEY`` or ``ADMIN_API_KEY`` is not set.
    """
    api_key = os.getenv("API_KEY")
    admin_key = os.getenv("ADMIN_API_KEY")
    if not api_key or not admin_key:
        raise RuntimeError(
            "API_KEY and ADMIN_API_KEY environment variables must both "
            "be set. Cannot seed default users without keys to hash."
        )

    # bcrypt refuses inputs over 72 bytes. This runs in entrypoint.sh under
    # `set -e`, so an unguarded ValueError here kills the container at boot
    # with a traceback that does not name the offending variable.
    for name, value in (("API_KEY", api_key), ("ADMIN_API_KEY", admin_key)):
        if len(value.encode("utf-8")) > _BCRYPT_MAX_KEY_BYTES:
            raise RuntimeError(
                f"{name} is {len(value.encode('utf-8'))} bytes; bcrypt accepts "
                f"at most {_BCRYPT_MAX_KEY_BYTES}. Generate one with: "
                f"openssl rand -hex 32"
            )

    db_url = os.getenv("DB_URL", "")
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_url)

    try:
        _seed(engine, api_key, admin_key)
    finally:
        # One-shot process, but leaving the pool open holds a Postgres
        # connection until the interpreter exits.
        engine.dispose()


def _seed(engine, api_key: str, admin_key: str) -> None:
    """Insert the default users if the table is empty.

    Args:
        engine: A synchronous SQLAlchemy engine.
        api_key: Plaintext key for the seeded researcher account.
        admin_key: Plaintext key for the seeded admin account.
    """
    with Session(engine) as session:
        existing = session.execute(
            select(User).limit(1),
        ).scalar_one_or_none()
        if existing is not None:
            logger.info(
                "Users table already has entries — skipping seed.",
            )
            return

        researcher_hash = bcrypt.hashpw(
            api_key.encode("utf-8"),
            bcrypt.gensalt(),
        )
        admin_hash = bcrypt.hashpw(
            admin_key.encode("utf-8"),
            bcrypt.gensalt(),
        )

        session.add(
            User(
                name="Default Researcher",
                api_key_hash=researcher_hash.decode("utf-8"),
                key_sha256=_sha256_hex(api_key),
                role="researcher",
            )
        )
        session.add(
            User(
                name="Admin",
                api_key_hash=admin_hash.decode("utf-8"),
                key_sha256=_sha256_hex(admin_key),
                role="admin",
            )
        )
        session.commit()
        logger.info("Seeded default researcher and admin users.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    seed_default_user()
