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
| B3 | Count-only stop, minimum 6, cap 8, both pairs >=39, cap accounting, insufficient-calibration outcome; exchangeability left to a separate simulation | `v4_cadence.calibration_stop`; protocol R12 B3 |
| R1 sizing | 61,607 s marked stale; 67,371 s one-encounter no-redo subtotal plus bracket/close/harvest; 96,427 s redo floor (RUN_STATE 216 corrected 215's 90,663 s) | `docs/align/r1_runtime_contract.md`, `LEAD-RULINGS-2.md` correction note |

Resolved by RUN_STATE 216: a zero-capture window does not count toward the cap of 8, one with >=1 captured member counts, two consecutive zero-capture refusals escalate to the lead (`calibration_stop`, protocol B3 item 3). `night_worst_case_s` and its tests corrected to the per-encounter rule.

Open (lead): the >=6 sabotage target (not
adopted); fit/C/T roles and any fit-support deduction; the C1-C8/T manifest
contents.
