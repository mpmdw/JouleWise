# Capstone report source (RPT-001 vertical slice + RPT-002 literature)

Canonical report source per `docs/specs/c027/rpt-001_report_vertical_slice.md`:
Pandoc-compatible Markdown, assembled by a stdlib-only script into one
deterministic Markdown document. No LaTeX/Pandoc/PDF engine is part of the
build gate; the final renderer is a P1-008 decision behind the
`format_adapter` seam in `report.json`.

## Layout

- `report.json` — report profile: ordered chapter manifest + format-adapter seam.
- `references.csl.json` — canonical offline CSL bibliography.
- `source_map.json` — seven-source RPT-002 evidence/verification map; all
  intake records were `VERIFIED_AGAINST_PRIMARY` by the lead on 2026-07-11.
- `chapters/`, `appendices/` — authored prose (edit these).
- `generated/` — build outputs inside the source tree (do NOT edit; first
  line carries a GENERATED marker).
- `report.md` — human-readable pointer to the manifest.

## Build / regeneration

One command re-derives the dataset, aggregates, figure F1, tables T1/S1, the
claims-index row, the generated results page, and the assembled report:

```sh
python3 scripts/build_capstone.py --profile rpt001 --full --offline \
  --runs-root runs
```

Requires the six pinned legacy bundles under `runs/` (local-only, ~110 MB,
gitignored). The assembled document lands at
`build/capstone/rpt001/report.md` (untracked). Source-only `--check`
regenerates from tracked analysis and report sources, compares the committed
generated page, validates assembly in memory, and exits 2 on drift. It neither
requires `runs/` nor uses the untracked assembled document as a reference. If
your bundle corpus lives elsewhere, pass that path to `--runs-root`; committed
artifacts always store repo-relative paths.

To re-pin input hashes after an intentional corpus change (this is a
versioning event — see the spec's rpt001-v2 rule):

```sh
python3 scripts/make_figures.py --runs-root runs \
  --bootstrap-input-manifest
```

## Evidence boundary

All current results content is **legacy L1 (manual review; pre-2M)**:
stack-specific instrument observations from six legacy bundles, n=3 per
exact stack. No cross-stack comparison, efficiency ranking, or scaling claim
is made anywhere in this source tree, and the assembler fails the build on a
small forbidden-phrase list.

## Bibliography verification boundary

The original eleven-source survey inherits its 2026-07-06 verification record
from `docs/phase_4/related_work_draft.md`. The lead verified all seven RPT-002
sources against primary records on 2026-07-11. `references.csl.json` contains
the corrected metadata; each source-map entry records the verified primary
URLs, retrieval date, scope boundary, claim wording, artifact status, and
completed primary-paper checks.

The assembler parses both JSON files, validates their structure, checks all
Pandoc citation keys offline, and requires the seven intake records to retain
an explicit recognized verification state.

## Known gaps vs the full RPT-001 spec (vertical slice, time-boxed)

- `{{jw:include-section}}` contract transclusion: not implemented; the
  assembler supports whole-file `{{jw:include path="..."}}` only. Chapters
  reference contracts instead of mirroring exact wording.
- `claims_lint --mode phase4` and the generated
  `docs/phase_4/claims_index.md` view: not yet implemented.
- Offline (`--offline`) CI build mode and the CI hook: not yet wired.
