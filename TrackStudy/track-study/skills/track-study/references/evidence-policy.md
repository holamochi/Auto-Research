# Evidence policy

## Evidence classes

- `local`: a text file inside the study workspace with line range and SHA-256.
- `manifest`: a machine identity or protocol record inside the study workspace.
- `external`: an HTTPS source that is useful context but not locally immutable.
- `remote-summary`: a path or statement recorded from another system without a local payload.

## Claim boundaries

- `citable`: the cited source directly supports the claim and is locally reproducible.
- `context-only`: useful for orientation, but insufficient for a formal result claim.
- `not-citable`: missing, remote-only, stale, or otherwise unavailable for verification.

## Required local fields

Every local or manifest evidence item must include:

```json
{
  "id": "ev-baseline-report",
  "type": "local",
  "path": "evidence/baseline.md",
  "lineStart": 1,
  "lineEnd": 8,
  "sourceSha256": "64 lowercase hexadecimal characters",
  "claimPolicy": "citable"
}
```

Paths are relative to the study root and may not escape it. Line ranges are inclusive.

## Relationship policy

Every relationship must cite at least one evidence ID. A relationship describes a documented connection, not merely a visual grouping. If the evidence only supports comparison, do not encode evolution.

## Freshness

Recompute SHA-256 after editing a source. Regenerate the browser data after changing source JSON, evidence, or the web build contract. Treat a stale digest as a build failure.

## Missing evidence

Represent missing evidence explicitly in caveats and status. Do not create fabricated local files solely to make validation pass.
