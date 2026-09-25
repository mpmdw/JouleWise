# Spotlight: the 09-17 exclusions work, but they miss the per-night measurement clones

2026-09-25 ≈02:10 PDT, prompted by Ed ("thought we fixed this by excluding it from spotlight").

## Executed checks (`mdfind -onlyin <dir>` with exact-name queries)

| Location | Indexed | Notes |
|---|---|---|
| `~/code` | 0 README.md hits | excluded 09-17; exclusion works |
| `~/night-archive` | 0 | excluded 09-17; works |
| `~/night-custody` | 0 | excluded 09-17; works |
| `~/JouleWise-measurement-*` (26 per-night clones, 2026-08-13 … 09-23) | **2,062–2,337 JSON files each, i.e. all but 6** | **NOT excluded.** Every night's fresh clone is indexed |
| `~/osctx-mvp-01` (tonight's diagnostic data root) | 46/46 summary files | not excluded; the lead's own placement error |
| `~/jw_models` | indexed | static weights: a one-time cost |

- A folder whose name ends in `.noindex` **was still indexed** on macOS 26.6.2 (25G83): a probe file was found within 45 s in both a plain and a `.noindex` folder. The name-suffix convention cannot be relied on here.
- `corespotlightd` (30 % of a core in one idle segment in session C) indexes content that apps donate (Mail, Messages, Notes and similar). Folder exclusions do not cover it. The file-indexing daemons are `mds`/`mds_stores`/`mdworker`.

## Why it matters

Each unattended night creates a fresh repository clone of ≈ 2,300 JSON files (plus code), shortly before the window. Spotlight then indexes it, and fseventsd has to log the file burst. That is a systematic, night-correlated background load inside the measurement period, the kind of contamination the quiet-machine gates exist to exclude.

## Proposed cure (for the magistrate's gated process)

Create measurement clones **under an already-excluded parent**, e.g. `~/night-custody/measurement/<stamp>/`, instead of `~/JouleWise-measurement-<stamp>`. This is a path change in the clone location used by evidence-night prepare, and it needs no GUI and no sudo. Alternatively, add a new dedicated parent (e.g. `~/jw-measure/`) to the Spotlight privacy list once, via System Settings (agent computer use, as on 09-17), and create clones inside it.

Future OSCTX runs should write under `~/night-archive/`.
