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


## Fix round 3

Activation `1cc172c8`, 2026-10-29. Continued `ad0bb794d` on `codex/2026-10-28-by-therm-lines`; input review/probes are JouleWise-data `9cc245015`, `by-therm-lines-delta-opus/`. Implemented V1–V6; Opus 7 remains outside this round.

- V1: hull unavailability keeps an existing OS code determined and marks a science member without it `not defined (hull assessment unavailable)`. Request-end's removal direction is preserved. Either pass mismatch marks every science member `not defined (pass mismatch)`. Equality requires all science members determined and equal. Tests cover both directions, both fault kinds, and individual unavailable hull records.
- V2: empty CSVs and missing code columns preserve their bytes, record undefined science statuses, and exit 0. A missing hull `journal_available` is an unavailable assessment. Unavailable Git metadata records both producer fields as null. Journal mismatch/provenance is checked before would-add: affected members keep their codes and receive the records-fault status. A matching-seal would-add still stops before creating output.
- V3: U3 had covered damaged manifests, but not the thermal record. Missing, unparsable or invalid thermal records now list `thermal_line.json`, reconstruct a flagged record, and exit 0.
- V4: confirmed U2 already handles absent `derived/window_flags.json` with `records.thermal_journal_provenance_unavailable`; retained that exact code and status. The original probes and regression tests confirm it.
- V5: empty code fields are unquoted empty fields. A withheld-copy regression compares the entire CSV against the exporter's `csv.DictWriter` with its exact parameters, including CRLF and opaque quoted fields.
- V6: verification rehashes every recorded source, including copied acceptance/export inputs, records `source_differing_paths`, sets the view-change flag, and prints `source changed since transform: <path>`. Changed and missing sources exit 0.

Decisions I made:

- Apply the hull direction to missing per-member assessment fields, null exclusions and unavailable journals as well as missing assessment files: an existing code remains determined; an absent code cannot be certified equal.
- Treat an invalid CSV header or row structure as an export records fault for every science member because the table cannot establish member/code agreement. Preserve the input CSV bytes and roll back proposed changes for those members.
- Apply the same provenance-unavailable protection to an apparent would-add as to an apparent removal. Only a matching seal can justify the would-add stop. Missing-request-span behavior remains the registered full-hull fallback.
- Keep U1's existing-output refusal and overlap protections. `probes_delta.py` already uses a fresh output directory for every transform, including `o2` after a journal change and separate `t4cN/o` cases. Therefore the adaptation for U1's new-output rule is the identity adaptation: no script changes were needed. Both executions used the exact pinned script in memory with `JW=/workspace/JouleWise`.
- Source freshness shares `records.thermal_view_changed` but has a separate source-path list; view-relative differing paths retain their existing meaning. A damaged record loses its bindings, so verification also flags the manifest/payload paths it can no longer certify.

Every probe line is recorded below. Temporary roots alone are normalized to `$TMP`; the probe's CLI helper prints only the last stdout/stderr line, so `withheld/spans.json` can be the tail even when the full output also lists a damaged control file.

Before (`ad0bb794d`):

```text
PROBE T2 export-without-exclusion_codes-column (2, "'exclusion_codes' is not in list", False)
PROBE T2 empty-public-csv (1, 'IndexError: list index out of range', False)
PROBE T2 withheld-store-absent (0, '}', 'not defined (journal provenance unavailable)', ['not defined (journal provenance unavailable)', 'equals registered line'], ['s.runs.csv', 's.session.json'])
PROBE T2 hull-record-missing-journal_available (1, "KeyError: 'journal_available'", False)
PROBE T3 no-window_flags.json (0, '}', ['records.thermal_journal_provenance_unavailable', 'records.thermal_line_undefined'], [])
PROBE T3 sealed-journal-null (0, '}', ['records.thermal_journal_provenance_unavailable', 'records.thermal_line_undefined'], 'not defined (journal provenance unavailable)')
PROBE T3 mismatch-and-would-add (2, 'request-end would add thermal.os_level_nonzero: a', False)
PROBE T3 matching-seal (0, '}', ['a'], 'evaluated')
PROBE T3 one-byte-journal-change (0, '}', [], "not defined (journal differs from the harvest's)", [])
PROBE T4 modes-of-copies {'thermal_line.json': '0o444', 'view_manifest.json': '0o444', 'derived/b6-acceptance.json': '0o444'}
PROBE T4 baseline (0, 'view verified')
PROBE T4 identical-bytes-new-inode (0, 'withheld/reductions/a.json')
PROBE T4 identical-bytes-touch-only (0, 'derived/roster.json', 'flag=True')
PROBE T4 deleted-linked-source (0, 'withheld/spans.json', 'flag=True')
PROBE T4 added-file-in-view (0, 'derived/extra.json', 'flag=True')
PROBE T4 deleted-file-in-view (0, 'derived/roster.json', 'flag=True')
PROBE T4 manifest-not-json (0, 'withheld/spans.json', 'flag=True')
PROBE T4 manifest-deleted (0, 'withheld/spans.json', 'flag=True')
PROBE T4 manifest-files-list-of-ints (0, 'withheld/spans.json', 'flag=True')
PROBE T4 thermal_line-deleted (1, "FileNotFoundError: [Errno 2] No such file or directory: '$TMP/t4c7/o/thermal_line.json'", 'flag=FileNotFoundError')
PROBE T4 thermal_line-not-json (1, 'json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)', 'flag=JSONDecodeError')
PROBE T4 source-acceptance-only-changed (0, 'view verified', 'flag=False')
PROBE T4 source-export-rewritten-after-transform (0, 'view verified')
PROBE BLIND decoded-sentinels []
PROBE BLIND sentinels-in-stdout-or-record []
PROBE BLIND withheld-copy-bytes (False, 1)
PROBE BLIND sidecar-copy {"operative_bound_s": 645192837.465564, "blinding": {"withheld": {"path": "withheld/s.withheld.csv", "row_count": 1}}}
PROBE T3 gap-independence {'comparisons': 24000, 'os_decision_differs': 0, 'comparisons_with_unmeasured_holes': 19486}
```

After (`08e66102c`):

```text
PROBE T2 export-without-exclusion_codes-column (0, '}', True)
PROBE T2 empty-public-csv (0, '}', True)
PROBE T2 withheld-store-absent (0, '}', 'not defined (journal provenance unavailable)', ['not defined (journal provenance unavailable)', 'equals registered line'], ['s.runs.csv', 's.session.json'])
PROBE T2 hull-record-missing-journal_available (0, '}', True)
PROBE T3 no-window_flags.json (0, '}', ['records.thermal_journal_provenance_unavailable', 'records.thermal_line_undefined'], [])
PROBE T3 sealed-journal-null (0, '}', ['records.thermal_journal_provenance_unavailable', 'records.thermal_line_undefined'], 'not defined (journal provenance unavailable)')
PROBE T3 mismatch-and-would-add (0, '}', True)
PROBE T3 matching-seal (0, '}', ['a'], 'evaluated')
PROBE T3 one-byte-journal-change (0, '}', [], "not defined (journal differs from the harvest's)", [])
PROBE T4 modes-of-copies {'thermal_line.json': '0o444', 'view_manifest.json': '0o444', 'derived/b6-acceptance.json': '0o444'}
PROBE T4 baseline (0, 'view verified')
PROBE T4 identical-bytes-new-inode (0, 'withheld/reductions/a.json')
PROBE T4 identical-bytes-touch-only (0, 'derived/roster.json', 'flag=True')
PROBE T4 deleted-linked-source (0, 'source changed since transform: $TMP/t4c1/archive/withheld/spans.json', 'flag=True')
PROBE T4 added-file-in-view (0, 'derived/extra.json', 'flag=True')
PROBE T4 deleted-file-in-view (0, 'derived/roster.json', 'flag=True')
PROBE T4 manifest-not-json (0, 'withheld/spans.json', 'flag=True')
PROBE T4 manifest-deleted (0, 'withheld/spans.json', 'flag=True')
PROBE T4 manifest-files-list-of-ints (0, 'withheld/spans.json', 'flag=True')
PROBE T4 thermal_line-deleted (0, 'withheld/spans.json', 'flag=True')
PROBE T4 thermal_line-not-json (0, 'withheld/spans.json', 'flag=True')
PROBE T4 source-acceptance-only-changed (0, 'source changed since transform: $TMP/t4c9/archive/derived/b6-acceptance.json', 'flag=True')
PROBE T4 source-export-rewritten-after-transform (0, 'source changed since transform: $TMP/t4x/export/s.runs.csv')
PROBE BLIND decoded-sentinels []
PROBE BLIND sentinels-in-stdout-or-record []
PROBE BLIND withheld-copy-bytes (True, 1)
PROBE BLIND sidecar-copy {"operative_bound_s": 645192837.465564, "blinding": {"withheld": {"path": "withheld/s.withheld.csv", "row_count": 1}}}
PROBE T3 gap-independence {'comparisons': 24000, 'os_decision_differs': 0, 'comparisons_with_unmeasured_holes': 19486}
```

Verification used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, synthetic fixtures only, no hardware or real BYTES data. Comparisons remain exact on codes, counts, integer stamps and hashes. No tolerance or numerical bar was introduced. The randomized gap probe exercises pre-existing production gap behavior; it adds no tool threshold.

- `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 33 tests, OK, 515.889 s; grouped analysis 30/30 and real harvest/acceptance chain 29/29, including compressed journals.
- `python3.13 -m unittest tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`: 198 tests, OK, 11 skipped, 713.242 s. Pass-1, block-5 and alpha byte-identity checks each compare 177 files exactly.
- Final focused `RecordedFaultTests`: 23 tests, OK. `git diff --check`: passed. The full repository suite is delegated to CI because this scope is confined to the exclusion-only tool and its regressions.

Analysis SHA-256 unchanged: `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`.
Harvest SHA-256 unchanged: `2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744`.

Each implementation step was committed and pushed: `7da248861` (V1), `73ccf920d` (V2), `08e66102c` (V3/V5/V6; V4 confirmed already closed). This report is a separate commit. Only the three authorized files changed. No NEEDS_RULING remains. PR #598 stays draft; final-head CI is read after the report push and every job's state is reported in the handoff. No all-green CI claim is made in this section.


## Fix round 4

Activation `1cc172c8`, 2026-10-29; continued `574f13d2f` on `codex/2026-10-28-by-therm-lines`, draft PR #598. Implemented W1–W6 in `2017aa309`, the required-span-field refinement in `e59fd06ba`, and invariant-member pass-mismatch disclosure in `8013ce085`, each committed and pushed; this report is a separate committed and pushed step.

- One shared `member_status` predicate now determines every science member from direction, original OS-code presence and evidence trust. Untrusted evidence preserves original codes regardless of candidate agreement. Only the direction-invariant members remain equal. Line equality requires every science member determined and equal.
- Hull exclusions require actual bool or null; null remains unavailable. Missing, malformed or mismatched pass identity is untrusted in both directions. The five W4 faults write affected-member undefined records and exit 0. Invalid CSV bytes are preserved, and its fault reason survives on changed members.
- Verification validates all control fields it consumes, reports damaged records as `thermal_line.json` differing, and completes the flag. It reads through resolved output links, writes only outside recorded sources, prints the flag without source writes otherwise, and leaves nonexistent outputs absent with `output missing`. Opus 7 remains unchanged by design.

Decisions I made:

- W1 supersedes the earlier all-member pass-mismatch status and candidate-dependent provenance checks: direction determines the invariant members even for these faults. An informational pass-mismatch notice remains visible even when every member is invariant. W4 structural/export faults still make every affected member undefined.
- Keep a missing roster identity as null in the record, never invent a run id; inability to join that roster conservatively affects its science members. A missing exclusion code with a known run id affects that member only.
- Keep §21's full-hull fallback for an explicitly absent (null) request span. A missing per-member span record or required span field is unavailable evidence. Keep the production journal parser and thermal helper's existing interpretation; introduce no estimator or threshold.
- Hull uses the archived harvest assessment, without reopening a journal or requiring a new seal. The generated hull journal/seal-unavailable cells exercise the assessment's unavailable-journal field; request-end cells damage the actual journal seal.
- Retain U1's new-output refusal and source-overlap protections. Give analysis-only positive fixtures explicit synthetic pass identities. Preserve and rerun the original review scripts; separately label the W3 positive-fixture ports rather than silently treating their old assumptions as passing.

Inputs: Sol review `d332aefca` and Opus review `3f0b7ce`. Read both complete reviews and their supplied scripts. Reran `independent.py`, `probes_v.py`, and all three `adapted/` Python repros before and after. Baseline reproduces the false equality, integer-bool acceptance, remaining stops and verifier crashes. Final fault repros complete with the ruled statuses/exit codes. The unchanged sealed Sol positive probe now fails its restoration assertion because it has no pass identity; the unchanged sealed census prints eight target/status failures for that same reason, with no census failure. Explicit W3 identity ports give `PROBES_PASS` and `SUMMARY fails []`. The U1-adapted delta probe completes and preserves sources.

Verification: Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`; synthetic only, no hardware or real BYTES data.

- Final `RecordedFaultTests`: 26 tests, OK. Includes 144 real-CLI cells: both directions × both original-code states × candidate agreement/difference × nine fault kinds, each paired with its trusted control. Assert exact status, kept codes, recorded drops and line equality; trusted request-end would-add controls assert the ruled stop before output.
- The initial `python3.13 -m unittest tests.test_bytes_thermal_lines tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q` ran all 234 tests in 1220.782 s (11 skipped). The 198 harvest-module tests had no failures (11 skipped); two thermal assertions failed on intermediate code: missing legacy hull notices and the superseded pass-mismatch assertion. Both were corrected. Final `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 36 tests in 615.906 s, OK; grouped analysis 30/30 and real harvest/acceptance chain 29/29, including compressed journals.
- `git diff --check`: passed. The full repository suite is left to PR-head CI for this exclusion-only tooling change.

Census, source equals output on both passes and both blinded stages:

| Sessions | Public + withheld physical rows | Science before release | Science after release / archive |
|---|---|---|---|
| s2-p1, s2-p2 | 63 + 50 = 113 | 50 = 50 | 100 = 100 |
| s5-p1, s5-p2 | 13 + 50 = 63 | 0 = 0 | 50 = 50 |

The W3 census port also checks exact changed codes, all other row fields, model preservation and the withheld-store read gate.

SHA-256 unchanged:

```text
18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71  joulewise/bytes_analysis.py
2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744  joulewise/b5/harvest.py
```

Only the three authorized files changed. The tool reads no energy value; comparisons remain exact on codes, counts, integer stamps and hashes. No tolerance, numerical bar or NEEDS_RULING was needed. Final-head CI is read after this report's push and every job state is reported in the final handoff; no all-green claim is made here.

## Fix round 5

Activation `4e748ac1`, 2026-10-30. Implemented X1–X12 from the adopted consult (`JouleWise-data` `0858773e`), starting at `9615ea4a1` and applying its prototype first. Read the consult, matrix, ports and logs, and the Opus (`00d85f4b8`) and Sol (`157da571b`) round-4 reviews and scripts.

Every source now passes through its validator before consumption. JSON validation covers the whole document, uses an explicit stack, rejects duplicate decoded keys and invalid lexemes, and leaves unconsumed values opaque. Navigation also avoids recursion. Typed projections, nested spans, the roster-named pack tree and registered-hull journal replay supply the trust reason to `member_status`, the sole science-status writer. Acceptance rows are spliced with retained row bytes intact. Verify uses validated control projections and structural link roots; directory records are flagged on stdout without replacement.

Decisions I made:

- Remove the no-`pack_id` allowance. Fixtures identify their pack and archive its tree under `sources/repo/configs/campaigns/<pack_id>/`. Unrelated trees do not carry the pass; multiple matching trees, unsafe pack names and missing identities are mismatches.
- Apply X3 to consumed exclusion scopes and roster kinds as well as the explicitly listed fields. Invalid scopes, identities and units are W4 records faults; unidentified roster members are represented by null. Missing `excluding` is a W4 global fault under X10, rather than the prototype matrix's extra stop. A known member's missing code remains member-only.
- Preserve the null-request fallback's registered codes while applying X5 to its journal trust. A contradictory replay produces the ruled reason and notice. The matching-seal would-add check retains priority for request-end evaluation.
- Lex each JSONL value before projecting the production parser's consumed fields. Preserve malformed-line skipping, bookkeeping behavior, sorting, error-presence semantics and the unchanged production line parser and thermal flag helper. Unknown journal values, retained acceptance rows and verify control fields remain opaque.
- Treat malformed, unlocatable or unreadable sidecars as an unlocated store; they never stop evaluation. Retain U1's fresh-output invocation precondition. X10 governs source-trust stops for valid new-output invocations.
- Derive link roots by stripping the view-relative depth even when a damaged link changes its target tail. A damaged record cannot erase this structural protection. No numerical tolerance or new scientific bar was needed.

Verification used Python 3.13.5 with `JW_B5_SYNTHETIC_ONLY=1` and `PYTHONDONTWRITEBYTECODE=1`:

- Final `tests.test_bytes_thermal_lines`: **45 tests, OK, 1132.253 s**. Round-4 baseline: **36 tests, OK, 825.356 s**. Runtime remains within 1.5×. Replaced the subsumed, repetitive 144-cell test with the generated 684-cell matrix; retained every real-chain and grouped-analysis variant.
- `tests.b6.test_bytes_p2_thermal_window` and `tests.test_harvest_b5_window`: **198 tests, OK, 11 skipped, 830.706 s**. Pass-1, block-5 and alpha each retain exact 177-file byte identity.
- Consult matrix: baseline **237 failures / 684 cells**; final **684/684**. Expected outcomes come from W1 and fault classes, never tool results. Final Opus matrix: **324/324**. Sol document and fault matrices: **80/80** and **360/360**. Lexer break cases, million-level nesting, span edges, typed identities, null-request replay, sidecar faults and retained-row lexemes pass through the CLI.
- All original and inherited reviewer entry points were replayed before/after, including argument-taking seal/pass/path utilities. Historical failures from superseded refusal/read-only expectations and missing fixture seals/pass identities remain labelled, not claimed as passes. X6 ports change fixture identities/tree locations and the corresponding no-repo deletion; the missing-`excluding` oracle follows X10.
- `ReviewerRealChainTests`: **44/44 checks**, with explicit zero-untrusted-member and zero-replay-disagreement checks on native harvests. Grouped analysis: **30/30 checks**. Guarded sentinels report no decoded measurement sentinels and none in tool stdout/control records; withheld bytes remain intact.

Census, source equals output on both passes:

| Sessions | Public + withheld rows | Science records before stage-1 commit | After commit / archive |
|---|---:|---:|---:|
| s2, p1 and p2 | 63 + 50 = 113 | 50 | 100 / 100 |
| s5, p1 and p2 | 13 + 50 = 63 | 0 | 50 / 50 |

Every model set is preserved at both blinded stages and the archive stage. All four sessions have zero undefined members (113 members per s2 session, 63 per s5 session), exact target change lists, correct withheld labels and verified views.

Discarded interrupted/mixed runs after an environment restart and a rewrite-time parser error. Retained synthetic reviewer fixtures also exhausted `/tmp`; removed only completed session-created fixtures, preserved logs, and reran affected checks. The completed final module and consult matrix use frozen script SHA-256 `e132ea161cabc6e0f8ce1c4fe7fe69087e20f7fa4bf077f8cb4cc77af039856f` at code head `5a91ce575`.

Pinned files remain unchanged:

```text
18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71  joulewise/bytes_analysis.py
2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744  joulewise/b5/harvest.py
```

`git diff --check` passes; fixture orphan census is `[]`, count 0, exit 0. Only the three authorized files changed. Synthetic fixtures only; no hardware or real BYTES data. All 13 code/test checkpoints were committed and pushed; this report is the separate final checkpoint. No NEEDS_RULING remains. CI is checked on the final pushed report commit and its job states are supplied separately in the handoff.


## Fix round 6

Activation `4e748ac1`, 2026-10-30. Continued `3ee2b83f3` on `codex/2026-10-28-by-therm-lines`, draft PR #598. Read the complete Opus delta-4 report/probes at JouleWise-data `e1b61a4d7`, Sol delta-5 report/probes at `2f5ed90ba`, and adopted consult `0858773e`. Implemented A1–A5 within the existing three-file WRITE_SCOPE.

- A1: JSON accepted by the production bytes decoder but rejected by the strict journal lexer makes the whole journal untrusted with `journal line not producer output`. Both-rejected lines retain malformed-skip behavior. Dup-level, NaN-sibling, lone-surrogate and BOM cases cannot restore a member; UTF-16 is also covered. Native real-chain archives now assert equal consumed stamps, status, integer level and malformed counts against `read_monitor_journal`.
- A2: repeated roster run ids, including science/reference collisions, are W4 global records faults. Acceptance bytes and codes remain intact.
- A3: validate the session as a safe single filename component before constructing export paths. Invalid identities produce export records faults, exit 0 and unchanged science codes. The writer checks resolved output containment, including leaf symlinks. External sidecar locators remain supported for reading; the outside sentinel is preserved.
- A4: contain production-helper conversion exceptions at the tool boundary as `journal level conversion unavailable`, under W1. The huge-level probe now exits 0 and writes a record.
- A5: emit `records.thermal_hull_replay_disagrees` only after an actual replay disagrees. Unknown member spans carry `member span unavailable` without that notice.

Decisions I made:

- Use the production bytes decoder as a recognition check on lexer-rejected lines. Numeric callbacks discard tokens and its decoded result is discarded. Consumed evidence still passes through lexical projection and the pinned production parser/helper. Match the interpreter's existing integer-token length rejection by counting digits, without converting opaque values. Keep non-object and other production-rejected lines in the malformed-skip path.
- Apply duplicate-identity faults globally across science members and export-identity faults to all science members in that export. Reject empty session identities and both separator spellings as unsafe filename components. Keep source-side locator resolution independent of destination containment.
- Preserve W1's direction-invariant members for unavailable journal evidence. Keep the matching-seal would-add stop and the source-overlap/new-output safety switches. Unknown spans produce no replay-disagreement notice; helper conversion failures introduce no new numerical interpretation.
- Leave Opus 4 unchanged: lone-surrogate refusal remains; macOS L1 decoding cannot emit that case. Leave Opus 5 unchanged: vertical-tab/form-feed whitespace changes only the malformed-line notice.

Verification used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1` and `PYTHONDONTWRITEBYTECODE=1`:

- `tests.test_bytes_thermal_lines`, alone in the background and waited to completion: **52 tests, OK, 1100.046 s**. All 45 previous tests remain. Round 5 was 1132.253 s; the 1.1× ceiling is 1245.4783 s. Grouped analysis passed **30/30** and strengthened real-chain checks **60/60**.
- `tests.b6.test_bytes_p2_thermal_window` and `tests.test_harvest_b5_window`: **198 tests, OK, 11 skipped, 704.941 s**. Pass-1, block-5 and alpha each retain exact 177-file byte identity.
- Every supplied Opus and Sol Python probe was rerun before and after, including the independent probes and census. The original divergence script stops at the new validator exception before its CLI call; a labelled in-memory adaptation catches that exception and completes all four CLI comparisons, with no restorations. The committed regressions assert the same result. Other probes complete; independent probes pass and the census ends `SUMMARY fails []`. Production-shaped real harvest: 103 equal readings, malformed 1/1, zero undefined members and zero replay disagreement.
- An environment restart interrupted the first full-module attempt; it is not counted as a result. Corrected the native-chain assertion binding before the completed final run. Final logs are retained in `/tmp/round6/final-*.log`; the tested script SHA-256 is `5a8e5fe467276045168605332b19c81dd94489406247d9282223257e1126df19` at code head `a9da7cd02`.

Census, source equals output on both passes:

| Sessions | Public + withheld rows | Science before commitment | After commitment / archive |
|---|---:|---:|---:|
| s2-p1, s2-p2 | 63 + 50 = 113 | 50 | 100 / 100 |
| s5-p1, s5-p2 | 13 + 50 = 63 | 0 | 50 / 50 |

All four sessions have zero undefined members. Model sets, exact target changes, withheld labels and verified views pass at both blinded stages and the archive stage.

Pinned SHA-256 hashes remain unchanged:

```text
18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71  joulewise/bytes_analysis.py
2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744  joulewise/b5/harvest.py
```

`git diff --check` passes. Fixture-orphan census: `[]`, count 0, exit 0. Only the script, its test module and this report changed. Synthetic fixtures only; no hardware or real BYTES data. No tolerance or scientific numerical bar was added. No NEEDS_RULING remains. The full repository suite is left to CI for this exclusion-only tooling change.

Code/test checkpoints, each committed and pushed: `e4a6cc2c5`, `be5fc668e`, `a3ff6ca8b`, `a672aab75`, `67a8f7cc6`, `a9da7cd02`. This report is the separate final checkpoint. CI is read on the final pushed report head and every job state is supplied in the handoff; no green claim is made here.
