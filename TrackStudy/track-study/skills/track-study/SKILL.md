---
name: track-study
description: Organize complex research repositories into evidence-backed experiment lineages and reusable static web atlases. Use when Codex needs to inventory code, reports, notes, runs, or results; reconstruct experiment evolution; create stable node and relation records; validate evidence paths, line ranges, and hashes; or generate a TrackStudy web view without inventing causal links.
---

# TrackStudy

Turn heterogeneous research files into a reproducible graph whose summaries and relationships remain traceable to source evidence. Keep source records authoritative and treat the web atlas as a deterministic generated view.

## Gather context

1. Read repository-level instructions and the project overview before scanning subdirectories.
2. Identify authoritative sources: manifests, immutable run metadata, formal reports, code entrypoints, and result indexes.
3. Distinguish current evidence from historical snapshots, plans, generated pages, and remote-only references.
4. Record missing or unavailable evidence instead of silently filling gaps.

Read [references/workflow.md](references/workflow.md) when reconstructing a repository for the first time. Read [references/evidence-policy.md](references/evidence-policy.md) before accepting claims or relationships. Read [references/data-contract.md](references/data-contract.md) when authoring or debugging TrackStudy JSON.

## Build the lineage

1. Create an isolated workspace with:

   ```bash
   python3 scripts/init_study.py <output-directory>
   ```

2. Build a source inventory before naming relationships. Group files by responsibility, not only by directory.
3. Assign stable experiment IDs. Preserve historical IDs when they are already cited by runs or reports.
4. Write each experiment at two levels:
   - `brief`: current experiment, change from predecessor, conclusion;
   - `detail`: full definition, typed predecessor changes, conclusion, caveats, and evidence.
5. Add a relationship only when a source supports it. Use `comparison` for parallel controls and `evolution` only for an actual method progression.
6. Keep negative, blocked, planned, and incomplete nodes visible with honest status values.
7. Build the browser data:

   ```bash
   python3 scripts/build_atlas.py <study-directory>
   ```

8. Validate the source and generated output:

   ```bash
   python3 scripts/validate_study.py <study-directory> --check-built
   ```

9. Preview `web/index.html` directly or serve the study root over local HTTP and open `/web/`. Check desktop and mobile layouts, light and dark themes, search, filtering, click details, double-click modal details, and evidence links.

## Guardrails

- Do not infer edges from numbering, timestamps, shared code, adjacent folders, or similar names.
- Do not rewrite historical paths or run IDs for visual consistency.
- Do not cite the generated atlas as stronger evidence than its source files.
- Do not drop failed experiments; distinguish terminal negative results from unfinished work.
- Do not claim cited-line correctness merely because a file and line range exist. Read the cited text.
- Do not overwrite an existing study workspace unless the user explicitly requests `--force`.
- Do not publish or deploy without separate authorization.

## Efficient review order

1. Read the root overview and machine manifest.
2. Map implementation families and experiment profiles.
3. Read group summaries and formal experiment reports.
4. Inspect exact code/config only for disputed claims.
5. Inspect raw runs or outputs only when aggregate reports are insufficient.
6. Write and validate one track at a time to keep evidence mistakes localized.

Stop and report a blocker when identity, predecessor, source path, or result denominator remains ambiguous after reading the authoritative sources.

## Verification checklist

- Every experiment ID is unique and stable.
- Every track reference and relationship endpoint exists.
- Primary evolution edges form an acyclic graph.
- Every non-structural relationship has evidence.
- Every local evidence path exists, remains inside the study root, has a valid line range, and matches its SHA-256.
- Every experiment contains concise and detailed narratives plus at least one caveat.
- The generated digest matches the current source data.
- JavaScript syntax and browser interactions pass.
- The final report separates verified facts, interpretations, missing evidence, and unrun checks.

## Bundled resources

- `scripts/init_study.py`: create a collision-safe workspace from the static template.
- `scripts/build_atlas.py`: validate sources and atomically generate browser data.
- `scripts/validate_study.py`: validate source contracts and optionally check generated output freshness.
- `assets/web-template/`: reusable offline-capable static atlas.
