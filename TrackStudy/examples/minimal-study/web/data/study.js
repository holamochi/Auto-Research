window.TRACKSTUDY_DATA = {
  "experiments": [
    {
      "brief": {
        "change": "This is the root experiment.",
        "conclusion": "The baseline provides a traceable reference for later changes.",
        "experiment": "Establish the initial protocol and evaluation contract."
      },
      "detail": {
        "caveats": [
          "A single baseline does not establish causal effects or stability."
        ],
        "changes": [
          {
            "from": null,
            "kind": "origin",
            "summary": "Create the baseline."
          }
        ],
        "conclusion": "Use this result only as the documented starting point.",
        "experiment": "Run the initial method with a fixed data and evaluation protocol."
      },
      "evidence": [
        {
          "claimPolicy": "citable",
          "id": "ev-baseline-report",
          "lineEnd": 4,
          "lineStart": 1,
          "path": "evidence/baseline.md",
          "sourceSha256": "c0fb622f264800bae1d1a2d1aa2498ea3f7317b63336bf937e9e40c9fbf3c2b1",
          "type": "local"
        }
      ],
      "id": "01_baseline",
      "number": "01",
      "status": "done",
      "title": "Baseline",
      "track": "main"
    },
    {
      "brief": {
        "change": "Replace the baseline component while keeping the evaluation fixed.",
        "conclusion": "The method improves the recorded metric in this single run.",
        "experiment": "Test a gated module under the baseline protocol."
      },
      "detail": {
        "caveats": [
          "The result is a single run and does not establish cross-seed stability."
        ],
        "changes": [
          {
            "from": "01_baseline",
            "kind": "primary",
            "summary": "Replace the baseline component with a gated module."
          }
        ],
        "conclusion": "The observed improvement supports further validation of the gated design.",
        "experiment": "Use the same data and evaluator while introducing a gated module."
      },
      "evidence": [
        {
          "claimPolicy": "citable",
          "id": "ev-method-report",
          "lineEnd": 5,
          "lineStart": 1,
          "path": "evidence/method.md",
          "sourceSha256": "58bff393e7550fdc5102fba285defc24dd95e4d98b92a8332b20003c989721e0",
          "type": "local"
        }
      ],
      "id": "02_gated_method",
      "number": "02",
      "status": "done",
      "title": "Gated method",
      "track": "main"
    }
  ],
  "meta": {
    "experimentCount": 2,
    "relationCount": 1,
    "schemaVersion": 1,
    "sourceDigest": "20c3c27216e0ee866ea0180726c4075fa3f8e889506426394d7decd8f551ebc3"
  },
  "project": {
    "description": "A minimal evidence-backed experiment lineage.",
    "id": "minimal-trackstudy-example",
    "snapshotDate": "2026-08-18",
    "title": "Minimal TrackStudy Example"
  },
  "relations": [
    {
      "evidence": [
        "ev-method-report"
      ],
      "from": "01_baseline",
      "id": "rel-01-02",
      "kind": "evolution",
      "label": "Replace the baseline component with a gated module",
      "primary": true,
      "to": "02_gated_method",
      "type": "depends_on"
    }
  ],
  "schemaVersion": 1,
  "tracks": [
    {
      "color": "#58a487",
      "id": "main",
      "label": "Main route"
    }
  ]
};
