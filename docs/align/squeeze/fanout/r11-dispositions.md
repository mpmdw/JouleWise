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
| B2 | Frozen 16-entry next-arm triage list (15 gating, after `battery_window`; `meter_coverage` is recorded, non-gating); arm evaluates it (`--next-arm-triage`); full desk gating after W1 and after code/config change | `v4_cadence.NEXT_ARM_TRIAGE`, `next_arm_triage`; `align_v4_session.arm_checks` |
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
| S2 M1 two-sentinel roster | Captured ceiling 24 (22 plus the two sentinels a U4/U5-inconclusive window may add); calibrators stay 7 per pair (SUPERSEDED by R20 / delta5 S2 F5: the supplemental sentinels count toward nothing and the ceiling is 22) | `v4_cadence.py` (`CAPTURED_MAX`) |
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

## Packet-builder integration (Opus HOLD on the triage-packet builder) and delta3 (Sol1, Sol2)

| Finding | Change | Where |
|---|---|---|
| Opus HIGH-1 packet is trusted text | A packet is a pointer. The arm rebuilds it with `build_packet` from the identities the packet names (own clock, own artifact-set digest) and requires canonical equality ignoring only `pushed_tip` and `packet_preflight`; a rebuild error refuses | `align_v4_session.arm_checks`, `align_v4_next_arm_packet.rebuild_and_compare` |
| Opus HIGH-2 expiry optional | `valid_until_epoch_s` is mandatory and numeric; the arm clock must be before it | `v4_cadence.next_arm_triage` |
| Opus HIGH-3 wire compatibility | `meter_reader_live` (ARM, gating) and `meter_coverage` (non-gating) split; `last_desk_passed_artifact_set_sha256` computed from committed bytes (`artifact_set_digest_at`); window ids validated; 16 entries (battery_window added by ruling 9), "14" text fixed | builder, `v4_cadence.py`, `v4_registration.py` |
| Opus MED-1..4 | Quiet state, live meter, `prepared_at` and battery evidence are computed at the arm (meter by a short monitor probe); the quiet start state keeps the committed observation until the condition-waits evaluator lands; hash-chained window records (omitted attempt detected); `text_sha256` of a lead ruling computed from a committed text file | builder, `align_v4_session._probe_meter_live` |
| Opus L1 | A U1-U3 fail gives that model 0 eligible from that window (R15, RUN_STATE 226) | builder |
| Zero-capture retry | Same window id with an attempt suffix: `C3#2`; `WINDOW_ID` accepts `#k`; the frozen order is unchanged | `v4_cadence.WINDOW_ID` |
| S1 F01 / S2 H1 amendment allowlist | The production hazard-pack night runner is back in the dynamic trace (`night_driver_hazard_pack`). The allowlist may hold only a module absent from BOTH the static closure and the trace; every bound path is statically reachable, so it is empty (strict if in doubt) | `v4_registration.AMENDMENT_ALLOWLIST`, `align_v4_dynamic_trace.py` |
| S1 F02 launch templates | The four `configs/launchd/*.plist.template` files are bound and strict | `v4_registration._NAMED_ARTIFACTS` |
| S1 F03 / S2 M1 (G1) stale record | The record is bound to the series ledger's latest window (`previous_record` + `series_sha256` at HEAD) through the hash-chained records the arm rebuilds | `align_v4_session._record_bound` |
| S1 F04 / S2 H2 (G3) salvage | Salvage only for a stream listed in the window's custody manifest AND supervised by the shared driver, with a recorded matching digest. An unlisted or unsupervised stream is never available DC and is not parsed; an unrecorded digest excludes. Separate flags: `meter.unsupervised`, `meter.stream_unlisted`, `meter.custody_digest_unrecorded` (mismatch: `meter.custody_hash_mismatch`) | `km003c.session_report` |

## Delta4 (Sol1 HOLD, Sol2 ADMIT_WITH_FIXES on 48a4d1d76)

| Finding | Change | Where |
|---|---|---|
| S1 F1 source sorting defeats the raw-order refusal | Each battery source (log or converted window journal) is checked in its own raw order for strictly increasing timestamps BEFORE merging; a regression or duplicate refuses with a structured reason. No new threshold or continuity rule | `v4_topup.derive_from_sources` |
| S2 F1 `Cn#k` loses its U3 scope | A validated retry id is normalized to its counted slot for the `checks_by_window` lookup; records keep the full attempt id; no slot is added | `thermal_desk.window_report` |
| S2 F2 `lru_cache` on U3 admission | All caches removed from `v4_u3` (decision cache and the pure-math memos): admission recomputes (about 0.2 s) | `v4_u3.py`, `v4_registration.validate_u3` |
| S1 L1 / S2 F3 nested pushed tip | `canonical` also drops `checks.record_committed.pushed_tip`; reachability is re-proved by the rebuild | `align_v4_next_arm_packet.canonical` |
| S1 stale R0 tests / S2 F4 | `test_r1_runtime` uses explicit temporary pending fixtures; the shipped templates carry `medium` | `tests/align/test_r1_runtime.py` |

## Integration item 4: D/C/T series (dct-series-merged @ 25860dcaf) and R20

| Item | Change | Where |
|---|---|---|
| Merge | `origin/align/2026-11-08-dct-series-merged` merged (not rebased). Seed check: MATCH (`align/2026-11-08-series-seed-check-sol`), so the manifest bytes are unchanged | `configs/campaigns/align_v4/series/series_manifest.json` |
| Arm binds the series with the arm-rebuild design | The arm binds its OWN rebuild of the packet (`bind_packet(..., authenticated_by_rebuild=True)`); the builder derives `next_window_id`, `series_manifest_sha256` and a chronological `series_history` (lead releases from `lead_rulings`) from the hash-chained records. `make_packet` is a dev/test producer needing an explicit expiry and arm clock | `align_v4_series.py`, `align_v4_session._arm_and_install`, builder |
| R15 text | Protocol section "R15 - the frozen D/C/T series" | `docs/align/pilot_protocol_v4.md` |
| R20 escalation sentinels | Ordinals 23 and 24 after the late sentinel, exact replays of W1:5, supplemental diagnostics (no identical-work group, no held-out seed, never counted), ceiling 62,400 s (R15); `--extra-sentinels 2`; protocol text | `align_v4_series.escalation_allocations`, `build_files`, `align_v4_session.assign_work_group`, `supplemental_report` |

## Delta5 (Sol1 and Sol2 ADMIT_WITH_FIXES on 03253edca)

| Finding | Change | Where |
|---|---|---|
| S1 F1 / S2 F1 supplemental and pool roles ignored | The committed-record reader counts only the frozen CALIBRATION pool (ordinary and supplemental sentinels, anchors, known-H and test members never enter m); supplemental captures stay authenticated in custody but are excluded from `captured_members`, zero-capture logic and the test-history branch | `align_v4_next_arm_packet.WindowRecord.eligibility`, `counted_captures` |
| S1 F2 / S2 F4 generated pair names | `spam_filter_update` / `bank_transfer_2` map explicitly to the count keys (same mapping as `series.PAIR_KEYS`); unknown pairs still refuse | `PAIR_NAMES` |
| S1 F3 / S2 F2 attempt id vs slot id | `slot_of` normalizes a validated `<slot>#<k>` to its slot for the previous-window comparison; full attempt ids stay in records, chain and rulings | `align_v4_series.bind_packet` |
| S2 F3 desk provisional ceiling dropped | The builder reads each calibration record's committed `series_desk_row` (mandatory) and carries `desk_eligible_benign` into the history; the series check refuses final counts above it | builder `desk_ceiling` |
| S2 F5 22-member ceiling | `CAPTURED_MAX` is 22 (supplemental sentinels count toward nothing); the series binding remains a second guard | `v4_cadence.CAPTURED_MAX` |

## R22 (RUN_STATE 234): Block 5 lessons applied to v4

| Item | Change | Where |
|---|---|---|
| R22-1 contention disclosure-only | Every member records its outside-tree CPU-seconds over its member span; a `contention.unmeasured` gap over 30 s is flagged and disclosed, never excluded; no `contention.*` code can exclude a member (desk and committed-record reader strip them; test over the catalog codes) | `v4_contention.py`, `align_v4_session.powermode_desk_check`, builder |
| R22-2 / R24 blind replacement windows | Six pre-declared windows C9-C14 (R24 cap C14: qualification 52.6 % at C10, 84.2 % at C12, 96.2 % at C14 at bar rate 1/4, e = .10; gate-admitted FPR invariant to the cap at b = 0, drift lowers it); T1-T3 keep their R15 seeds (66-89); contiguous reserve pool 100-147 (91-99 are reserved development indices; C13 132-139, C14 140-147), 8 per pair per window; armed in order ONLY to replace a STRUCTURAL bar (U1-U3 FAIL, whole-window capture failure, zero-capture refusal beyond the retry), never on scores, counts or to repair low m; a barred window contributes nothing (no partial use); exactly 8 admitted windows; `insufficient_calibration` if a pair is below 39 after 8 admitted or C14 is reached with fewer than 8 admitted; wired into the manifest generator, `calibration_stop` (`barred`) and the triage. Manifest bytes changed: the paired Sol seed check runs on the new sha | `align_v4_series.py`, `v4_cadence.py`, builder |
| R22-3 balance check | Exclusions + flags per member-second by condition and pair against the exposure-adjusted expectation, printed and disclosed (`balance_check`) | `v4_balance.py` |
| R22-5 tau_rel | 0.13 % (stress 0.21 %) of cell energy recorded as the Block 5 between-window prior; B3's tau = 0.5 s_r conversion to be checked at the first benign residual SD | `pilot_protocol_v4.md` |
