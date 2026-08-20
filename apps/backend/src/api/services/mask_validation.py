"""Strict validation of reviewer-supplied corrected masks.

A corrected mask becomes a training label, so it must match the
format the pipeline produces: a single-channel, 8-bit, binary PNG the
same size as the prediction's input image. Anything else is rejected
so a malformed label cannot silently poison retraining.

The validator is deliberately forgiving about *encoding* (it accepts
RGB or grayscale input and collapses it to single channel, and treats
any non-zero pixel as root) but strict about *correspondence*: the
mask must be a decodable image whose dimensions equal the prediction's
stored image dimensions.
"""

from __future__ import annotations

import base64
import binascii
import io
import logging

from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError

logger = logging.getLogger(__name__)

_BACKGROUND = 0
_ROOT = 255


class MaskValidationError(Exception):
    """Raised when a corrected mask fails validation.

    The ``error_code`` and ``message`` set on the instance are documented
    on ``__init__`` to avoid a duplicate autodoc description.
    """

    def __init__(self, error_code: str, message: str) -> None:
        """Initialise the error.

        Args:
            error_code: Machine-readable code, e.g. ``MASK_CORRUPT``.
            message: Human-readable explanation.
        """
        self.error_code = error_code
        self.message = message
        super().__init__(message)


def validate_corrected_mask(
    mask_b64: str,
    expected_width: int,
    expected_height: int,
) -> str:
    """Validate and normalise a base64-encoded corrected mask.

    Args:
        mask_b64: Base64-encoded PNG supplied by the reviewer.
        expected_width: Width in pixels of the prediction's image.
        expected_height: Height in pixels of the prediction's image.

    Returns:
        Base64-encoded PNG of the normalised single-channel binary
        mask (background ``0``, root ``255``), safe to store.

    Raises:
        MaskValidationError: If the input is not valid base64, not a
            decodable image, or the wrong dimensions.
    """
    try:
        raw = base64.b64decode(mask_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise MaskValidationError(
            "MASK_NOT_BASE64",
            "corrected_mask_b64 is not valid base64.",
        ) from exc

    # Image.open reads only the header, so size is known before any pixel data
    # is decoded. Checking dimensions here rather than after image.load() is
    # what makes a decompression bomb cheap to reject: a 69-byte PNG can
    # declare 40000x40000 and would otherwise allocate 1.6e9 pixels before the
    # dimension check below ever ran.
    try:
        image = Image.open(io.BytesIO(raw))
    except DecompressionBombError as exc:
        # Pillow raises at header-parse time when the declared size exceeds
        # twice MAX_IMAGE_PIXELS; between 1x and 2x it only warns and the
        # dimension check below rejects it. Both paths must be handled.
        raise MaskValidationError(
            "MASK_TOO_LARGE",
            "corrected_mask_b64 declares more pixels than can be decoded.",
        ) from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise MaskValidationError(
            "MASK_CORRUPT",
            "corrected_mask_b64 could not be decoded as an image.",
        ) from exc

    if image.size != (expected_width, expected_height):
        raise MaskValidationError(
            "MASK_DIMENSION_MISMATCH",
            (
                f"Mask is {image.width}x{image.height} but the prediction "
                f"image is {expected_width}x{expected_height}."
            ),
        )

    # Dimensions match the prediction's image, so the allocation is bounded by
    # a size we already accepted. DecompressionBombError is caught explicitly:
    # it subclasses Exception rather than OSError, so it would otherwise escape
    # as an uncaught 500 instead of a 422.
    try:
        image.load()
    except DecompressionBombError as exc:
        raise MaskValidationError(
            "MASK_TOO_LARGE",
            "corrected_mask_b64 declares more pixels than can be decoded.",
        ) from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise MaskValidationError(
            "MASK_CORRUPT",
            "corrected_mask_b64 could not be decoded as an image.",
        ) from exc

    # Collapse to single channel: RGB/RGBA are flattened to luminance,
    # which is fine for a binary mask. Then binarise so any non-zero
    # pixel becomes root (255) and zero stays background (0). This
    # accepts both already-binary masks and antialiased edges from an
    # annotation tool, storing the canonical 0/255 form.
    grayscale = image.convert("L")
    binary = grayscale.point(lambda px: _ROOT if px > 0 else _BACKGROUND)

    buffer = io.BytesIO()
    binary.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")
