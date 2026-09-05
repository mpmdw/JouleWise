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

Source-only assembly and `--check` are reproducible from a pristine clone:

```sh
python3 scripts/build_capstone.py --profile rpt001 --offline --check
```

This path uses only tracked analysis and report sources. It compares the
committed generated page, validates full-report assembly in memory, and exits
2 on drift. It neither requires `runs/` nor uses the untracked assembled
document as a reference.

The controlled/internal full route is not a clean-clone or external
reproducibility claim. The following command authenticates the retained
historical inputs, then regenerates only void placeholders for the dataset,
aggregates, figure, and tables, plus the retained claims-index row with status
`voided`. It never re-derives or emits the corpus's measurement values:

```sh
python3 scripts/build_capstone.py --profile rpt001 --full --offline \
  --runs-root runs
```

It requires controlled access to the six pinned legacy bundles under `runs/`
(internal, ~110 MB, gitignored). Neither the pristine clone nor the
privacy-transformed public projection supplies strict-valid, independently
re-reducible replacements for that corpus. The assembled document lands at
`build/capstone/rpt001/report.md` (untracked). If the controlled corpus lives
elsewhere, pass that path to `--runs-root`; committed artifacts always store
repo-relative paths.

To re-pin input hashes after an intentional corpus change (this is a
versioning event — see the spec's rpt001-v2 rule):

```sh
python3 scripts/make_figures.py --runs-root runs \
  --bootstrap-input-manifest
```

## Evidence boundary

The legacy corpus is **VOIDED permanently for claim use**, as stated in the
[root README](../../README.md#current-state). The generated results page is a
historical pipeline demonstration only: it emits no energy-result table,
energy values, or rendered result figure. The immutable historical derived
artifacts remain under `analysis/rpt001-v1/` and `figures/rpt001-v1/`; the v2
paths contain regenerated void placeholders only.

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
- A final PDF renderer remains pending the P1-008 format-adapter decision.
