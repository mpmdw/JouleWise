# BYTES twin anchor fix: cold review (RL-80 item 1)

2026-11-11. Cold, clean-seat review (Opus 5.5), required by research-lead ruling RL-80 §2: "the fix is built by a
seat that has not seen the diagnostic's output beyond what the attribution report states, and it gets a cold
review."

- **Target:** `origin/fix/2026-11-11-bytes-twin-anchor` @ `10342e9ec`, based on `lane/2026-11-07-bytes-stage1-run` @ `df4c73e55`.
- **Read:** RL-80 verbatim (`origin/audit/2026-11-10-fable`); the fix report; the attribution report @ `205734f27`;
  `docs/registrations/bytes_pack_v1.md` §7, §11, §12 and §16; and code (`scripts/bytes_twin.py`,
  `joulewise/bytes_analysis.py`, `joulewise/reduce.py`, `joulewise/adapters/powermetrics.py`, fixtures, tests).
- **Ran:** synthetic fixtures only. Worktree `jw-wt/rev-twin`, plus a throwaway mutation worktree `jw-wt/rev-twin-mut`.
  TMPDIR was on `/Volumes/JW-EXT`, every run used `nice -n 10`, and the commands were
  `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B`.

## Verdict: ADMIT

The twin's stage-1 and stage-2 anchor term now follows §7 independently. Nothing outside the twin and its tests
moved. The failing-first evidence is real. All nineteen synthetic campaigns agree at §12's bar, with zero fields
above it. Two of my own registered-semantics mutants are killed, as are two further mutants.

There is one suite failure: `test_neg8_reference_battery_omission_is_detected`. It is independent of this fix
(see "Campaign results"). It does not touch the anchor term and is not a condition of admission, but it needs a
fix on the lane.

Two coverage gaps are non-blocking. Per RL-80 they are settled by the real fit-set rerun, which is still owed:
agreement at the bar and byte-identical predictions (`a6cb172c…5f19`).

## Checks

| # | Check | Result |
|---|---|---|
| 1a | §16 source of the operative bound | **Pass.** `load_archive` keeps `derived/b6-acceptance.json`'s `calibration` record (`scripts/bytes_twin.py:1046, 1060`). `decode_anchor_bound` reads `calibration.operative_bound_s` and refuses a missing, boolean, non-numeric or negative value (`:1111-1116`). It never recomputes a bracket. |
| 1b | §7 "re-derived under the session's operative timing bound" | **Pass.** The edge bound is `operative + span`, the common shift is the member's `effective_clock_anchor_bound_s` (`:1135-1138, 1171`), and a narrowing below the mint bound is refused (`:1141-1142`). This matches the reducer under the override (`joulewise/reduce.py:1839-1858, 2148-2268`): fiducial replaced by the operative bound, edge = fiducial + wall-minus-monotonic span, common = bundle bound. |
| 1c | Block-5 §4 step 4 "for the phase", the decode envelope | **Pass.** The window is the single decode `phase_start` and `phase_end` (`:1144-1147`). Rails are the manifest rails of `power_trace.csv`, summed per interval (`:1148-1170`). `anchor_envelope` (`:1063-1100`) covers four independent-edge corners × every common-shift breakpoint, with max\|E−E₀\|. That is the same extremum the reducer's `max(point−lower, upper−point)` takes. |
| 1d | Independence (R8 item 4; must not import or call the estimator) | **Pass.** The new code adds no imports; the twin's imports remain standard library (`:39-57`). `FenceTests` passed: stdlib-only, runs with `joulewise` unimportable, D8 t table. |
| 1e | Stage scope | **Pass.** The term is computed only at stages `1`/`2`, for valid, unblinded rows of stage models with an archive (`:2193, 2225-2234`). The blinded stage keeps the export column as §11 prescribes (`_member`, `:1439`; `test_blinded_stage_keeps_export_columns`). It reads only bundles that `dc_join` already reads, so the blinding gate is unchanged. A failed join leaves `None`, the cell refuses with `refused_bound_kind_missing`, and nothing falls back to the export column. |
| 2a | Estimator byte-identical | **Pass.** `joulewise/bytes_analysis.py` SHA-256 is `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`, and `git diff df4c73e55..10342e9ec -- joulewise/` is empty. |
| 2b | Every changed file (`df4c73e55..10342e9ec`) | Two reports added: the fix report and `docs/run_reports/interp-energy-desk/bytes-twin-fix-sol-report.md`. Modified: `scripts/bytes_twin.py`, `scripts/test_timings.json` (one inserted provenance key), `tests/fixtures/bytes/campaign.py`, `tests/fixtures/bytes/twin_synth.py`, `tests/test_bytes_agreement.py`, `tests/test_bytes_twin.py`. Nothing else changed. |
| 2c | Flags unchanged | **Pass.** No flag code, flag selection or `_meter_flags` logic changed. The only new output field is the diagnostic `anchor_join_status`. In `campaign.py`, `timing` equals the old inline `calibration.evaluate(.040, .030)` when `anchor_profile` is None, so the 17 existing campaigns' inputs do not change. |
| 3a | New campaigns: non-zero, decode-distinct envelopes and operative ≠ member bound | **Pass.** `anchor_narrow` has an operative bound of 54.531 ms and `anchor_wide` 74.531 ms, against a member bound of 10 ms. Common is 2 ms and span 0.4 ms. The test asserts decode > 0, decode ≠ gross and mint ≠ operative (`tests/test_bytes_agreement.py:1702-1722`). |
| 3b | Revert fails above §12's bar, restore passes | **Pass.** Unit level (`test_stage1_uses_operative_decode_envelope`): the df4c73e55 twin is at 71.98× bar (FAIL) and the fixed twin at 0.000× (pass). Campaign level (full df4c73e55 twin, stage 1, the suite's `compare_cells`): 48 anchor fields above bar, 5.30–72.32× on `anchor_narrow` and 7.91–79.93× on `anchor_wide`, with no mean, h or duration field above. The fixed twin has 0 above on both. |
| 3c | Own mutants | **Pass.** Four of six are killed, including both registered-semantics mutants. See "Mutants". |
| 4 | Agreement, twin, stage-1 modules and all 19 campaigns | **Pass, with one failure that predates the fix.** `tests.test_bytes_twin`: 109 OK (548 s). `tests.test_bytes_stage1`: 23 OK (196 s). `tests.test_bytes_agreement`: 50 tests in 7,291 s, 49 OK and 1 failure (neg8, see below). All 19 campaigns have **0 fields above the bar**. |
| 5 | Read-scope exception | **Confirmed.** Nothing from the three files reached any output. See "Read-scope exception". |

## Mutants

I made textual edits of the fixed twin and ran each through stage 1 against the unchanged estimator's fit output
with the suite's own comparer. Unit means the `test_stage1` assertion; the rest are campaign results.

| Mutant | Unit | anchor_narrow | anchor_wide | Result |
|---|---|---|---|---|
| OLD: df4c73e55 twin, the export whole-window column | 71.98× | 48 anchor above, 5.30–72.32× | 48 above, 7.91–79.93× | killed |
| **M1** whole request window (first phase start to last phase end) instead of decode | 0.00× | 48 above, 2.97–40.49× | 48 above, 3.57–36.07× | **killed** |
| **M2** member mint bound instead of operative bound | 89.77× | 48 above, 6.11–83.35× | 48 above, 8.69–87.85× | **killed** |
| M4 common clock shift dropped (common = 0) | 0.00× | 24 above, 2.71–3.42× | 24 above, 2.07–2.45× | killed |
| M6 operative bound halved at each edge | 71.96× | 48 above, 3.90–53.25× | 48 above, 5.17–52.23× | killed |
| M3 wall-minus-monotonic span dropped | 0.00× | 0 above | 0 above | survives: 0.4 ms against a 54.5 ms edge is under the bar, as on real data |
| M5 archive-anchor trace shift disabled | 0.00× | 0 above | 0 above | survives: every fixture's trace already sits on the anchor (shift = 0) |

Every killing mutant moved only B, `B_kind:anchor`, the interval ends and the attribution floors. None moved a
central estimate. The unit toy world is constant-power with span 0, so only the campaigns separate M1 and M4.

## Campaign results (fixed twin, `tests.test_bytes_agreement`, every CLI stage)

| Campaign | Compared | Equal | Under bar | Above bar | Diagnostics / different |
|---|---:|---:|---:|---:|---:|
| bytes | 314,837 | 307,590 | 7,247 | 0 | 102,274 / 620 |
| resident | 262,385 | 256,980 | 5,405 | 0 | 84,106 / 595 |
| time | 262,385 | 257,058 | 5,327 | 0 | 84,106 / 576 |
| defects | 269,281 | 263,564 | 5,717 | 0 | 86,430 / 564 |
| minimum | 254,966 | 249,072 | 5,894 | 0 | 81,108 / 770 |
| edge_locked | 262,385 | 257,015 | 5,370 | 0 | 84,106 / 574 |
| withheld | 219,549 | 214,672 | 4,877 | 0 | 68,146 / 717 |
| invalid_anchor | 262,033 | 256,489 | 5,544 | 0 | 83,978 / 582 |
| marker_incomplete | 20,312 | 18,062 | 2,250 | 0 | 302 / 278 |
| late_start | 169,903 | 164,325 | 5,578 | 0 | 51,394 / 514 |
| polls_only | 20,220 | 17,977 | 2,243 | 0 | 302 / 296 |
| header_closed | 20,220 | 18,068 | 2,152 | 0 | 302 / 258 |
| empty_payload_n | 314,837 | 307,559 | 7,278 | 0 | 102,274 / 650 |
| replayed_batch | 314,485 | 307,203 | 7,282 | 0 | 102,146 / 626 |
| replayed_tail | 314,837 | 307,578 | 7,259 | 0 | 102,274 / 622 |
| first_batch_tail_replayed | 314,837 | 307,581 | 7,256 | 0 | 102,274 / 632 |
| compressed | 262,385 | 256,821 | 5,564 | 0 | 84,106 / 540 |
| anchor_narrow | 269,017 | 263,284 | 5,733 | 0 | 84,130 / 616 |
| anchor_wide | 269,017 | 263,601 | 5,416 | 0 | 84,130 / 616 |

In the same run, the legacy-anchor mutation test reported 48 anchor fields above bar on each new campaign,
smallest multiples 5.301 and 7.909. Flips: edge_locked 1000 of 1000, resident 501 of 1000.

**The under-bar split varies between runs; the above-bar count does not.** `anchor_narrow` gave equal/under of
263,341/5,676 (the seat), 263,252/5,765 (my mutant harness) and 263,284/5,733 (this run). In every run, compared
was 269,017 and above was 0. This is consistent with order-dependent float summation, for example set iteration
under hash randomization. It is not a defect at §12's bar, but receipts should not be compared on the equal count.

**The neg8 failure is independent of the fix.** `test_neg8_reference_battery_omission_is_detected` failed with
`refused: BYTES commitment guard refused: ` and an empty reason. The test writes its mutant twin into the campaign
directory and runs `--stage 2` with no commitment options. The twin's stage-2 guard runs
`Path(__file__).with_name("bytes_commitment.py")`, which does not exist next to the mutant. That guard was added
in `276d05201`, which predates the base, and neither this test nor the guard is touched by the fix.
**Confirmed at the base:** the same single test, run at `df4c73e55` itself, fails identically (`refused: BYTES commitment guard refused: `, 354 s). It predates the fix and should be repaired on the lane, for example by writing the mutant beside `scripts/bytes_commitment.py` or passing the commitment fixture options. Because it fails before the comparison, it currently gives NEG-8 no protection.

## Read-scope exception (item 5)

I examined the seat's own transcript (`~/.codex/sessions/2026/11/11/rollout-2026-11-11T07-53-02-…jsonl`, cwd
`/Volumes/JW-EXT/jw-wt/sol-bytes-twin-fix`). The commands are shown; the outputs were checked mechanically.
Three commands name the files:

1. **16:02Z.** `git diff --numstat -- joulewise/bytes_analysis.py RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py`.
   Numstat prints counts only, and its output has no line naming any of these paths, so there was no diff.
2. **16:12Z.** `assert subprocess.check_output(['git','diff','--name-only','--', …]) == b''`. The only output is a
   fixed success sentence.
3. **16:21Z**, the final check. `assert Path(name).read_bytes() == git show df4c73e55:name` for each file; on
   failure the assert would show only the path. The output is two fixed sentences and the estimator's SHA-256.

The seat's report discloses only the third. The first two are path-restricted `git diff` calls that also print no
content. **Leak test:** I took every line of 40 characters or more from the three base blobs: 5,871 from RUN_STATE,
1,171 from TASK_QUEUE and 2,988 from the kernel. **None** of them appears anywhere in the transcript: tool inputs,
tool outputs, messages or completed items. As a positive control, 234 of 1,261 such lines of `bytes_twin.py`
and 102 of 341 of the registration do appear, so the detector works. Nothing from those files reached any output
or the model.

**My own scope note.** To run that leak test, I loaded the three files' df4c73e55 blobs into memory with `git show`.
I printed only line counts and match counts, and displayed no content. This is the same class of non-displaying
read as the seat's, and I record it as such. Beyond that, I opened no BYTES data, export, predictions, withheld
store, key, probe output, custody, night-* or archive path. I used no SSH.

## Non-blocking findings (for the lead; no change required to admit)

1. **The estimator's real re-reduction path is not exercised end to end by any campaign.** In the anchor
   campaigns, the estimator returns the labelled synthetic summary (`bytes_analysis.py:605-612`). The fixture
   computes that summary with `reduce._corner_composed_anchor_shift_envelope` under the operative bound, so the
   campaigns test the twin's arithmetic and source choice against the reducer's envelope function. The one
   integration test (`test_interval_bundle_matches_operative_estimator_without_writes`) does run `operative_summary`
   through the real reducer seam. However, it stubs `_derive_anchor_context` with the same clock values the twin
   reads.
   - On real powermetrics bundles, the reducer **re-derives** the anchor placement, the common bound and the span
     from the raw plist and the clock stamps. The twin **reads** them from `metadata.uncertainty_evidence.clock_anchor`
     and uses `power_trace.csv`.
   - These are equivalent when the stored anchor equals the re-derived one. Code check: `combined_power_w` is the
     sum of the manifest rails, and record spacing is cumulative `elapsed_ns` in every adapter mode. Neither is
     guaranteed by a test.
   - The RL-80 real fit-set rerun (agreement at the bar, byte-identical predictions) is the check. If it disagrees
     on the anchor term, look here first.
2. **The trace-shift path (`:1162-1165`) is untested.** Mutant M5 survives everywhere because every fixture places
   the trace on the anchor. A fixture with an older-mode placement, where the first stamp is the anchor plus the
   first record's elapsed time, would close this.
3. **Fail-closed asymmetry.** A per-run anchor failure makes the twin refuse the cell, while the estimator raises
   `AnalysisError` for the whole run. Both refuse, but differently. The comparer would show an exit-code mismatch,
   not a silent number.
4. **The fix report's "no push" is stale**; the branch is on origin.

## Cleanup

Both worktrees and the JW-EXT temporary directories were removed after this report was pushed.
