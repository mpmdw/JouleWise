# State-machine shadow replay over closed nights (RL-108), 2026-11-12

Branch `feat/2026-11-12-sm-shadow-replay`. Script `scripts/sm_shadow_replay.py`; tests `tests/test_sm_shadow_replay.py`
(26 tests, `python3.13 -B -m unittest tests.test_sm_shadow_replay`). Derived data: `docs/run_reports/2026-11-12-sm-shadow-replay.derived.json`
(the 15 closed ALIGN nights: 4 `align-r1-*`, 11 `align-pilot-*`; DERIVED, structure-only, NOT custody).

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
- The R1 follow-up night of 11-12 is not closed and has no `night-results` ref; it is not in the data. Re-run after its custody closes.
- Disagreements are listed with a kind (module defect, input gap, legacy schema gap, writer candidate), not resolved.

## What is compared
Shadow (`observe_night_dir`, `derive_window_state`, `owed_effects`, `exit_contract.classify`) against what the delivered records say: result
verdict or refusal, `chain.started`/`chain.exited`, the exit codes in `chain.exited`, `result.json` and `hazard_result.json`, courier send
records, and the network-time-off action record. Checks: `outcome`, `chain_lifecycle`, `exit_code_sources`, `verdict_vs_exit_class`, `delivery`,
`verdict_masks_outcome` (only for records without `chain_outcome`; a W1-style record that keeps GO and carries `chain_outcome`/`fault` is compared
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

Against RUN_STATE: `20261110T2146Z` was a pre-chain refusal (RUN_STATE item 250, line 2667) and the shadow derives REFUSED_PRE_CHAIN: agrees.
`20261111T0208Z` is recorded as refused (thermal start gate timed out, item 253), exit 3 under the R1 driver vocabulary, with verdict GO (audit A-01);
the shadow derives CHAIN_FAILED and lists `verdict_masks_outcome`. `20261108T0917Z` has the same shape. `20261111T0453Z` is verdict GO, exit 0, no
faults: MEASURED_OK, agrees. Note the shadow derivation (CHAIN_FAILED) and the driver's own word (refused) differ in vocabulary: the runtime module
counts any non-zero exit as a failed chain.
The 11 `align-pilot-*` nights: 10 MEASURED_OK and 1 REFUSED_PRE_CHAIN; the only disagreement on them is the courier input gap below.

## Default (ALIGN-only) corpus: 15 nights
No night is free of disagreement (0 of 15 agree); every one carries the courier input gap. The rest:

| Check or invariant | Kind | Nights |
|---|---|---|
| COURIER_SENT_WITHOUT_DELIVERY | input_gap | 15 |
| verdict_masks_outcome | writer_candidate | 2 |
| NONZERO_EXIT_WITHOUT_FAULT | writer_candidate | 2 |

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
| M3 restore check cannot fire | Fixed in part: full `ls-tree` name list, both `network_time_off*.json` forms, "restore" in any name. Limit: file names only; fields inside delivered files are not inspected. Result: 14 of 15 nights record a network-time-off action, none lists a restore-named file |
| M4 scope not enforced | Fixed: default family gate, `--family` explicit, test that a non-ALIGN ref is skipped |
| M5 `verdict_masks_outcome` on W1-style records | Fixed: fires only when `chain_outcome` is absent; both shapes tested |
| M6 "module defect" label | Fixed: `legacy_schema_gap` (reasons without boolean `fault`); boolean-present non-zero exit stays a violation (`writer_candidate`); tested |
| L1 courier wording | Fixed: `input_gap`, "not observable from the allowlist", A-02 pointer for `align-r1-*` |
| L2, L3 | L2 not changed (stated above); L3 stated above |
| L4, L5 | Fixed in this report |
| Part B (W1 restore record location) | Open: lead to confirm the W1 restore record is in the published set |

## Explanations (RL-108 item 6)
- `COURIER_SENT_WITHOUT_DELIVERY`, input gap (15 nights): the pre-W1 courier wrote `courier.sent` and `courier.json sent:true`. A delivery receipt and the
  `courier_mode` declared in `night_plan.json` are not observable from the allowlist (the delivered tree does not carry them). Module-side fix: a
  legacy-courier rule or a replay input that supplies `courier_mode`. For the four `align-r1-*` nights see audit A-02 (file-only courier marks
  `courier.sent`). Not shown to be a writer defect.
- `NONZERO_EXIT_WITHOUT_FAULT`, writer candidate (2 nights, both `align-r1-*` with exit 3): nonzero chain exit with neither a fault flag nor fault reasons
  recorded (audit A-01). The legacy label `legacy_schema_gap` (reasons recorded, no boolean) applies to no ALIGN night; it was the label for the three
  non-ALIGN hits of the first run.
- `verdict_masks_outcome`, writer candidate (2 nights, `align-r1-20261108T0917Z` and `20261111T0208Z`): verdict GO while the chain failed (A-01).
- Owed effects: every effect is `unknown`, because the delivered tree cannot supply live host facts. Expected; not evidence of a restore.
  14 nights record a network-time-off action and none lists a restore-named file (note `restore_records`; names only, see M3 limit).

## Writer defects for the research lead (reported, not fixed)
1. Verdict GO with nonzero chain exit (A-01 pattern): `align-r1-20261108T0917Z` and `align-r1-20261111T0208Z`.
2. Nonzero chain exit with no fault flag and no fault reasons: the same two R1 nights.
3. No restore-named file in the delivered night tree although a network-time-off action is recorded (14 nights; A-05, partly an artifact of names-only checking).

## Next steps
1. Module side (main, Track M): a legacy-courier rule or a `courier_mode` input for replay; make `invariant_nonzero_fault` accept `fault_reasons`.
   Re-run and confirm those rows drop.
2. Re-run on the R1 follow-up night once `night-results/<plan>` is published and its custody has closed:
   `python3.13 scripts/sm_shadow_replay.py --git-ref-glob 'origin/night-results/*' --night <plan> --out <file>`.
3. Declare the watchdog transition table as data and check the exported watchdog status of these nights against it (RL-108 item 5): not started.
4. Cold review, then the lead opens the PR. An adoption request also needs W1's own night in the report.
