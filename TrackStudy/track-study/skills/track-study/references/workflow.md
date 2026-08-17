# TrackStudy workflow

## Contents

1. Scope and source hierarchy
2. Inventory
3. Identity
4. Narratives and relationships
5. Generation
6. Review

## 1. Scope and source hierarchy

Write down the repository root, included research tracks, excluded archives, and the date of the snapshot. Establish a truth hierarchy before reading large volumes of files. A common order is:

1. machine-readable experiment/run manifest;
2. immutable run configuration and artifacts;
3. current formal reports;
4. implementation and profile code;
5. group summaries and project navigation;
6. planning notes and historical pages.

Generated dashboards are navigation aids, not independent evidence.

## 2. Inventory

Create a responsibility map:

| Responsibility | Typical sources | Questions |
|---|---|---|
| identity | manifest, profile, run config | What is the stable experiment ID? |
| implementation | source tree, entrypoint | Which code actually ran? |
| protocol | config, launcher, run receipt | What data, model, seed, and budget were used? |
| result | report, metrics, raw output | What denominator and evaluator produced the claim? |
| status | run receipt, current project summary | Completed, negative, blocked, planned, or unknown? |

Do not infer a missing responsibility from a neighboring file.

## 3. Identity

Prefer an existing immutable experiment ID. If none exists, create a lower-case stable ID and record the alias to any historical names. Keep display labels separate from identity.

Define tracks for research questions or modality families. A track is a view filter, not automatically a causal parent.

## 4. Narratives and relationships

For every experiment answer:

1. What is the experiment?
2. Relative to each cited predecessor, what changed?
3. What result was observed?
4. What does the result not prove?

Use `evolution` when the later experiment directly changes the earlier method. Use `variant` for a controlled branch, `comparison` for parallel baselines, `evaluation` when one node evaluates outputs from another, and `transfer` for cross-track reuse.

Mark at most one incoming evolution edge as primary. Additional predecessors remain visible as secondary or comparison relationships.

## 5. Generation

Run the builder only after the source JSON passes validation. The builder computes a source digest, embeds evidence metadata, and writes the browser data atomically. Never hand-edit generated `web/data/study.js`.

## 6. Review

Review in four passes:

1. identity and coverage;
2. relationship direction and type;
3. cited text and numerical denominators;
4. browser interaction and layout.

Static validation cannot prove that an interpretation is scientifically correct. Read every cited passage used for a headline conclusion.
