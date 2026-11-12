# State-machine shadow replay over closed nights (RL-108), 2026-11-12

Branch `feat/2026-11-12-sm-shadow-replay`. Script `scripts/sm_shadow_replay.py`; tests `tests/test_sm_shadow_replay.py`
(17 tests, `python3 -m unittest tests.test_sm_shadow_replay`). Derived data: `docs/run_reports/2026-11-12-sm-shadow-replay.derived.json`
(the ALIGN pilot and R1 nights; DERIVED, structure-only, NOT custody).

## Conditions kept (RL-108)
- Replay on the Air over the published `origin/night-results/*` refs, read with `git ls-tree` and `git show`. Nothing in them was modified.
- Only an allowlist of structure files is read (markers, `result.json`, `refusal.json`, `chain.*`, `hazard_result.json`, `courier.*`,
  `network_time_off.action.json`, `chain.exit-census.json`). Energy, power, census, meter and monitor files are not loaded.
- Output holds states, outcome words, exit codes and their class, invariant names and owed-effect rows. No measured value, no timing.
- No SSH to the MBP, no Block 6 path, no sealed directory, no host command. The derived journal was not produced.
- The R1 follow-up night of 11-12 is not closed and has no `night-results` ref; it is not in the data. Re-run after its custody closes.
- Disagreements are listed with a kind (module defect, fixture gap, writer candidate), not resolved.

## What is compared
Shadow (`observe_night_dir`, `derive_window_state`, `owed_effects`, `exit_contract.classify`) against what the delivered records say: result
verdict or refusal, `chain.started`/`chain.exited`, the exit codes in `chain.exited`, `result.json` and `hazard_result.json`, courier send
records, and the network-time-off action record. Checks: `outcome`, `chain_lifecycle`, `exit_code_sources`, `verdict_vs_exit_class`, `delivery`,
`verdict_masks_outcome`, each shadow invariant, and notes for restore records. The chain exit code is read under `r1_runtime` for `align-*`
and `r1-*` nights, else `b5_chain` (a choice made in the script; the contract table does not say which applies).

## R1 nights (ALIGN v4 R1 series)
| Night | Verdict | started/exited | chain exit | Class | Shadow state | Shadow outcome | Disagreements |
|---|---|---|---|---|---|---|---|
| align-r1-20261108T0917Z | GO | True/True | 3 | r1_runtime:failed | Delivered | CHAIN_FAILED | verdict_masks_outcome, NONZERO_EXIT_WITHOUT_FAULT, COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261110T2146Z | REFUSED | False/False | None | - | Delivered | REFUSED_PRE_CHAIN | COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261111T0208Z | GO | True/True | 3 | r1_runtime:failed | Delivered | CHAIN_FAILED | verdict_masks_outcome, NONZERO_EXIT_WITHOUT_FAULT, COURIER_SENT_WITHOUT_DELIVERY |
| align-r1-20261111T0453Z | GO | True/True | 0 | r1_runtime:complete | Delivered | MEASURED_OK | COURIER_SENT_WITHOUT_DELIVERY |

Against RUN_STATE: `20261110T2146Z` was a pre-chain refusal (item 2667) and the shadow derives REFUSED_PRE_CHAIN: agrees. `20261111T0208Z` has
chain exit 3 under verdict GO, Fable finding A-01; the shadow derives CHAIN_FAILED and lists `verdict_masks_outcome`. `20261108T0917Z` has the same
shape (exit 3, verdict GO). `20261111T0453Z` is verdict GO, exit 0, no faults: MEASURED_OK, agrees.
The 11 `align-pilot-*` nights (derived JSON): 10 MEASURED_OK and 1 REFUSED_PRE_CHAIN; the only disagreement on them is the courier fixture gap below.

## Whole published corpus (99 refs, counts only)
4 of 99 nights list no disagreement. The rest:

| Check or invariant | Kind | Nights |
|---|---|---|
| COURIER_SENT_WITHOUT_DELIVERY | fixture_gap | 95 |
| verdict_masks_outcome | writer_candidate | 5 |
| NONZERO_EXIT_WITHOUT_FAULT | writer_candidate | 5 |
| NONZERO_EXIT_WITHOUT_FAULT | module_defect | 3 |
| verdict_vs_exit_class | - | 2 |
| COURIER_SENT_WITHOUT_RESULT | writer_candidate | 1 |

## Explanations (RL-108 item 6)
- `COURIER_SENT_WITHOUT_DELIVERY`, fixture gap: the pre-W1 courier wrote `courier.sent` and `courier.json sent:true` but no message id or git-push
  receipt. For the R1 file-only courier the declaration lives in `night_plan.json`, which the delivered tree does not carry. Module-side fix: a
  legacy-courier rule, or a replay input that supplies `courier_mode`. Not a writer defect.
- `NONZERO_EXIT_WITHOUT_FAULT`, module defect (3 nights): `hazard_result.json` records `faults.reasons` but no boolean `fault`, and
  `invariant_nonzero_fault` looks only at the boolean.
- `NONZERO_EXIT_WITHOUT_FAULT`, writer candidate (5 nights): nonzero chain exit with neither flag nor reasons recorded. Includes both R1 nights with exit 3.
- `verdict_masks_outcome`, writer candidate (5 nights, 2 of them R1): verdict GO while the chain failed. Known as audit A-01.
- `COURIER_SENT_WITHOUT_RESULT` (1 night, `20260911`): courier send recorded, refusal record present, no `result.json`. An early-September
  night from before the result schema; no current writer is implicated.
- `verdict_vs_exit_class` (2 nights, none R1): verdict ABORTED with a code undeclared under the chosen table (exit 2 under `b5_chain`; -15, a negative
  signal, under `r1_runtime`). The exit contract needs to say which tool's code a result carries.
- Owed effects: every effect is `unknown`, because the delivered tree cannot supply live host facts. Expected; not evidence of a restore.
  73 nights recorded a network-time-off action and none delivers a restore record (note `restore_records`).

## Writer defects for the research lead (reported, not fixed)
1. Verdict GO with nonzero chain exit (A-01 pattern): `align-r1-20261108T0917Z`, `align-r1-20261111T0208Z`, and three BYTES/D117 nights.
2. Nonzero chain exit with no fault flag and no fault reasons: the same two R1 nights, and three others.
3. No restore record in the delivered night tree although network time was turned off (73 nights).

## Next steps
1. Module side (main, Track M): a legacy-courier rule or a `courier_mode` input for replay; make `invariant_nonzero_fault` accept `fault_reasons`.
   Re-run and confirm those rows drop.
2. Re-run on the R1 follow-up night once `night-results/<plan>` is published and its custody has closed:
   `python3 scripts/sm_shadow_replay.py --git-ref-glob 'origin/night-results/*' --night <plan> --out <file>`.
3. Declare the watchdog transition table as data and check the exported watchdog status of these nights against it (RL-108 item 5): not started.
4. Cold review, then the lead opens the PR. An adoption request also needs W1's own night in the report.
