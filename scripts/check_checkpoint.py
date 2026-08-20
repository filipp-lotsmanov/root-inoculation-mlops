"""Probe whether a checkpoint loads under torch's safe unpickler.

Answers three questions in one run:

1. Does ``torch.load(..., weights_only=True)`` succeed on this checkpoint?
2. If not, exactly which objects are disallowed (all of them, not just
   the first one torch happens to trip on)?
3. Does ``SegmentationModel`` construct end-to-end under the safe loader?

Also prints the SHA-256, which is what an integrity check in
``weights.py`` would need to pin.

Usage:
    python check_checkpoint.py                        # via get_weights("unet-v1")
    python check_checkpoint.py --version unet-v2
    python check_checkpoint.py --path /path/to/best_model.pth

Run from the repo root with the project environment active:
    uv run python check_checkpoint.py
"""

from __future__ import annotations

import argparse
import hashlib
import pickletools
import sys
import zipfile
from pathlib import Path

import torch

# Types torch's _weights_only_unpickler accepts without an explicit allowlist.
_SAFE_PRIMITIVES = (
    bool,
    int,
    float,
    complex,
    str,
    bytes,
    bytearray,
    type(None),
    torch.Tensor,
    torch.Size,
    torch.dtype,
    torch.device,
)


def sha256_of(path: Path) -> str:
    """Return the SHA-256 hex digest of the file, streamed in 1 MB chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pickled_globals(path: Path) -> set[str]:
    """Return every ``module.Name`` the checkpoint's pickle stream references.

    Reads the pickle opcodes without executing them, so this is safe to run
    on a checkpoint you do not yet trust. A .pth is a zip archive; the
    pickle lives in ``*/data.pkl``.
    """
    found: set[str] = set()
    try:
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith("data.pkl")]
            if not names:
                return found
            raw = archive.read(names[0])
    except zipfile.BadZipFile:
        # Legacy (pre-1.6) non-zip checkpoint. Fall back to the whole file.
        raw = path.read_bytes()

    for opcode, arg, _pos in pickletools.genops(raw):
        if opcode.name in ("GLOBAL", "STACK_GLOBAL") and isinstance(arg, str):
            found.add(arg.replace(" ", "."))
    return found


def describe(obj: object, prefix: str = "", depth: int = 0) -> list[str]:
    """Walk a loaded checkpoint and return one description line per entry.

    Lines for values outside the safe-primitive set are marked UNSAFE, which
    is what would make ``weights_only=True`` reject the file.
    """
    lines: list[str] = []
    if depth > 3:
        return lines

    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}[{key!r}]"
            kind = type(value)
            if isinstance(value, torch.Tensor):
                lines.append(
                    f"  ok     {path}: Tensor{tuple(value.shape)} {value.dtype}"
                )
            elif isinstance(value, dict):
                lines.append(f"  ok     {path}: dict({len(value)} entries)")
                lines.extend(describe(value, path, depth + 1))
            elif isinstance(value, (list, tuple)):
                lines.append(f"  ok     {path}: {kind.__name__}({len(value)})")
            elif isinstance(value, _SAFE_PRIMITIVES):
                lines.append(f"  ok     {path}: {kind.__name__} = {value!r}")
            else:
                lines.append(f"  UNSAFE {path}: {kind.__module__}.{kind.__qualname__}")
    return lines


def main() -> int:
    """Run the probe and return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="unet-v1")
    parser.add_argument("--path", type=Path, default=None)
    args = parser.parse_args()

    if args.path is not None:
        checkpoint_path = args.path
        if not checkpoint_path.exists():
            print(f"FAIL  no such file: {checkpoint_path}")
            return 2
    else:
        from cv_pipeline.weights import get_weights

        print(f"Resolving weights for version {args.version!r} ...")
        try:
            checkpoint_path = get_weights(args.version)
        except Exception as exc:
            print(
                f"FAIL  get_weights({args.version!r}) raised "
                f"{type(exc).__name__}: {exc}"
            )
            print(
                "      The download path is broken before we even reach "
                "torch.load. Fix the REGISTRY URL first."
            )
            return 2

    size_mb = checkpoint_path.stat().st_size / (1024 * 1024)
    print(f"file    {checkpoint_path}")
    print(f"size    {size_mb:.1f} MB")
    print(f"sha256  {sha256_of(checkpoint_path)}")
    print()

    print("--- pickle globals referenced (static read, nothing executed) ---")
    globals_found = pickled_globals(checkpoint_path)
    if not globals_found:
        print("  none beyond the built-in rebuild helpers")
    for name in sorted(globals_found):
        print(f"  {name}")
    print()

    print("--- torch.load(weights_only=True) ---")
    safe_ok = False
    try:
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        safe_ok = True
        print("  PASS")
    except Exception as exc:
        print(f"  FAIL  {type(exc).__name__}")
        print(f"        {str(exc).splitlines()[0][:200]}")
        print()
        print("  Re-reading permissively to enumerate what is in the file.")
        print("  (Same trust level as the code you deploy today.)")
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    print()
    print("--- checkpoint contents ---")
    if isinstance(checkpoint, dict):
        for line in describe(checkpoint):
            print(line)
    else:
        print(f"  top level is not a dict: {type(checkpoint)}")
    print()

    print("--- keys SegmentationModel actually reads ---")
    if isinstance(checkpoint, dict):
        has_sd = "model_state_dict" in checkpoint
        version = checkpoint.get("model_version")
        print(
            f"  model_state_dict present : {has_sd}"
            f"{'' if has_sd else '  (falls back to the top-level dict)'}"
        )
        print(f"  model_version            : {version!r} ({type(version).__name__})")
    print()

    print("--- SegmentationModel end-to-end under the safe loader ---")
    original_load = torch.load
    torch.load = lambda *a, **k: original_load(*a, **{**k, "weights_only": True})
    try:
        from cv_pipeline.segmentation import SegmentationModel

        model = SegmentationModel(str(checkpoint_path))
        print(
            f"  PASS  in_channels={model.in_channels} "
            f"model_version={model.model_version}"
        )
    except Exception as exc:
        print(f"  FAIL  {type(exc).__name__}: {str(exc)[:200]}")
        safe_ok = False
    finally:
        torch.load = original_load

    print()
    print("=" * 62)
    if safe_ok:
        print("VERDICT  Safe to delete weights_only=False from")
        print("         segmentation.py:200. torch 2.6 already defaults to")
        print("         the safe unpickler, so removing the argument is")
        print("         enough - no new flag needed.")
    else:
        print("VERDICT  The checkpoint carries objects the safe unpickler")
        print("         rejects. Do NOT flip the flag yet. See the UNSAFE")
        print("         lines above - re-save the checkpoint keeping only")
        print("         model_state_dict + model_version.")
    print("=" * 62)
    return 0 if safe_ok else 1


if __name__ == "__main__":
    sys.exit(main())
