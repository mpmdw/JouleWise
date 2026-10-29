# BY-THERM-LINES

Branch: `codex/2026-10-28-by-therm-lines`, based on `ee4ce93fc`.
Authority: registration §21 item 3 and §7; activation `bde918c1`.

## Changes

Added `scripts/bytes_thermal_lines.py` with `hull-p2` and `request-end-p1`:

```
python3.13 scripts/bytes_thermal_lines.py hull-p2 ARCHIVE NEW_OUTPUT [--export EXPORT]
python3.13 scripts/bytes_thermal_lines.py request-end-p1 ARCHIVE NEW_OUTPUT [--export EXPORT]
```

The output contains a modified `derived/b6-acceptance.json`, an optional
`export/SESSION.runs.csv`, and `thermal_line.json`. The record includes the exact
line label, input SHA-256 digests, producing Git commit, changes, notices, and
restored/dropped members and units. Unit lists contain run ids only; member drops
include codes. The unchanged analysis remains responsible for record validity,
whole units, minimum counts, NEG-8, arithmetic, and pass combination.

Acceptance edits replace only `excluding`. CSV edits replace only the raw
`exclusion_codes` field. Other CSV fields retain their exact quoting, separators,
newlines, and bytes. Measurement JSON subtrees are skipped lexically without
numeric decoding. No measurement value enters the record or stdout.

## Decisions I made

- Use sealed `withheld/spans.json`, expressly permitted by the brief, rather than
  reopen member metadata or call `member_spans` again.
- Use the harvest's resolved `derived/harvest-thresholds.json` thermal gap value.
  Replay that thermal projection through production `resolve_thresholds`;
  missing nonthermal keys concern joins this tool never performs. There is no
  new default or resolution against mutable live registration files.
- Call production `read_monitor_journal` and `thermal_member_flags` directly.
  Their production bracketing and threshold arithmetic are unchanged. The tool
  introduces no floating comparison or tolerance.
- Report missing spans/journals and unchanged references. Preserve full-hull
  decisions for absent request spans. Refuse before writing if request-end would
  add an OS exclusion, CSV codes disagree with archive codes, a changed member
  is absent from the CSV, or an archived pass identity contradicts the command.
- Require a new output directory and reject overlap in either direction with
  either source. Link unchanged archive files without opening measurement files;
  keep the source available when analyzing the output. The output is a linked
  analysis view, not an independently portable archive. Reprocessing a linked
  CSV replaces its destination link before writing.
- Report restoration eligibility from exclusion codes only. Do not claim a
  numeric result or bypass the analysis's remaining validity checks.

## Verification

With `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, Python 3.13:

- `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 8 passed.
- `python3.13 -m unittest tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`:
  198 tests passed, 11 skipped. Existing non-pass-2 byte-identity replays passed.
- `python3.13 -m unittest tests.test_battery_float_sweep -q`: 5 passed;
  no registry edit required.
- `git diff --check`: passed. Fixture orphan census: `[]`, count 0, exit 0.

Tests cover thermal additions/removals, whole-quad analysis, retained battery
codes, inside-request exclusions, null/unavailable/reference records, clean-pack
identity, CSV/archive agreement, opaque JSON/CSV measurement values, byte
preservation, idempotence, overlap refusal, and monotonicity refusal.
The full suite was left to CI as instructed.

The tests deliberately distinguish two fixtures: real session harvests from
`tests.b6.test_bytes_p2_thermal_window` / `tests.test_harvest_b5_window`, and the
existing complete BYTES campaign/export fixture for valid 50-member analysis
replays. The shared session fixture writes B5 exclusions, so a test adapter
materializes those production member decisions in the B6 acceptance wire shape.
Its documented cooldown-isolation catalog is used. Special null/journal/reference
records are injected into synthetic harvested archives. Consequently these tests
do not establish a single uninterrupted real-B6-harvest-to-analysis chain for
all requested cases; that stricter fixture integration remains a coverage gap.

## Scope and limitations

Only the requested script, test module, and this report changed. No registry
change was necessary. No real BYTES data or hardware was used. Neither
`harvest.py` nor `bytes_analysis.py` changed. The analysis SHA-256 remains
`18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`.

The script refuses unavailable archived journals and incomplete/mismatched
exports rather than inventing decisions. An export with changed science rows
held outside its runs CSV must first supply those rows in the analysis input;
the tool does not open hidden stores or rewrite their sidecars.

No scientific ruling is requested. The implementation is delivered, with the
fixture-integration and hidden-store limitations above explicitly outstanding.

## Commits

- `52eda2ee9`: implementation; pushed.
- `4f1b9b8cf`: implementation refinements and tests; pushed.
- This report is committed and pushed separately as the final step.

Next exact step for complete acceptance: add an uninterrupted real B6 harvest,
transform, and valid 50-member analysis fixture covering the requested cases;
confirm the export ingress contract for changed rows held outside `*.runs.csv`.
