# R11 review dispositions (Sol1 + Sol2 on c3796bf49)

Fixes live on `align/2026-11-08-v4-r11`. Scientific constants, estimands,
thresholds and exclusions are unchanged except where the cited authority
(AGREEMENT-FINAL Track 1 R01-R16, RUN_STATE 203/204/209/210/212/214) requires.
Reviews: `r11-review-sol1.md`, `r11-review-sol2.md` (review branches
`align/2026-11-08-v4-r11-review-sol{1,2}`), whose witness tests are
`tests/align/test_r11_review_sol1_witnesses.py` and `test_r11_review_sol2.py`.

## Lead rulings on the fixer's four items

1. **Top-up window.** 1800 s is a hard bound (protocol section 4, "about 30
   minutes", no slack). `v4_registration.TOPUP_WINDOW_S`.
2. **U6 conventions confirmed.** `cell_residual_sd` (s_r) is in joules, the same
   unit as each per-turn `residual_j`; early/late halves are chronological
   episodes within a pair; the cluster is (pair, trajectory); no new m>=6 rule.
   The final-roster U6 operating-characteristic rerun is assigned to a Sol seat,
   not to the fixer, and is still owed.
3. **F01 scope.** Bind the full executed dependency closure, not a hand list.
   `v4_registration.EXECUTED_CLOSURE` is the static (stdlib `ast`, module- and
   function-level imports, parent packages included) joulewise/ closure of
   `endpoint.py`, `scripts/run_night.py` and `scripts/align_v4_session.py`,
   merged into `ARTIFACTS`. `tests/align/test_v4_executed_closure.py` recomputes
   it and fails if any module is missing from `ARTIFACTS` or the receipt
   template. Limits: `importlib` string imports, third-party packages and the
   `scripts/` modules reached in the closure are not bound by this list.
4. **Coverage.** Admission scope is the stack since the R10 baseline
   (`d600baba0..head`). Earlier history keeps its own earlier gates; Sol1/Sol2
   did not line-review the 1,117-commit `origin/main...head` range and this
   record does not claim they did.

## Per-finding table

| Finding | Sev | Change | Where | Witness / tests |
|---|---|---|---|---|
| S1-H1 U6 route used legacy rule | HIGH | `monitoring_stability_v4`: +/-0.5*s_r, trajectory-clustered, imprecision label, D position means, no slope gate; `session_desk_evidence(v4=True)` default; legacy kept as `monitoring_stability`; `acceptance(v4)` refuses legacy-shaped U6 | `thermal_desk.py` | `test_r11_review_sol1_witnesses` (2), `test_thermal_desk` |
| S1-H2 no completed-top-up timing | HIGH | `battery_arm(..., topup, now_epoch_s)` refuses missing/future/>1800 s evidence; `--topup-completed-at`, `--topup-source` required; evidence kept in the arm record | `v4_registration.py`, `align_v4_session.py` | `test_r11_review_sol1_witnesses` (1), `test_v4_registration`, `test_v4_r11`, `test_v4_kit` |
| S1-M1 / Sol2 F03 H* identity | MED | `subturn_h_star` rejects fractional/negative/bool/duplicate/non-finite doses; unobserved earlier grid dose leaves the crossing undefined (listed); off-grid doses reported | `v4_estimands.py` | witnesses (2+2), `test_v4_estimands` |
| Sol2 F01 receipt omits cache code | HIGH | executed closure bound into `ARTIFACTS` (219 paths); template regenerated; receipt blob check batched in one `git cat-file --batch` | `v4_registration.py`, `registration_receipt.json` | `test_receipt_refuses_changed_live_cache_implementation`, `test_v4_executed_closure` |
| Sol2 F02 zero-turn X-G | MED | `validate_wp19` accepts zero compared turns only for a `fail` receipt with the INCONCLUSIVE predeclaration; never pass/complete/identical | `v4_registration.py` | `test_zero_turn_x_retains_nonveto_failed_identity_receipt`, `test_v4_registration` |

## R12 (RUN_STATE 214, amended by 215) written into the registration

Cross-checks: `perf/2026-11-08-r12-review-sol1`, `-sol2`. Protocol section
"R12 window cadence" in `docs/align/pilot_protocol_v4.md`.

| Item | Change | Where |
|---|---|---|
| B1 | A window ends at authenticated terminal completion; 59,520 s is a ceiling, not a reservation; custody, quiet admission and ceiling kept | protocol R12 B1 and the Sizing line; kit README text |
| B2 | Frozen 14-entry next-arm triage list, all gating; arm evaluates it (`--next-arm-triage`); full desk gating after W1 and after code/config change | `v4_cadence.NEXT_ARM_TRIAGE`, `next_arm_triage`; `align_v4_session.arm_checks` |
| B3 | Fixed 8 counted calibration windows (RUN_STATE 217 reverted the count stop), both pairs >=39 after 8, cap accounting, insufficient-calibration outcome | `v4_cadence.calibration_stop`; protocol R12 B3 |
| R1 sizing | 61,607 s marked stale; 67,371 s one-encounter no-redo subtotal plus bracket/close/harvest; 96,427 s redo floor (RUN_STATE 216 corrected 215's 90,663 s) | `docs/align/r1_runtime_contract.md`, `LEAD-RULINGS-2.md` correction note |

Resolved by RUN_STATE 216: a zero-capture window does not count toward the cap of 8, one with >=1 captured member counts, two consecutive zero-capture refusals escalate to the lead (`calibration_stop`, protocol B3 item 3). `night_worst_case_s` and its tests corrected to the per-encounter rule.

Open (lead): the >=6 sabotage target (not
adopted); fit/C/T roles and any fit-support deduction; the C1-C8/T manifest
contents.

## RUN_STATE 217: R12 B3 reverted to a fixed 8 calibration windows

Two synthetic simulations (`align/2026-11-08-b3-sim-sol1` @ `09d7b3c7f`, `-sol2` @ `95d43c054`)
agree that a count stop saves about one window but lowers the threshold and raises
future benign FPR under window-level drift (sol1 clustered/hot: maximum rule 2.84 % vs
2.14 %, 5 % rank 5.38 % vs 4.13 %; sol2 hot10, tau .5: 2.73 % vs 2.22 %). Counts never
read scores, so blinding was not at risk. Cost of fixed 8: about 13 MBP hours.

- `calibration_stop` is now a fixed-8 predicate: exactly 8 counted windows in the frozen
  order, no early stop; `calibration_complete` if both pairs >= 39 eligible after 8,
  else `insufficient_calibration`. The zero-capture rule and two-in-a-row escalation
  (item 216) stay. Decision `stop_complete` is renamed `calibration_complete`.
- Protocol R12 B3 text, the `calibration_stop` triage entry, kit README text and tests
  updated. The FPR statement stays conditional on exchangeability; both designs exceed
  nominal FPR under a forward drift trend and the held-out test cohort is the empirical
  evidence, which public text must say.
- **Open statistics item (before W1 registration, not adopted):** sol1's candidate of a
  minimum of 7 windows plus a frozen 0.5 s_r threshold margin. It is model-dependent and
  needs a scale/scorer qualification and a power assessment.

## Delta-HOLD round (Sol delta reviews sol1/sol2 on 353446ad6)

Witnesses: `tests/align/test_r11_delta_sol1.py`, `test_r11_delta_sol2.py` (the review-era
six-window and `stop_complete` expectations were updated to the fixed-8 predicate of
RUN_STATE 217, and the arm-call witnesses to the battery-log API).

| Finding | Change | Where |
|---|---|---|
| H01 / DELTA-S2-H1 scripts outside the receipt | Execution closure now follows script launch edges (exact `scripts/...` string constants outside docstrings, shell tokens) from endpoint, run_night, session, kit, budget procedure and the night_chains wrappers; 292 bound paths, scripts included. Strict/amendment tiers (below) keep the cost proportionate | `v4_registration.py` (`EXECUTED_CLOSURE`, `STRICT_*`), `tests/align/test_v4_executed_closure.py` |
| H02 / DELTA-S2-M1 impossible counts | `calibration_stop` refuses rows with eligible benign > captured, captured > 22, bool/non-integer/negative counts, a wrong `eligible_total`; the triage refuses `calibration_totals` that do not sum | `v4_cadence.py` |
| M01 unfinished zero-capture window | A provisional zero-capture window is unfinished, not a refusal: `pending_final_eligibility` until final | `v4_cadence.py` |
| M02 / DELTA-S2-M2 packet flags | Previous-window-is-W1 is derived from the registered window id; code/config-changed from the artifact-set digest vs the digest recorded at the last desk pass; a contradictory flag refuses | `v4_cadence.py`, `v4_registration.artifact_set_digest` |
| M03 retention | The arm record keeps the packet, its digest, the packet file digest and the derived calibration summary | `v4_cadence.py`, `align_v4_session.py` |

## Opus cold review round (v4-opus-cold-review.md @ 33d0bc89f)

| Finding | Change | Where |
|---|---|---|
| HIGH-1 WP22 dry run red | Contrast re-derived after the WP18 update (with the matching X-G stand-in), delta_slow_c and stage in the synthetic manifest, a synthetic registration directory with a PENDING U3; the desk takes a PENDING U3 as inconclusive and keeps running; the minimal run is in the default tests; the full `JW_WP22_FULL=1` run passes; both are in the Stage A checklist | `align_v4_w1_synthetic.py`, `align_v4_thermal_desk.py`, `test_v4_w1_synthetic.py` |
| MED-1 receipt brittleness | Strict tier (re-register) and amendment tier (lead-signed `amendments` row: path, old/new sha, reason, signature; chained; never for strict paths) | `v4_registration.py`, `tests/align/test_v4_receipt_tiers.py` |
| MED-2a deadlock | `lead_rulings` row (id, text digest, resets, after_window, signature) resets the zero-capture escalation count, retained in the arm record | `v4_cadence.py` |
| MED-2b meter | `meter_samples_clock` replaced by gating `meter_reader_live` and non-gating `meter_coverage` (gaps listed) | `v4_cadence.py` |
| MED-3 top-up | Evidence derived from a battery log (completed charge within 1800 s, or continuous float since); hand-entered time removed (`--battery-log`); sampler/derive script | `v4_topup.py`, `scripts/align_v4_battery_log.py`, `align_v4_session.py` |
| MED-4 v5 blinding | DC residual printed for benign members only; non-benign DC rows sealed (hash only) | `km003c.seal_non_benign` |
| L2/L3 | Raw packet retained; `record_commit` must be a commit the arm finds | `align_v4_session.py` |
| L5 | Window id from the session state (default W1) | `align_v4_session.py` |
| L7 | Packet template and `--emit-triage-template` | `v4_cadence.py` |
| L8 | `pmset -g batt` is evidence only | `align_v4_session.py` |
| L9 | H* refuses bool and non-numeric scores | `v4_estimands.py` |
| L1, L4 | L1 is covered by the R1 exporter. L4 (note only): U6's trajectory-clustered SE is CR0 with z = 1.645, anti-conservative at about 14 trajectories; CR1 with t(G-1) is a candidate, not changed here (U6 is reported, never a gate) | n/a |

## Delta2 round (Sol delta2 reviews on f993b784f) and the smoke-kit findings

| Finding | Change | Where |
|---|---|---|
| S1 F01 / S2 H1, H2 receipt completeness | Strict is now the default tier; the amendment tier is a 25-module allowlist justified by the reviewed refusal census and never traced; the walker follows `-m` launches; `WP15` runtime script and its config, `joulewise/__main__.py` and the registration helpers are bound; a dynamic closure (audit-hook trace of the synthetic WP22 chain, R1 arm with the real runtime child, R1-to-W1 chain and arm/install session) is committed as evidence and asserted inside the strict receipt | `v4_registration.py`, `scripts/align_v4_dynamic_trace.py`, `docs/align/v4/dynamic_closure_trace.json`, `tests/align/test_v4_dynamic_closure.py` |
| S1 F02 / S2 M3 stranded back-to-back arms | Basis (a) has no continuity rule; basis (b) unchanged; the sampler runs continuously (`sample --loop`) from the initial charge acquisition through windows and turnarounds | `v4_topup.py`, `align_v4_battery_log.py`, protocol section 4 |
| S1 F03 / S2 M2 filtered rows | Raw-order evaluation: a transition needs consecutive valid timed rows; invalid, untimed, off-AC or out-of-order rows break the interval | `v4_topup.py` |
| S2 M1 two-sentinel roster | Captured ceiling 24 (22 plus the two sentinels a U4/U5-inconclusive window may add); calibrators stay 7 per pair | `v4_cadence.py` (`CAPTURED_MAX`) |
| G1 stale packet | The packet carries `record_path` and `record_sha256`; the arm checks the blob at `record_commit` and that it is the last commit changing the path | `align_v4_session.py` (`_record_bound`), `tests/align/test_v4_record_binding.py` |
| G2 chain doc | Kit regeneration inserted between installing the slots and `--check`; the doc block is a tested script | `scripts/align_r1_to_w1_chain.py`, `tests/align/test_r1_to_w1_chain.py` |
| G3 KM003C crash radius | An unclosed stream is salvaged up to its last valid record (start offset, no fabricated samples); only members overlapping the gap are DC-missing | `km003c.py`, `km003c_parse.py`, `tests/align/test_km003c.py` |

## Ruling: no battery sampler during a window

An ioreg spawn every 120 s on the measuring Mac is out-of-tree activity the quiet guard exists to
catch. `sample --loop` now runs only between windows (start at terminal completion, `stop`
before the arm dwell; `--pidfile`), and across a window the float evidence is the window's own
1 Hz SMC battery journal, converted by `v4_topup.window_records` and merged in time order with
the between-window logs (`--window-battery-journal`). A boundary gap above 300 s, or a missing
window journal, breaks continuity as before. Amendment allowlist unchanged.
