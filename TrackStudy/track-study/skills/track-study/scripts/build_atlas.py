#!/usr/bin/env python3
"""Validate TrackStudy sources and atomically generate browser data."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from trackstudy_core import build_payload, render_javascript


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study_root", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if generated data is missing or stale")
    mode.add_argument("--dry-run", action="store_true", help="validate and print the digest without writing")
    return parser.parse_args()


def atomic_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    args = parse_args()
    root = args.study_root.resolve()
    payload = build_payload(root)
    rendered = render_javascript(payload)
    output = root / "web" / "data" / "study.js"
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"generated data is missing or stale: {output}")
        print(f"TrackStudy build is current: {payload['meta']['sourceDigest']}")
        return
    if args.dry_run:
        print(
            f"TrackStudy dry-run: {payload['meta']['experimentCount']} experiments, "
            f"{payload['meta']['relationCount']} relations, digest {payload['meta']['sourceDigest']}"
        )
        return
    atomic_write(output, rendered)
    print(
        f"built {output}: {payload['meta']['experimentCount']} experiments, "
        f"{payload['meta']['relationCount']} relations, digest {payload['meta']['sourceDigest']}"
    )


if __name__ == "__main__":
    main()
