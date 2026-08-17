# TrackStudy

TrackStudy turns scattered code, reports, notes, run metadata, and result files into a traceable experiment map. It is derived from the workflow used to build the BioStitch Research Atlas, but contains no BioStitch-specific experiments or metrics.

## What it produces

```text
research repository
  -> source inventory
  -> stable experiment IDs
  -> concise and detailed experiment narratives
  -> evidence-backed relationships
  -> path / line-range / SHA validation
  -> deterministic browser data
  -> static experiment atlas
```

The bundled web template provides:

- a top-down experiment tree;
- visible relationship labels;
- compact numbered nodes with full experiment IDs;
- click-to-read summaries;
- double-click detailed changes, conclusions, caveats, and evidence;
- track filters, search, theme switching, and fit-to-canvas controls;
- `file://` and local HTTP operation without a backend.

## Why this is both a Skill and a Plugin

The reusable workflow lives in the `track-study` Skill. The surrounding plugin manifest makes the Skill distributable without coupling it to an MCP server, external account, or hosted service.

```text
TrackStudy/
├── README.md
├── track-study/                    # installable Codex plugin
│   ├── .codex-plugin/plugin.json
│   └── skills/track-study/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── scripts/
│       ├── references/
│       └── assets/web-template/
├── examples/minimal-study/         # generated working example
└── tests/
```

## Quick start

> **Which page should I open?**
>
> `track-study/skills/track-study/assets/web-template/` is an unbuilt template.
> Its `data/study.js` intentionally contains `window.TRACKSTUDY_DATA = null`, so
> opening that template directly displays “TrackStudy data is missing.” To see a
> working atlas immediately, open `examples/minimal-study/web/index.html`. For a
> new study, run `build_atlas.py` first and then open that study's
> `web/index.html`.

Set the script directory once:

```bash
TRACKSTUDY=TrackStudy/track-study/skills/track-study
```

Create a new study workspace:

```bash
python3 "$TRACKSTUDY/scripts/init_study.py" my-study
```

Edit `my-study/study.json` and `my-study/experiments/*.json`, then build and validate:

```bash
python3 "$TRACKSTUDY/scripts/build_atlas.py" my-study
python3 "$TRACKSTUDY/scripts/validate_study.py" my-study
```

Open `my-study/web/index.html` directly, or preview it over HTTP:

```bash
python3 -m http.server 8000 --directory my-study
```

Then open `http://127.0.0.1:8000/web/`. Serve the study root—not only
`web/`—so links from a dossier to its cited evidence remain resolvable.

## Install the Skill

After this repository is published, ask Codex:

```text
$skill-installer install https://github.com/ShiLong-CN/AutoResearch/tree/main/TrackStudy/track-study/skills/track-study
```

The plugin wrapper is located at `TrackStudy/track-study/` for plugin-aware distribution.

## Source-of-truth rules

1. Treat code, immutable run metadata, and formal reports as evidence; treat the atlas as a generated view.
2. Create stable IDs before writing relationships.
3. Require evidence for every claim and every non-structural relationship.
4. Do not promote directory order, experiment numbering, shared implementations, or temporal proximity into causal edges.
5. Preserve negative, blocked, and incomplete experiments rather than collapsing them into success/failure.
6. Regenerate the web data after every source change and require validation to pass.

## Verification

From the repository root:

```bash
python3 -m unittest discover -s TrackStudy/tests -v
python3 TrackStudy/track-study/skills/track-study/scripts/validate_study.py TrackStudy/examples/minimal-study --check-built
node --check TrackStudy/track-study/skills/track-study/assets/web-template/assets/app.js
```

Plugin and Skill manifests are additionally checked with the Codex plugin and skill validators during development.

## Boundaries

- TrackStudy validates the existence and integrity of cited evidence; it does not decide whether a scientific interpretation is true.
- Generated relationship suggestions remain drafts until a researcher confirms them against source evidence.
- A successful static validation does not replace browser interaction and visual checks.
