#!/usr/bin/env python3
"""Create a collision-safe TrackStudy workspace from the bundled template."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new study directory")
    parser.add_argument("--title", default="Example Study", help="project display title")
    parser.add_argument("--force", action="store_true", help="replace an empty existing directory")
    return parser.parse_args()


def stable_project_id(title: str) -> str:
    value = "".join(character.lower() if character.isalnum() else "-" for character in title)
    value = "-".join(part for part in value.split("-") if part)
    return value or "example-study"


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    if output.exists():
        if not args.force:
            raise SystemExit(f"refusing to overwrite existing path: {output}")
        if any(output.iterdir()):
            raise SystemExit(f"--force only accepts an empty existing directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    skill_root = Path(__file__).resolve().parents[1]
    template = skill_root / "assets" / "web-template"
    shutil.copytree(template, output / "web")
    (output / "experiments").mkdir()
    (output / "evidence").mkdir()

    evidence_text = (
        "# Baseline evidence\n\n"
        "The baseline establishes the initial protocol and evaluation contract.\n"
        "Its result is a reference point, not evidence that later changes caused an improvement.\n"
    )
    evidence_path = output / "evidence" / "baseline.md"
    evidence_path.write_text(evidence_text, encoding="utf-8")
    evidence_sha = hashlib.sha256(evidence_text.encode("utf-8")).hexdigest()
    method_text = (
        "# Method evidence\n\n"
        "The second experiment replaces the baseline component with a gated module.\n"
        "The evaluation reports a measurable improvement under the same protocol.\n"
        "The single run does not establish stability across seeds or datasets.\n"
    )
    method_path = output / "evidence" / "method.md"
    method_path.write_text(method_text, encoding="utf-8")
    method_sha = hashlib.sha256(method_text.encode("utf-8")).hexdigest()

    study = {
        "schemaVersion": 1,
        "project": {
            "id": stable_project_id(args.title),
            "title": args.title,
            "description": "A minimal evidence-backed experiment lineage.",
            "snapshotDate": date.today().isoformat(),
        },
        "tracks": [{"id": "main", "label": "Main route", "color": "#58a487"}],
        "relations": [
            {
                "id": "rel-01-02",
                "from": "01_baseline",
                "to": "02_gated_method",
                "type": "depends_on",
                "kind": "evolution",
                "label": "Replace the baseline component with a gated module",
                "primary": True,
                "evidence": ["ev-method-report"],
            }
        ],
    }
    experiments = {
        "schemaVersion": 1,
        "experiments": {
            "01_baseline": {
                "number": "01",
                "title": "Baseline",
                "track": "main",
                "status": "done",
                "brief": {
                    "experiment": "Establish the initial protocol and evaluation contract.",
                    "change": "This is the root experiment.",
                    "conclusion": "The baseline provides a traceable reference for later changes.",
                },
                "detail": {
                    "experiment": "Run the initial method with a fixed data and evaluation protocol.",
                    "changes": [{"from": None, "kind": "origin", "summary": "Create the baseline."}],
                    "conclusion": "Use this result only as the documented starting point.",
                    "caveats": ["A single baseline does not establish causal effects or stability."],
                },
                "evidence": [
                    {
                        "id": "ev-baseline-report",
                        "type": "local",
                        "path": "evidence/baseline.md",
                        "lineStart": 1,
                        "lineEnd": 4,
                        "sourceSha256": evidence_sha,
                        "claimPolicy": "citable",
                    }
                ],
            },
            "02_gated_method": {
                "number": "02",
                "title": "Gated method",
                "track": "main",
                "status": "done",
                "brief": {
                    "experiment": "Test a gated module under the baseline protocol.",
                    "change": "Replace the baseline component while keeping the evaluation fixed.",
                    "conclusion": "The method improves the recorded metric in this single run.",
                },
                "detail": {
                    "experiment": "Use the same data and evaluator while introducing a gated module.",
                    "changes": [
                        {
                            "from": "01_baseline",
                            "kind": "primary",
                            "summary": "Replace the baseline component with a gated module.",
                        }
                    ],
                    "conclusion": "The observed improvement supports further validation of the gated design.",
                    "caveats": ["The result is a single run and does not establish cross-seed stability."],
                },
                "evidence": [
                    {
                        "id": "ev-method-report",
                        "type": "local",
                        "path": "evidence/method.md",
                        "lineStart": 1,
                        "lineEnd": 5,
                        "sourceSha256": method_sha,
                        "claimPolicy": "citable",
                    }
                ],
            },
        },
    }
    (output / "study.json").write_text(
        json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "experiments" / "main.json").write_text(
        json.dumps(experiments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"initialized TrackStudy workspace: {output}")
    print(f"next: python3 {skill_root / 'scripts' / 'build_atlas.py'} {output}")


if __name__ == "__main__":
    main()
