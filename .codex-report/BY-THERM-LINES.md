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

## Fix round 1

Implemented lead rulings T1–T7 from activation `bde918c1` on the requested branch, starting at `5d80e12cd`. This section supersedes the earlier hidden-store and fixture-coverage limitations.

- Grouped exports now copy their sidecar and already-offset withheld store, rewrite codes and exporter-style `excluded` booleans in both CSVs, and retain opaque measurement bytes. Withheld members carry `not defined at blinded stage (row withheld)`; post-commit analysis retains their models.
- Former journal, export disagreement, absent-member, and pass-mismatch refusals now write per-line and per-member statuses with exit 0. Independently evaluable members still receive their decisions. Source overlap and request-end-would-add remain stops.
- Request-end checks the journal against the harvest's sealed SHA-256, accepts compressed journals, and records journal mismatches without restoring affected members. Hull evaluation does not read the journal.
- Outputs include a payload manifest with relative paths, sizes, and SHA-256 digests. `verify OUTPUT` lists every differing path or prints `view verified`, records `records.thermal_view_changed`, and exits 0. Keep the linked source available and verify the view before analysis. Modified files are copies with mode 0444. Producing commit and tracked-tree dirty state are recorded.

Decisions I made:

- Name the copied private store `SESSION.withheld.csv`: the unchanged analysis recursively discovers `*.runs.csv`, so retaining that suffix would double-load held-out rows before the commit. The expanded census test caught this during the fix.
- Keep undefined members' archive and CSV codes independently unchanged; never reconcile disagreement with a union or intersection.
- Supply zero only as the production thermal helper's unused gap argument. It affects solely the discarded `thermal.unmeasured` projection, so missing gap thresholds require no refusal and cannot change OS-code decisions.
- Exclude the manifest and `thermal_line.json` control files from the payload census to avoid cyclic self-hashing; bind the manifest's exact SHA-256 in `thermal_line.json`. Verification checks that binding as well as every exposed payload file.
- Record file modification stamps and inode identities as well as size and hash. A deterministic real re-acceptance can replace linked flags with identical bytes; its replacement still needs to be disclosed by `verify`. These are exact integer metadata comparisons and never affect membership.
- Retain the complete reviewer campaign and all real-harvest variants. There is no existing optional slow-test convention in this module. Counting acceptance is not fabricated: the real chain verifies exact cross-pass codes, while the campaign fixture separately verifies analysis.

Verification (Python 3.13, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`):

- `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 19 tests, OK. The final damaged-manifest addition was also checked by rerunning all 9 `RecordedFaultTests`, OK.
- `python3.13 -m unittest tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`: 198 tests, OK (11 skipped). Pass-1, block-5, and alpha byte-identity replays passed.
- `git diff --check`: passed. JSON/CSV sentinels, including withheld rows, remain opaque; real re-acceptance and changed reductions are reported by the verifier.

Both reviews and all six repro scripts were read and executed before and after the fix. Sol's final campaign censuses match: s2 100/100 and s5 50/50, on both passes. Opus's original chain changes from 23/24 to 22/24 because it still expects pass mismatch to refuse and all linked files to reject writes; the port replaces these with the ruled exit-0 status, modified-copy mode, and manifest checks. Its numerical/code checks still pass. The original linked-mutation probes still demonstrate mutable links; the new verifier detects that drift. The strengthened real-chain port passes 29/29 checks, including a strictly interior integer-stamped read. The grouped analysis port adds real assertions to the reviewers' informational checks, including every-session census at both stages and the s5 held-out line.

No tolerance or new agreement bar was introduced; primary policy, harvest, and analysis remain unchanged. The analysis SHA-256 remains `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`; harvest remains `2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744`. Only the three authorized files changed. No hardware or real BYTES measurements were used. No NEEDS_RULING remains.

Fix commits, each pushed: `22bc6039c`, `338ab1a07`, `3ed2ca65c`, `b904908b8`, `4c04bcda1`, `b4038dc40`; this report is the final separate commit.

Draft PR: https://github.com/mpmdw/JouleWise/pull/598 (target `lane/2026-10-28-bytes-pass2-open`).

CI is running on the PR. Earlier implementation runs passed build, fences, and installed-wheel checks. The whole-suite result remains pending and is not claimed green. The final report push may supersede that run; the PR checks show the current head.


## Fix round 2

Implemented U1–U4 for activation `bde918c1`, starting at `e23cd1e7b`, using the Sol delta review and nine scripts pinned at `3e95b69a39`.

- U1: require a new output directory, including refusal of dangling output symlinks, before any writes. Check destination directories before creating or replacing payloads; refuse symlinks and paths resolving inside sources. Existing outputs cannot retain or certify stale exports.
- U2: absent journal provenance records `records.thermal_journal_provenance_unavailable`. Would-be restorations retain their original codes and receive `not defined (journal provenance unavailable)`, with exit 0. Matching and mismatching sealed digests retain their T3 behavior.
- U3: validate the manifest container, entries, normalized unique relative paths, sizes, hashes and integer identity stamps. Missing, invalid JSON, deeply nested or structurally damaged manifests complete the flag write with `records.thermal_view_changed`, a reason, and exit 0.
- U4: all four delta findings are fixed. The review's remaining first-round dispositions remain governed by T1–T7. No NEEDS_RULING remains.

Decisions I made:

- Keep inode/mtime checks on linked source payloads, where they detect byte-identical re-acceptance. Copied payloads use exact sizes and SHA-256 hashes, so two fresh outputs from the same inputs produce byte-identical manifests and change lists. The tests compare both byte for byte; no same-output rerun is supported.
- Bind the deliberately injected campaign journals to explicit synthetic provenance seals in the tests. Keep missing-provenance tests separate; never manufacture provenance in the tool.
- Replace the verifier's control record without chmodding through a possible file symlink. Measurement fields remain opaque; code, count, integer-stamp and hash comparisons remain exact. No float tolerance or numerical bar was introduced.

All nine pinned review scripts were rerun before and after the fixes: `sol_campaign.py`, `sol_probes.py`, `sol_chain.py`, `opus_chain_test.py`, `opus_chain_analysis.py`, `opus_probe_postcommit_heldout.py`, `campaign_delta.py`, `view_and_gap.py`, and `delta_probes.py`. The optional byte-identical real re-acceptance replay also passes on both implementations. Logs and synthetic fixtures stayed outside the repository.

Before fixing, the delta reproduced source mutation, stale export certification, restoration without provenance and a verifier crash. Afterwards, the original delta script records the required missing-provenance status and then stops at the newly required existing-output refusal. The original Sol probe stops at its obsolete unsealed-restoration assertion. Regression tests independently exercise every subsequent fault, including source byte preservation, stale-output refusal and damaged-manifest exit 0. The original Opus chain remains 22/24 because its pass-mismatch-refusal and linked-file-write-protection expectations were superseded by T1–T7. The other six scripts complete; grouped analysis remains 30/30, censuses and heldout models survive, and the strengthened campaign tests supply matching provenance for their intended restorations. T7's real-chain non-counting limitation remains explicit.

Verification used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1` and `PYTHONDONTWRITEBYTECODE=1`:

- `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 24 tests, OK; strengthened real-chain port 29/29 and grouped-analysis port 30/30. Final edge-case refinements were checked with all 15 `RecordedFaultTests`, OK, including the subsequently added dangling-link test.
- `python3.13 -m unittest tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`: 198 tests, OK (11 skipped). Pass-1, block-5 and alpha byte-identity checks pass exactly.
- `git diff --check`: passed. The full repository suite is left to CI because this change is confined to the exclusion-only tool and its tests.

Only the three authorized files changed. No hardware or real BYTES measurements were used. Analysis SHA-256 remains `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`; harvest remains `2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744`.

Fix commits, each pushed: `ad3b497d8`, `c9dcee9dd`, `7beee5ed9`, `0f164a1d5`, `cd91fd2c9`, `edafd77e5`. This report is committed and pushed separately. PR #598 remains a draft. The final-head CI job snapshot is read after that push and reported with the handoff; no completed green whole-suite result is claimed.
