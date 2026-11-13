# State-machine shadow replay over closed nights (RL-108), 2026-11-12

Branch `feat/2026-11-12-sm-shadow-replay`. Script `scripts/sm_shadow_replay.py`; tests `tests/test_sm_shadow_replay.py`
(30 tests, `python3.13 -B -m unittest tests.test_sm_shadow_replay`). Derived data: `docs/run_reports/2026-11-12-sm-shadow-replay.derived.json`
(the 16 published ALIGN nights: 5 `align-r1-*`, 11 `align-pilot-*`; DERIVED, structure-only, NOT custody). "Closed" is taken from the brief; the script
cannot tell, and there is no explicit closed-night list: every published ALIGN ref is replayed. Exact command (N4, re-run 2026-11-12 after round 2):
`python3.13 -B scripts/sm_shadow_replay.py --git-ref-glob 'origin/night-results/*' --now 0 --out docs/run_reports/2026-11-12-sm-shadow-replay.derived.json`
(the default clock gives the same bytes for these nights). Each night row carries `source_commit`, the commit its `night-results` ref pointed at
(structure only; null in `--tree` mode).

## Conditions kept (RL-108)
- Replay on the Air over the published `origin/night-results/*` refs, read with `git ls-tree` and `git show`. Nothing in them was modified.
- Family gate: by default only `align-r1-*` and `align-pilot-*` refs are replayed; any other family needs an explicit `--family` and is never part
  of the default run. The gate runs on the ref name before anything is fetched.
- Only an allowlisted set of JSON structure files is fetched (`result.json`, `refusal.json`, `chain.*`, `hazard_result.json`, `courier.*`,
  `network_time_off.action.json`, `chain.exit-census.json`, launch markers). Each is projected to the keys the checks read (verdict, exit codes,
  fault flag, reason counts, outcome words, courier sent/receipt fields) before it is kept or written; reason strings and message ids are reduced
  to placeholders. The temp copy lives on the SSD (`/Volumes/JW-EXT/tmp`), is projected only, and is deleted on exit. Existence-only files
  (`censuses.jsonl`, `go-census.json`, `arm_decision.json`, receipts, ...) are taken from the `git ls-tree` name list; their contents are never
  fetched. Energy, power, meter and monitor data are not loaded.
- Output holds states, outcome words, exit codes and their class, invariant names and owed-effect rows. No measured value, no timing.
- No SSH to the MBP, no Block 6 path, no sealed directory, no host command. The derived journal was not produced.
- The R1 follow-up night `align-r1-20261112T2251Z` (the first W1-schema night) now has a `night-results` ref and is in the data as the 16th night.
- Disagreements are listed with a kind (module defect, input gap, legacy schema gap, writer candidate, known writer defect), not resolved.
- Kept-key projection also retains `ended_epoch_s` (`result.json`) and `commit`, `result_sha256`, `ref` (`courier.delivery.json`) because the module reads
  them; none of these is emitted. `result.json` is further reduced to the presence of a `host_restoration` object (no key or value inside it is kept).

## What is compared
Shadow (`observe_night_dir`, `derive_window_state`, `owed_effects`, `exit_contract.classify`) against what the delivered records say: result
verdict or refusal, `chain.started`/`chain.exited`, the exit codes in `chain.exited`, `result.json` and `hazard_result.json`, courier send
records, and the network-time-off action record. Checks: `outcome`, `chain_lifecycle`, `exit_code_sources`, `verdict_vs_exit_class`, `delivery`,
`restore_records` (presence of `host_restoration` in `result.json` on W1-schema nights, file names otherwise), `verdict_masks_outcome` (only for records without `chain_outcome`; a W1-style record that keeps GO and carries `chain_outcome`/`fault` is compared
against the shadow outcome instead), each shadow invariant, and notes for restore records. The chain exit code of `align-r1-*` nights is read under
`r1_driver` (exit 3 = refused; the delivered inventory names the R1 driver as the chain). What ran the `align-pilot-*` chains is not established, so
their exit codes are not classed (all are 0 or absent; no result depends on it). `outcome` agreement is a consistency check, not an independent one:
the expectation uses the same non-zero-exit rule as the module, and all `MEASURED_*` words are collapsed before comparing.

## R1 nights (ALIGN v4 R1 series)
| Night | Verdict | started/exited | chain exit | Class | Shadow state | Shadow outcome | Disagreements |
|---|---|---|---|---|---|---|---|
| align-r1-20261108T0917Z | GO | True/True | 3 | r1_driver:refused | Delivered | CHAIN_FAILED | verdict_masks_outcome, NONZERO_EXIT_WITHOUT_FAULT, COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261110T2146Z | REFUSED | False/False | None | - | Delivered | REFUSED_PRE_CHAIN | COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261111T0208Z | GO | True/True | 3 | r1_driver:refused | Delivered | CHAIN_FAILED | verdict_masks_outcome, NONZERO_EXIT_WITHOUT_FAULT, COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261111T0453Z | GO | True/True | 0 | r1_driver:complete | Delivered | MEASURED_OK | COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261112T2251Z | GO | True/True | 0 | r1_driver:complete | Delivered | MEASURED_OK | none |

Against RUN_STATE: `20261110T2146Z` was a pre-chain refusal (RUN_STATE item 250, line 2667) and the shadow derives REFUSED_PRE_CHAIN: agrees.
`20261111T0208Z` is recorded as refused (thermal start gate timed out, item 253), exit 3 under the R1 driver vocabulary, with verdict GO (audit A-01);
the shadow derives CHAIN_FAILED and lists `verdict_masks_outcome`. `20261108T0917Z` has the same shape. `20261111T0453Z` is verdict GO, exit 0, no
faults: MEASURED_OK, agrees. `20261112T2251Z` is the first W1-schema night: verdict GO, exit 0 in all three sources, `chain_outcome: COMPLETE`
and a boolean `fault` present (the recorded outcome agrees with the shadow), `courier.delivery.json` delivered so the courier invariant does not fire, and
a `host_restoration` object in `result.json`: it is the only night of 16 with no disagreement. Note the shadow derivation (CHAIN_FAILED) and the driver's own word (refused) differ in vocabulary: the runtime module
counts any non-zero exit as a failed chain.
The 11 `align-pilot-*` nights: 10 MEASURED_OK and 1 REFUSED_PRE_CHAIN; the only disagreement on them is the courier input gap below.

## Default (ALIGN-only) corpus: 16 nights
1 of 16 nights agrees (`align-r1-20261112T2251Z`); the other 15 each carry the courier input gap. The rest:

| Check or invariant | Kind | Nights |
|---|---|---|
| COURIER_SENT_WITHOUT_DELIVERY | input_gap | 15 (every night except the W1 night) |
| verdict_masks_outcome | known_writer_defect (A-01) | 2 |
| NONZERO_EXIT_WITHOUT_FAULT | known_writer_defect (A-01) | 2 |

The 84 refs of other families were gated out (`skipped_by_family_gate` in the JSON) and are not part of this data.

## First run (37ed348ca) and Review round 1
The first run swept all 99 `night-results` refs. Files were loaded whole only into a temp directory that was deleted at exit; for the 84 non-ALIGN
nights only counts were emitted, and the committed JSON was ALIGN-only. The BYTES item H is after the stage-1 commitment, and no Block 6 night
exists among the `night-results` refs. The wide-sweep counts (95 courier gaps, 5 masks, 8 non-zero-without-fault of which 3 were labelled module
defects, 2 `verdict_vs_exit_class`, 1 `COURIER_SENT_WITHOUT_RESULT`) are superseded by the gated run above and are not reproduced here.

| Finding | Disposition |
|---|---|
| H1 wrong exit vocabulary for `align-r1-*`; bare `r1-` prefix | Fixed: `r1_driver`; prefix dropped; pilot chains unclassed; test updated; derived JSON and tables regenerated |
| M1 existence-only files fetched | Fixed: presence from `ls-tree` only; test asserts contents are never fetched |
| M2 JSON loaded whole, temp on internal disk | Fixed: per-file key projection before keeping/writing; temp under `/Volumes/JW-EXT/tmp` (no internal fallback); test on temp contents and output |
| M3 restore check cannot fire | Fixed: full `ls-tree` name list, both `network_time_off*.json` forms, "restore" in any name for pre-W1 nights; W1 nights read presence of the `host_restoration` object in `result.json` (round 2, N3). Result: 14 pre-W1 nights record a network-time-off action and none lists a restore-named file; the W1 night carries a `host_restoration` object |
| M4 scope not enforced | Fixed: default family gate, `--family` explicit, test that a non-ALIGN ref is skipped |
| M5 `verdict_masks_outcome` on W1-style records | Fixed: fires only when `chain_outcome` is absent; both shapes tested |
| M6 "module defect" label | Fixed: `legacy_schema_gap` (reasons without boolean `fault`); boolean-present non-zero exit stays a violation (`writer_candidate`); tested |
| L1 courier wording | Fixed: `input_gap`, "not observable from the allowlist", A-02 pointer for `align-r1-*` |
| L2, L3 | L2 not changed (stated above); L3 stated above |
| L4, L5 | Fixed in this report |
| Part B (W1 restore record location) | Answered by round 2: the W1 restore record is the `host_restoration` field of the published `result.json` |

## Review round 2 (74adc30cb)
| Finding | Disposition |
|---|---|
| N1 CI red: `tests.test_sm_shadow_replay` has no weight | Fixed: `scripts/test_timings.json` `seconds_by_module` weight 1.0 s (local run 0.07 s; a hint until the next hosted harvest), so the module is also eligible for the quick tier (< 5 s) |
| N2 data and report one night stale | Fixed: regenerated with the documented command, 16 nights; report lines updated |
| N3 restore note false for the W1 night | Fixed: `host_restoration` presence only (no values, no `ok` booleans); report finding 3 reads 14 pre-W1 nights and one W1 night with a delivered restore record. The `ok` booleans Fable suggested are not read (kept to presence under the structure-only rule); a later request if wanted |
| A-01 ruling | Relabelled `known_writer_defect` for `NONZERO_EXIT_WITHOUT_FAULT` and `verdict_masks_outcome` on `align-r1-*` records without `chain_outcome`, citing A-01 and the W1 fix (`99622e96c` `scripts/run_night.py:2308-2324`); the driver's word is refused (in-chain refusal, not a crash). The invariant is not loosened. |
| N4 reproducibility by ref name only | Fixed: `source_commit` per night; exact command in the header. No explicit closed-night list yet. |
| N5 wording | Fixed with the A-01 change: boolean `fault: false` is worded apart from absent fault |
| N8 kept keys | Fixed in the Conditions section |
| N6 `--family` gets `b5_chain` | Deferred (gate before the W1 replay is used in an adoption request) |
| N7 `chain_outcome` conflict between `result.json` and `hazard_result.json` | Deferred (same gate) |
| W1-shaped non-zero-exit refusal test (exit 3, CHAIN_FAILED, `fault: true`) | Deferred (same gate); the existing W1-style test uses exit 5 |
| RL-108 item 5 watchdog transition table | Not started |

## Explanations (RL-108 item 6)
- `COURIER_SENT_WITHOUT_DELIVERY`, input gap (15 nights): the pre-W1 courier wrote `courier.sent` and `courier.json sent:true`. A delivery receipt and the
  `courier_mode` declared in `night_plan.json` are not observable from the allowlist (the delivered tree does not carry them). Module-side fix: a
  legacy-courier rule or a replay input that supplies `courier_mode`. For the four `align-r1-*` nights see audit A-02 (file-only courier marks
  `courier.sent`). Not shown to be a writer defect.
- `NONZERO_EXIT_WITHOUT_FAULT`, known writer defect (2 nights, both `align-r1-*` with exit 3): nonzero chain exit with neither a fault flag nor fault reasons
  recorded (audit A-01, ruled; closed on the W1 line by `chain_exit_nonzero` and `fault: true`, `99622e96c` `scripts/run_night.py:2308-2324`). The driver's word for
  exit 3 is refused: an in-chain refusal, not a crash. The 11-12 W1 night shows the fixed schema with exit 0; a non-zero W1 night has not been observed, so the fix
  is confirmed by code reading and tests, not by a delivered record. The closed records are not rewritten and the invariant is not loosened. The legacy label `legacy_schema_gap` (reasons recorded, no boolean) applies to no ALIGN night; it was the label for the three
  non-ALIGN hits of the first run.
- `verdict_masks_outcome`, known writer defect (2 nights, `align-r1-20261108T0917Z` and `20261111T0208Z`): verdict GO while the chain failed (A-01, ruled; closed on W1).
- Owed effects: every effect is `unknown`, because the delivered tree cannot supply live host facts. Expected; not evidence of a restore.
  14 pre-W1 nights record a network-time-off action and none lists a restore-named file (note `restore_records`; names only). The W1 night carries a
  `host_restoration` object in its delivered `result.json` (presence only).

## Writer defects for the research lead (reported, not fixed)
1. Verdict GO with nonzero chain exit (A-01, known, ruled; closed on W1): `align-r1-20261108T0917Z` and `align-r1-20261111T0208Z`.
2. Nonzero chain exit with no fault flag and no fault reasons: the same two R1 nights (A-01, same ruling).
3. No restore-named file in the delivered pre-W1 night tree although a network-time-off action is recorded (14 nights; A-05, partly an artifact of names-only
   checking). The W1 night has a delivered restore record (`host_restoration` in `result.json`).

## Next steps
1. Module side (main, Track M): a legacy-courier rule or a `courier_mode` input for replay; make `invariant_nonzero_fault` accept `fault_reasons`.
   Re-run and confirm those rows drop.
2. Re-run when a further ALIGN night's custody closes, and once a non-zero W1 night exists (to confirm the A-01 fix on a delivered record), with the exact
   command in the header. Before the W1 night is used in an adoption request: N6, N7 and the exit-3 W1-shaped test.
3. Declare the watchdog transition table as data and check the exported watchdog status of these nights against it (RL-108 item 5): not started.
4. Cold review, then the lead opens the PR. W1's own night is now in the report (16th night).
