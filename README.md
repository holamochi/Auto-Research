# AutoResearch

**Turn repeated research practices into auditable workflows that an AI agent can run.**

[TrackStudy](TrackStudy/) · [Example study](TrackStudy/examples/minimal-study/) · [Issues](https://github.com/holamochi/Auto-Research/issues)

AutoResearch is a collection of research workflows, small tools, and installable agent skills. Each module has explicit inputs, deterministic outputs, and a verification step, so the results can be checked rather than trusted.

## Why

Research repositories accumulate dozens of experiments, reports, and result files. After a few months, nobody can say with confidence which run led to which conclusion, and AI assistants asked to summarise the history tend to invent links between experiments from file names or numbering.

AutoResearch packages the fixes for that as reusable workflows: every claim cites its evidence by path, line range, and hash, and generated views are rebuilt and validated from sources.

## Modules

| Module | What it does | Status |
| --- | --- | --- |
| [TrackStudy](TrackStudy/) | Turns a complex research repository into an evidence-backed experiment lineage and a static, browsable web atlas. Ships as a Codex skill and plugin. | Initial release |

## Quick start: TrackStudy

See a working atlas right away by opening `TrackStudy/examples/minimal-study/web/index.html` in a browser.

To build an atlas for your own study:

```bash
TRACKSTUDY=TrackStudy/track-study/skills/track-study

python3 "$TRACKSTUDY/scripts/init_study.py" my-study       # create a study workspace
# edit my-study/study.json and my-study/experiments/*.json
python3 "$TRACKSTUDY/scripts/build_atlas.py" my-study      # generate the atlas
python3 "$TRACKSTUDY/scripts/validate_study.py" my-study   # check every cited path, line range, and hash
python3 -m http.server 8000 --directory my-study           # open http://127.0.0.1:8000/web/
```

Install it as a Codex skill:

```text
$skill-installer install https://github.com/holamochi/Auto-Research/tree/main/TrackStudy/track-study/skills/track-study
```

Full instructions, source-of-truth rules, and limits are in the [TrackStudy README](TrackStudy/README.md).

## Principles

- Keep source evidence separate from generated views.
- Give experiments, runs, and relationships stable IDs.
- Never infer causal relationships from file names or numbering alone.
- Record evidence paths, line ranges, and source hashes for every claim.
- Make generated artifacts reproducible, and validate them before publishing.
- Keep project-specific data out of reusable templates.

## Adding a module

Put each independent capability in its own top-level folder with its own README covering scope, inputs, outputs, usage, limitations, and verification commands. Then add a one-line entry to the Modules table above.

## Topic / Keywords

- **Problem**: research projects lose track of how experiments relate and which evidence supports which conclusion; AI-generated summaries of that history are hard to verify.
- **Approach**: agent skills and scripts that inventory a research repository, assign stable experiment IDs, link experiments only with cited evidence (file path, line range, SHA), validate everything, and render a static experiment atlas that runs from `file://` with no backend.
- **Category**: research workflow automation · experiment tracking · research provenance · AI agent skills (Codex skill / plugin) · reproducible research
- **Not to be confused with**: an ML experiment tracker that logs metrics during training (such as MLflow or Weights & Biases), or an autonomous research agent that runs experiments by itself. AutoResearch organises and verifies experiments that already exist.
- **Keywords**: experiment lineage, experiment map, research atlas, research provenance, evidence-backed summaries, reproducibility, audit trail, Codex skill, agent skill, static site, Cytoscape, Python
- **中文关键词**：科研工作流、实验谱系、实验追溯、证据链、可复现研究、科研仓库整理、AI 智能体技能、Codex 技能

## TL;DR

> AutoResearch: reusable agent skills for research. Its first module, TrackStudy, turns a messy research repo into a verified, clickable map of how your experiments connect.

## Link

- GitHub: https://github.com/holamochi/Auto-Research
- Similar projects:
  - MLflow (experiment tracking and ML lifecycle): https://github.com/mlflow/mlflow
  - DVC (data versioning and ML experiments): https://github.com/treeverse/dvc
  - Aim (open-source experiment tracker): https://github.com/aimhubio/aim

## License

Unless a module states otherwise, this repository is released under the [MIT License](LICENSE).
