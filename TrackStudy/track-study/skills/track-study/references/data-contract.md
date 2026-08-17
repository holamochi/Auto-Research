# TrackStudy data contract

## Contents

1. Workspace layout
2. Study file
3. Experiment files
4. Relations
5. Evidence
6. Generated output

## 1. Workspace layout

```text
study-root/
├── study.json
├── experiments/
│   └── main.json
├── evidence/
│   └── baseline.md
└── web/
    ├── index.html
    ├── assets/
    └── data/study.js
```

## 2. Study file

`study.json` uses schema version 1:

```json
{
  "schemaVersion": 1,
  "project": {
    "id": "example-study",
    "title": "Example Study",
    "description": "A minimal lineage",
    "snapshotDate": "2026-08-17"
  },
  "tracks": [
    {"id": "main", "label": "Main route", "color": "#58a487"}
  ],
  "relations": []
}
```

IDs must match `^[a-z0-9][a-z0-9._:-]*$`.

## 3. Experiment files

Every JSON file under `experiments/` contains:

```json
{
  "schemaVersion": 1,
  "experiments": {
    "01_baseline": {
      "number": "01",
      "title": "Baseline",
      "track": "main",
      "status": "done",
      "brief": {
        "experiment": "What this experiment runs.",
        "change": "What changed from the predecessor.",
        "conclusion": "What was observed."
      },
      "detail": {
        "experiment": "Full experiment definition.",
        "changes": [
          {"from": null, "kind": "origin", "summary": "Initial baseline."}
        ],
        "conclusion": "Detailed result and interpretation.",
        "caveats": ["What this result does not prove."]
      },
      "evidence": []
    }
  }
}
```

Allowed status values are `planned`, `in-progress`, `done`, `blocked`, and `registered`.

## 4. Relations

Relations use predecessor-to-successor direction:

```json
{
  "id": "rel-01-02",
  "from": "01_baseline",
  "to": "02_method",
  "type": "depends_on",
  "kind": "evolution",
  "label": "Replace the baseline encoder",
  "primary": true,
  "evidence": ["ev-method-report"]
}
```

Allowed kinds are `evolution`, `variant`, `comparison`, `evaluation`, and `transfer`. Primary evolution edges must be acyclic, and each successor may have at most one primary incoming edge.

## 5. Evidence

Evidence IDs are globally unique. See [evidence-policy.md](evidence-policy.md) for fields and claim boundaries.

## 6. Generated output

`build_atlas.py` writes `web/data/study.js`:

```javascript
window.TRACKSTUDY_DATA = { /* validated payload */ };
```

The payload contains a deterministic source digest. Do not edit it by hand.
