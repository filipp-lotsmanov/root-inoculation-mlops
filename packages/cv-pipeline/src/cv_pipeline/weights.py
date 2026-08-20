"""Weight checkpoint download and caching.

Local analogue of the cloud model registry: a directory on disk plus
the code that knows how to populate it. Every version the package
knows about has an entry in REGISTRY mapping its version string to a
download URL. First call to get_weights() downloads; subsequent calls
return the cached path.

Design decisions:
- Cache directory defaults to ~/.cache/cv-pipeline/models (follows
  the XDG Base Directory convention). Overridable via
  CV_PIPELINE_CACHE_DIR. Docker containers mount this as a volume so
  weights persist across container restarts.
- REGISTRY is a Python dict rather than a JSON file shipped with the
  package. A dict is simpler, import-time typo-checked, and can be
  replaced with a JSON loader later without breaking callers.
  Alternative considered: per-version URL in an env var - rejected
  because it defers the "what models does this package support" answer
  to deployment config, which is the wrong layer.
- Downloads stream in 1 MB chunks so a 50 MB weight file does not blow
  up memory. We write to a temp file and rename on success so an
  interrupted download cannot leave a corrupt file in the cache.
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WeightSpec:
    """Where a checkpoint lives and what it should hash to.

    Attributes:
        url: Direct download URL returning raw bytes.
        sha256: Expected SHA-256 hex digest of the file. When set, a
            downloaded file whose digest differs is deleted and the download
            fails. ``None`` disables the check, which should only happen for
            a version whose digest has not been recorded yet.
    """

    url: str
    sha256: str | None = None


# Version string -> download URL. Add a new entry per new model.
# URLs must return the raw binary. For SharePoint / OneDrive share
# links, append &download=1 to force direct download. If the host
# returns HTML instead, the download will fail loudly with a clear
# message - see _download below.
REGISTRY: dict[str, WeightSpec | str] = {
    "unet-v1": WeightSpec(
        # TODO: replace with a GitHub Release asset on this repository and fill
        # in sha256 below. A personal file-share link is not a durable host:
        # it expires with the account and cannot be integrity-checked.
        url=(
            "https://edubuas-my.sharepoint.com/:u:/g/personal/"
            "240247_buas_nl/"
            "IQB2wvFuucF6QKxzhA_Se8i8ASonyPGioDLILJtH-sX066g"
            "?download=1"
        ),
        # Fill in once the artifact is republished. Until then the download is
        # unverified and get_weights() logs a warning on every cache miss.
        sha256=None,
    ),
}

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "cv-pipeline" / "models"


def get_cache_dir() -> Path:
    """Return the directory where cached weights are stored.

    Reads CV_PIPELINE_CACHE_DIR from the environment if set, otherwise
    uses the XDG default. Creates the directory if missing.

    Returns:
        Absolute path to the cache directory.
    """
    raw = os.getenv("CV_PIPELINE_CACHE_DIR")
    cache = Path(raw).expanduser() if raw else _DEFAULT_CACHE_DIR
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def list_versions() -> list[str]:
    """Return the sorted list of known model versions."""
    return sorted(REGISTRY)


def get_weights(version: str) -> Path:
    """Return the local path to the weights file for the given version.

    Downloads from REGISTRY[version] if the file is not already cached.

    Args:
        version: A key from REGISTRY, e.g. "unet-v1".

    Returns:
        Absolute path to the local .pth file.

    Raises:
        KeyError: If version is not in REGISTRY.
        RuntimeError: If the download fails or returns non-binary
            content (indicates a wrong or preview-page URL).
    """
    if version not in REGISTRY:
        raise KeyError(
            f"Unknown version '{version}'. "
            f"Known versions: {list_versions()}. "
            f"Add a new entry to REGISTRY in cv_pipeline/weights.py."
        )

    target = get_cache_dir() / f"{version}.pth"
    spec = _spec_for(version)

    if target.exists():
        # A cached file is re-verified rather than trusted: a truncated or
        # tampered cache volume would otherwise be loaded forever.
        if spec.sha256 is not None:
            _verify_digest(target, spec.sha256, delete_on_mismatch=True)
        logger.info("Using cached weights at '%s'.", target)
        return target

    logger.info("Downloading weights for '%s' from %s.", version, spec.url)
    _download(spec.url, target)

    if spec.sha256 is None:
        logger.warning(
            "No sha256 recorded for '%s'; the downloaded weights were NOT "
            "integrity-checked. Record the digest in REGISTRY.",
            version,
        )
    else:
        _verify_digest(target, spec.sha256, delete_on_mismatch=True)

    logger.info("Weights saved to '%s'.", target)
    return target


def _spec_for(version: str) -> WeightSpec:
    """Return the registry entry for *version* as a WeightSpec.

    Accepts a bare URL string as well as a WeightSpec so existing entries and
    test monkeypatches that map version to URL keep working.

    Args:
        version: A key present in REGISTRY.

    Returns:
        The normalised WeightSpec for that version.
    """
    entry = REGISTRY[version]
    if isinstance(entry, WeightSpec):
        return entry
    return WeightSpec(url=entry)


def sha256_of(path: Path) -> str:
    """Return the SHA-256 hex digest of *path*, streamed in 1 MB chunks.

    Exposed so the digest for a new REGISTRY entry can be computed with the
    same code that later verifies it.

    Args:
        path: File to digest.

    Returns:
        A 64-character lowercase hex string.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_digest(
    path: Path,
    expected: str,
    delete_on_mismatch: bool = False,
) -> None:
    """Check that *path* hashes to *expected*, raising if it does not.

    Args:
        path: File to check.
        expected: Expected SHA-256 hex digest.
        delete_on_mismatch: Remove the file before raising, so a poisoned
            cache entry cannot be reused by the next call.

    Raises:
        RuntimeError: If the digest does not match.
    """
    actual = sha256_of(path)
    if actual == expected.lower():
        logger.info("Checksum verified for '%s'.", path.name)
        return

    if delete_on_mismatch:
        path.unlink(missing_ok=True)
    raise RuntimeError(
        f"Checksum mismatch for '{path.name}': expected {expected}, got "
        f"{actual}. The file was not what the registry describes and has been "
        f"discarded."
    )


def _download(url: str, target: Path) -> None:
    """Stream a file from url to target.

    Writes to <target>.tmp first and renames on success so a failed
    download cannot leave a truncated file in the cache.
    """
    # Lazy import: requests is a dep of many ML libraries but we keep
    # the import out of module load to keep cv_pipeline import cheap.
    import requests

    with requests.get(
        url,
        stream=True,
        allow_redirects=True,
        timeout=60,
    ) as response:
        response.raise_for_status()

        # Guard against SharePoint-style preview redirects. A direct
        # download returns application/octet-stream or similar. HTML
        # means the URL is wrong (or SharePoint ignored &download=1).
        content_type = response.headers.get("Content-Type", "")
        if "html" in content_type.lower():
            raise RuntimeError(
                f"Expected binary response from {url} but got "
                f"content-type={content_type!r}. This is probably a "
                f"SharePoint preview page. Append '&download=1' to the "
                f"share URL, or host the file somewhere that returns "
                f"raw bytes (e.g. a GitHub Release asset)."
            )

        tmp = target.with_suffix(target.suffix + ".tmp")
        with tmp.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)
        tmp.replace(target)
