# AutoResearch

AutoResearch collects reusable research workflows, small tools, and installable agent components. Each module should turn a repeated research practice into an auditable process with explicit inputs, deterministic outputs, and verification steps.

## Modules

| Module | Purpose | Status |
|---|---|---|
| [TrackStudy](TrackStudy/) | Turn a complex research repository into an evidence-backed experiment lineage and a reusable static web atlas. | Initial release |

## Repository principles

- Separate source evidence from generated views.
- Keep stable IDs for experiments, runs, and relationships.
- Never infer causal relationships from filenames or numbering alone.
- Record evidence paths, line ranges, and source hashes for claims.
- Make generated artifacts reproducible and validate them before publication.
- Keep project-specific data out of reusable templates.

## Adding a module

Place each independent capability in its own top-level folder. Give the repository root a short index entry and give the module its own README with scope, inputs, outputs, usage, limitations, and verification commands.

## License

Unless a module states otherwise, this repository is released under the [MIT License](LICENSE).
