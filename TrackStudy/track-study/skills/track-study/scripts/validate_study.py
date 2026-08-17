#!/usr/bin/env python3
"""Validate a TrackStudy workspace and optionally require a current web build."""

from __future__ import annotations

import argparse
from pathlib import Path

from trackstudy_core import ContractError, build_payload, render_javascript


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study_root", type=Path)
    parser.add_argument("--check-built", action="store_true", help="require web/data/study.js to be current")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.study_root.resolve()
    try:
        payload = build_payload(root)
    except ContractError as exc:
        raise SystemExit(f"TrackStudy validation failed: {exc}") from exc
    if args.check_built:
        output = root / "web" / "data" / "study.js"
        expected = render_javascript(payload)
        if not output.is_file():
            raise SystemExit(f"TrackStudy validation failed: generated data is missing: {output}")
        if output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"TrackStudy validation failed: generated data is stale: {output}")
    print(
        f"TrackStudy validation passed: {payload['meta']['experimentCount']} experiments, "
        f"{payload['meta']['relationCount']} relations, digest {payload['meta']['sourceDigest']}"
    )


if __name__ == "__main__":
    main()
