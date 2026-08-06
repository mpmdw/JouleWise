# D-110 re-mint custody session — structural-block diagnosis (2026-08-06)

Magistrate session record. Repo main at `c537386` (clean), immediately after
PR #109 (D-079 issuance) merged. All reproduction steps below were run live
this session; logs in `operator_logs/`.

## Sequence of fail-closed refusals

1. **Governed extractions** (both corpora, correct basis pins + semantics
   pairing + `--hash-bundles`): exit 1, ALL cells refused.
   - a10: `whole_window_neg8_verdict_missing`,
     `adapter_continuity_evidence_missing`, `cpu_admission_core_missing` (+
     per-cell reasons). Report: `a10-detection-floor-extraction.json`.
   - window-C: same class. Report: `window-c-detection-floor-extraction.json`.
   - Root cause: current HEAD selects verdict rows by consumption semantics
     (`joulewise/whole_window.py:4670-4674`); a row without the field
     defaults to `d078_minted_envelopes_v1`
     (`_row_consumption_semantics_id`, `whole_window.py:3567`). Both July
     corpora carry only legacy rows → the max-bracket request matches zero
     rows → the "missing"-triple refusal. This invalidates the earlier
     theory (2026-08-03 bytecompare RESULT.md) that the refusals came from
     a missing `--evaluation-basis-sha256` flag.

2. **Max-bracket re-verdict append** (the documented cure —
   `detection_floor.md` "Append-only whole-window history uses explicit
   semantic dispatch… Rows with those two semantics may coexist"):
   `run_campaign.py --whole-window-verdict --consumption-semantics-id
   d078_authenticated_max_bracket_rederivation_v1` on the a10 corpus:
   exit 2, `authenticated survivor consumption refused:
   instrument_calibration_bracket_missing`. No row appended (log
   sha-verified against backup).
   - Invocation notes: relative `--runs-dir` breaks manifest resolution
     (path doubling in `source_manifest_descriptors`,
     `whole_window.py:1871-1892` — catalog `record.path` is root-relative
     when runs_root is relative); use absolute paths. A killed attempt
     leaves `campaign.lock` (holder-dead staleness confirmed before
     removal). Verdict runtime exceeds 2 min.

3. **Direct reproduction of the bracket refusal**
   (`calibration_bracket_for_bundles` driven with the production policy and
   the issued-artifact ledger snapshot):
   - Snapshot valid, 38 observations, dispositions 30 valid / 6
     ordinary-invalid / 2 systematic-invalid — **ALL
     `is_historical_import: true`**.
   - `discover_calibration_candidates` → **0 candidates**: it skips
     `disposition != "valid" or observation.is_historical_import`
     (`calibration_bracketing.py:726`; import-exclusion also enforced at
     :752, :980, :1051, :1322 per the consult pre-verification).
   - `evaluate_calibration_bracket` requires causal live candidates
     (`causal_pre`/`causal_post` around the window within `MAX_AGE_S`);
     zero candidates → `instrument_calibration_bracket_missing`.
   - Per-bundle binding evidence is NOT the problem: bundle
     `metadata.instrument_calibration.bindings` carries all
     `V2_BINDING_FIELDS` (checked on `p2015-df-ph-decode-abs-r01`).

## The structural conclusion

The import-exclusion is deliberate and test-enshrined by PR #109 itself
(`tests/test_calibration_bracketing.py:716`,
`test_import_marker_is_excluded_by_discovery_and_trigger_paths`). Since the
issued ledger contains only import-marked receipts and zero live receipts,
and future live receipts cannot causally bracket a past window, **no
historical window (a10 2026-07-25, window-C 2026-07-26, 7B-floor
2026-07-29) can pass max-bracket consumption under merged semantics.** The
bootstrap contract (import-marked genesis) and the bracketing contract
(live-candidate endpoints) are individually sound and jointly exclude the
D-110 re-mint as desk work at current main.

Design fork (Sol xhigh consult in flight, run `20260806T165843Z-10884`):
1. Role-aware historical candidacy (import-marked valid receipts may
   bracket windows entirely preceding the ledger cutoff) — amends a
   just-cold-gated contract; full gauntlet + rule-11 gate.
2. Historical re-mint declared closed; fresh Window D under the live
   regime — stronger end-to-end authentication story; costs a quiet-mac
   night; D-113 rigor-first precedent.
3. Per-bundle embedded b_fiducial consumption — presumed unsound
   (self-attested evidence; exactly what issuance replaced).

Separately standing regardless of fork outcome (scout F1/F2): the mint's
D-084 hard literal `EXPECTED_OPERATIVE_FLOOR_TEXT = "7.377086"`
(`mint_floor_artifact.py:91`) refuses any corrected (wider) floor and needs
a per-plan re-supply; and the mint consumes BOTH extraction reports (a10 +
window-C), so any surviving path re-runs both extractions in one custody
session (FLOOR-BIND-01 fence).

## Custody state

- Both campaign logs byte-identical to pre-session state (sha-pinned
  backups in `log_backups/`; verified after every refusal).
- Both refused extraction reports retained (exit-1 reports are evidence,
  not claim artifacts).
- No ledger mutation, no bundle mutation, no repo mutation this session
  beyond the PR #109 merge itself.
