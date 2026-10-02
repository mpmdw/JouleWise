COLD SCIENCE GATE: ADMIT

# Cold science gate ruling: D-079 epoch 25G83, Revision 6, block 1 candidate

- Candidate: `2-candidate/candidate_acceptance_25g83_rev6.json`, sha256 `aa59ebb25dcb4f1bace8d529d7d96ecf4969fec77ab54a51bac5120272a69884`, acceptance id `d079_calibration_acceptance_v2_n24_25g83_r2`, n = 24.
- Registration: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, sha256 `d0034003a7e61683696b88662825d909dc4bb8ad23678edad6bbc8dfd4877b78` (Revision 6 sealed, carrying the Revision 5 screen and ceiling and the D-125 envelope).
- Judge: one non-interactive Claude Fable 5.1 session in the detached worktree `/Users/edr/code/JouleWise-coldgate-judge` at HEAD `1a62cc11c543ccc5cf825767285352e08f7454d5`, 2026-10-02. No campaign context was read beyond the packet, the files it names, the two harvest records, the member evidence under `/Users/edr/night-custody`, and the issuer code. No background task, no subagent, no git write, no sudo.
- Ruling: **ADMIT**. The candidate is a correct application of the pre-registered rules to this corpus. Every key quantity re-derives exactly from the primary artifacts by routes independent of the issuer. No refusal trigger should have fired. Two non-blocking observations are recorded in §6 for the D-138 gate; neither changes a member, a statistic or an operative.

## 1. Summary of what was verified

| Area | Result |
|---|---|
| Packet integrity | 130 of 139 MANIFEST entries verify in this worktree; the 9 missing files are `*.log` chain logs that `.gitignore` excludes from `docs/process_traces/**`. Their custody originals hash to the MANIFEST digests byte for byte and were read in their place. All 7 REFERENCES digests verify. |
| Membership (a) | Exactly two derivation-kind ledger sessions were opened after the pinned head (sequence 276); both match the id pattern, declared 12 slots, finalized all 12 slots `valid`, and are terminal. The 24 members' `manifest.json` and `instrument_evidence.json` hash to the ledger rows and to the candidate; each raw `b_fiducial_s` lexeme equals the ledger `exact_bound_lexeme_s` and the candidate lexeme; every stored clock anchor is method anchor-v3, status `bounded`, `clock_anchor_resolved: true`; every median frame is within 100 to 150 ms; no foreign row exists. `verify-members`: 24 PASS. |
| Source statistics (b) | min, max, range, mean, sample SD, per-window median/mean/SD, s_within, ICC, rho1 and the window-median range divided by S all recompute exactly in Decimal at 80 and 200 digits. |
| Quantiles and predictions (c) | My own Abramowitz and Stegun closed-form implementation (own arctan, own Machin pi, own bisection, 70-digit Decimal) agrees with all four published quantiles to all 20 printed decimal places. The three binary64 products reproduce the candidate's shortest round-trip decimals exactly. |
| S and C (d) | S = max(0.014531, 0.010818) = 0.014531; C = max(0.010164834757777545, 0.015100307220104515, 0.01550217418713139, 0.014531) = 0.01550217418713139, set by Q99_within; C minus S = 0.00097117418713139; level screen 0.036462861644980. All equal the candidate. |
| Refusal triggers (e) | No member above 0.25 s; zero members above 0.075 s; no excluded member and no non-registered exclusion mechanism; all five R9 clauses true from the per-slot record; both battery verdicts pass from raw ioreg bytes; every pin equals its sealed value; predecessor is P8 by id and digest; both disposing decision ids declared; successor id follows the approved pattern; first counting window has 12 valid; count rule replays to NEXT_WINDOW then CLOSE_AND_DERIVE. |
| Diagnostics (f) | Screen challenge count 4 recorded as diagnostic (Revision 5 dropped it as a veto, Revision 6 keeps it dropped); new maximum does not exceed 0.04262208300415633; headroom positive; per-window and serial diagnostics recorded and they trim nothing. |

## 2. Packet integrity

```
cd docs/process_traces/rev6-derivation-block1/packet && shasum -a 256 -c MANIFEST.sha256 | grep -v ': OK$'
```
Result: 9 `FAILED open or read` lines, all `*.log` files; every other entry OK. `git check-ignore -v` shows `.gitignore:45: docs/process_traces/**/*.log` for them. Custody originals:

```
shasum -a 256 /Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c{1-20261001T0617Z,2-20261001T2252Z}/{night.log,night/chain.stdout.log,night/chain.stderr.log,operator_logs/derivation-chain.log} \
  /Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0137Z/night.log
```
Result: all 9 digests equal the MANIFEST lines (`aec5d1f0…`, `a3a20e62…`, `681eebc6…`, `bb79392c…`, `37678a26…`, `3f1bc2e9…`, `0556b5fe…`, `896a7a88…`, `24354cd3…`).

```
shasum -a 256 -c docs/process_traces/rev6-derivation-block1/packet/REFERENCES.sha256
```
Result: 7 of 7 OK (two harvest records, issuer, chain, cap-rule text, roster, predecessor P8). The packet's registration copy and the tracked registration both hash to `d0034003…7b78`. Candidate, R9 record, run-3 stdout and verify-members stdout hash to the digests stated in `2-candidate/invocation.md` (`aa59ebb2…`, `8be16a20…`, `2ce73127…`, `d05ecd61…`).

## 3. Check (a): membership

### 3.1 Ledger
Script over `3-chain-logs-and-harvest/calibration_observation_ledger.jsonl` (376 rows):
- sequence contiguous 1..376; every `predecessor_digest` equals the previous `receipt_digest`; all 376 receipt digests recompute as sha256 of the row's canonical JSON without `receipt_digest`; the last digest equals the head pin `a5b825b7…7014` and the candidate's `ledger_cutoff` (376). Row 276's digest is `476e2ae8…9737`, the sealed `pins.ledger_head_pin_at_first_window`.
- Session-open rows in the whole ledger: sequences 78, 128, 178, 228 (the n1, n2, W1, W2 sessions, all before the pin) and 278 (`d079-epoch-25g83-r6-20261001T0617Z`) and 328 (`d079-epoch-25g83-r6-20261001T2252Z`), both `derivation`, each with 12 declared slots. No other session was opened after sequence 276, so the two sessions named at issuance are exactly the sessions of the registration (§7). Both ids match `^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$`. Neither is a null session.
- Slot rows: for each session, 12 claim rows and 12 finalization rows, every finalization `valid`, `os_build` 25G83, T1 `powermetrics_sha256` = `b762e5bf…30c5`, anchor method `powermetrics_native_second_rate_aware_set_membership_v1`. No abort row, no `window_exhausted` slot, no attempt left pending.
- Dispositions of finalized 25G83 rows: 47 valid, 25 ordinary-invalid. The 23 valid 25G83 rows outside the two sessions (4 + 7 from the 2026-09-19 sessions, 6 + 6 from W1/W2) are exactly the 23 rows of `configs/calibration/observation_dispositions.json` (sha256 `4a3d96da…effd`, equal to the sealed registry digest): 11 under `D-126-disposition-25G83-v3-2026-09-25`, 12 under `CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29`. The candidate declares both ids in `prior_observation_set.disposing_decision_ids`. No foreign row exists. Prior set: 110 observations (77 valid, 31 ordinary-invalid, 2 systematic-invalid), equal to the candidate's inventory.

### 3.2 Member evidence bytes
Script over the 24 `source_directory` entries under `/Users/edr/night-custody` (per member: sha256 of `manifest.json` and `instrument_evidence.json`; regex read of the raw `"b_fiducial_s": <lexeme>` text; `clock_anchor`, `clock_anchor_resolved`, `status`, `derivation_only`, `screen_basis.acceptance_id`, `bindings.os_build`, `battery_float.pre/post.passed`; content id as sha256 of the canonical JSON of the two digests). Result for all 24:

| Check | Result |
|---|---|
| custody path equals ledger `custody_locator` | 24/24 |
| manifest sha256 equals ledger row and candidate | 24/24 |
| instrument_evidence sha256 equals ledger row and candidate | 24/24 |
| raw `b_fiducial_s` lexeme equals ledger `exact_bound_lexeme_s` and candidate | 24/24 |
| content id recomputed equals ledger `content_id` | 24/24 |
| `clock_anchor.method` = anchor-v3 (`CLOCK_METHOD_V3`), `status` = `bounded`, `clock_anchor_resolved` = true | 24/24 |
| ledger disposition valid; evidence `status` valid; 59 pulses detected; 0 spurious plateaus; empty `reasons` | 24/24 |
| `derivation_only` true; `screen_basis.acceptance_id` = `d079_calibration_acceptance_v2_n17_r8` (P8) | 24/24 |
| `bindings.os_build` 25G83 (the only other `os_build` occurrences are P8's own epoch inside `screen_basis`) | 24/24 |
| battery_float pre and post observations present and `passed` | 24/24 |

Sanctioned command:
```
/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/.venv/bin/python scripts/issue_calibration_acceptance_generation.py verify-members --artifact docs/process_traces/rev6-derivation-block1/packet/2-candidate/candidate_acceptance_25g83_rev6.json --corpus-root /Users/edr/night-custody
```
Result: 24 lines `PASS`, exit 0.

### 3.3 Member values (ledger order)

| Session | Slot | b_fiducial_s |
|---|---|---|
| …0617Z (C1) | d01 | 0.025463179772367898 |
| | d02 | 0.02766399977693898 |
| | d03 | 0.03460915378691863 |
| | d04 | 0.027892564073153783 |
| | d05 | 0.0274417652193393 |
| | d06 | 0.02790192270133949 |
| | d07 | 0.02193176218569716 |
| | d08 | 0.030373696240460962 |
| | d09 | 0.033858213964584355 |
| | d10 | 0.025533661955889533 |
| | d11 | 0.030402083768569316 |
| | d12 | 0.027971479139464784 |
| …2252Z (C2) | d01 | 0.028443395186875983 |
| | d02 | 0.024007067914171086 |
| | d03 | 0.027381927068597392 |
| | d04 | 0.03633250571256254 |
| | d05 | 0.028114814464204912 |
| | d06 | 0.024958379592343757 |
| | d07 | 0.030679289625902346 |
| | d08 | 0.03646286164497997 |
| | d09 | 0.025013543792252485 |
| | d10 | 0.029091074834746312 |
| | d11 | 0.024497152758604247 |
| | d12 | 0.026633405691469065 |

### 3.4 Frame range and R9 record (§8 member condition "median frame in 100 to 150 ms")
Script over `2-candidate/r9_campaign.json` (sha256 `8be16a20…18a2`, equal to `docs/process_traces/rev6-derivation-block1/r9_campaign.json` at HEAD and at commit `344e63fc`): all 24 slots have `cap_trigger` null, `counted` true, `disposition` valid, `has_recording` true, `median_frame_reported` true, median frame between 124.805 and 130.336 ms, `ratio` = cells / 1,710,000 (maximum 0.1035), content id equal to the ledger row. The two per-window `r9_window.json` files in the packet hash to the record's `r9_window_sha256` values (`32b2b111…`, `fa490d32…`). Harness `scripts/cap_replay_harness.py` hashes to the sealed `692471b7…6839`. Counted 24, members 24, all five clauses true, `clock_movement_or_empty_fit_refusals` empty.

### 3.5 Count rule replay (§7), my own replay from the R9 record and the ledger
C1: not null, no stop line (median of per-capture medians 129.672 ms, 12 valid, no cap or deadline stop, max ratio 0.103, every frame reported), not adverse, counted 12, members 12, totals 12/12, fewer than 3 counting windows: NEXT_WINDOW. C2: totals 24/24: CLOSE_AND_DERIVE. Equal to the candidate's `revision6_count_replay` and to both harvest records' `next_window` blocks (C1 harvest `61273b09…`, cited as C2's `b_blind_checks.decision_sha256`).

### 3.6 Exclusion mechanisms (packet item 4)
`derivation_notes.excluded_members` is empty and the R9 record lists no clock-movement or empty-fit refusal. The assertion checks against the code: `anchor_v3_replay_outcome` (issuer lines 1826 to 1845) returns unresolved only for `anchor_method_not_v3`, the `clock_anchor_unresolved` reason or `status == "unknown"`, or `clock_anchor_not_marked_resolved`; the Revision 6 path refuses on a digest disagreement before interpreting the anchor. No member took any of those branches, so the question of whether a non-registered reason would have refused rather than excluded did not arise in this corpus.

## 4. Checks (b), (c), (d): statistics, quantiles, operatives

Command: `python3 /tmp/coldgate_recompute.py` (script reproduced in Appendix A; it reads only the candidate's member lexemes and the ledger slot map).

### 4.1 Source statistics, exact Decimal (precision 80, re-checked at 200)
| Quantity | Recomputed | Candidate | Equal |
|---|---|---|---|
| minimum (C1 d07) | 0.02193176218569716 | same | yes |
| maximum (C2 d08) | 0.03646286164497997 | same | yes |
| range | 0.01453109945928281 | same | yes |
| mean, quantized 1e-18 ROUND_HALF_EVEN | 0.028444120869643095 | same | yes |
| sample SD, quantized 1e-18 ROUND_HALF_EVEN | 0.003803438860221064 | same | yes |
| C1: n 12, median 0.0278972433872466365, mean 0.02842029021539368258…, SD 0.00353003458914322672… | | same | yes |
| C2: n 12, median 0.027748370766401152, mean 0.02846795152389250791…, SD 0.00421722839779789396… | | same | yes |
| s_within (df 22), quantized | 0.003888840415839957 | same | yes |
| ICC (MSB 1.36e-5 below MSW 1.51e-5, F = 0.0009) | 0 | 0 | yes |
| rho1, 22 adjacent-slot pairs, no ties | -0.18012422360248447204… | same | yes |
| range of window medians / S | 0.01024517382461527080… | same | yes |

### 4.2 Student-t quantiles by an independent route
mpmath is not installed in any available interpreter, so the independent route is my own code (Appendix A): the Abramowitz and Stegun 26.7.3 (odd df) and 26.7.4 (even df) finite closed forms, with arctan by argument halving plus Taylor series, pi by Machin's formula from that arctan, and 260 bisection halvings over (0, 100), all in 70-digit Decimal. A float composite-Simpson integration of the density (200,000 panels) confirms the CDF at each quantile to 12 places.

| df | p | My quantile (24 places) | Candidate (20 places) | Absolute difference |
|---|---|---|---|---|
| 23 | 0.975 | 2.068657610419048651508524 | 2.06865761041904865151 | 1.5e-21 |
| 23 | 0.995 | 2.807335683769999002931101 | 2.80733568376999900293 | 1.1e-21 |
| 22 | 0.975 | 2.073873067904026165846478 | 2.07387306790402616585 | 3.5e-21 |
| 22 | 0.995 | 2.818756060600143498533825 | 2.81875606060014349853 | 3.8e-21 |

Each published value is the correct rounding of my value to 20 places. Evaluating my survival function at the published 20-place quantiles gives probability residuals of 7.5e-23, 1.3e-23, 1.8e-22 and 4.4e-23, consistent with a quantile rounded at the 21st place times a density of order 0.05 to 0.01. The candidate's recorded residuals (2.4e-80 and smaller) refer to its 80-digit internal quantile, within the declared bound 1e-30; its recorded agreement digit counts (55 to 57) exceed the declared bound 30. Both quantile-proof blocks (df 23 and df 22) carry the quantiles, residuals, digit counts, both bounds, the closed-form method string and precision 80, as the registration requires.

### 4.3 Two-draw predictions in binary64
`repr(float(t) * float(sd_lexeme) * math.sqrt(2))`, the issuer's left-to-right order:

| Prediction | Recomputed | Candidate | Equal |
|---|---|---|---|
| Q95 = t(0.975, 23) × 0.003803438860221064 × √2 | 0.01112705033143238 | same | yes |
| Q99 = t(0.995, 23) × 0.003803438860221064 × √2 | 0.015100307220104515 | same | yes |
| Q99_within = t(0.995, 22) × 0.003888840415839957 × √2 | 0.01550217418713139 | same | yes |

The exact Decimal products are 0.011127050331432378…, 0.015100307220104514…, 0.015502174187131390…, so each binary64 result is the correctly rounded shortest decimal. The within-window value is recorded under its own rule string, and the sealed `TWO_DRAW_PREDICTION_RULE` string describes only Q99, as §9 requires. The ratio Q99_within / Q99 = 1.02661 is below the §9 bound r = 1.02663 for n = 24, K = 2.

### 4.4 Operatives (d)
- Quantized range: 0.01453109945928281 → 0.014531 (1e-6, ROUND_HALF_EVEN). S = max(0.014531, 0.010818) = 0.014531; the range arm won, so `floor_bound: false`; the rule name `floored_range_envelope_screen` is recorded independent of the arm, as Revision 1 requires.
- Predecessor ceiling read from `configs/calibration/calibration_acceptance_d079_v2_n17_r8.json` (sha256 `52e3d18a…a13`, `derivation_sha256` `911d06c3…acd`, `acceptance_id` P8): `ratified_operatives.maximum_budgetable_drift_s` = 0.010164834757777545.
- C = max(0.010164834757777545, 0.015100307220104515, 0.01550217418713139, 0.014531) = 0.01550217418713139, set by Q99_within (candidate `ceiling_set_by: ["Q99_within"]`). C − S = 0.00097117418713139. S < C strictly; headroom positive, no `zero_headroom`.
- Preflight level screen: 0.03646286164497997 quantized to 1e-15 ROUND_HALF_EVEN = 0.036462861644980.
- `registered_generation_row` carries the same four operatives, both predictions, the within-window prediction, `corpus_n` 24, `corpus_doubles_from_24_to_48`, cutoff 376, P8 as predecessor with its ceiling, both session ids, `registration_revision` 6.
- `derivation_sha256` and `derivation_input_sha256` recompute with the issuer's own canonicalization functions (`677f37ce…bcef`, `2adb4ff4…28e1`).

## 5. Checks (e) and (f): refusal triggers, pins, diagnostics

| Trigger or pin | Evidence | Fired? |
|---|---|---|
| Member B > 0.25 s (`PLATEAU_INSET_S`) | maximum 0.03646 s | no |
| Two or more members > 0.075 s (`excursion_limited`) | 0 members | no; `excursion_member_count` 0, no label |
| Retained n below 12 | 24 | no |
| Non-registered exclusion mechanism | no exclusion at all | no |
| R9 cell stop, deadline stop, ratio > 0.5, unreported frame | none; max ratio 0.103; 24/24 frames reported | no |
| STOP-CADENCE (> 150 ms) | 129.672 ms, 129.648 ms | no |
| STOP-FUTILITY (first counting window < 6 valid) | 12 valid | no |
| Adverse window (A-R5b) | `battery_float_verdict.json` c1 sha `6b8ce0c5…`, c2 sha `eb138080…` (equal to the candidate's `battery_verdict_records`), status pass, 12/12 slot verdicts pass each; every slot's `raw/battery_float.pre.ioreg` and `.post.ioreg` under custody hash to the verdict's digests; t0 night-gate C3 battery predicate passed (0 mA, not charging, AC) | no |
| STOP-NULL-REPEAT | no null session exists | no |
| Foreign same-epoch rows (A-7) | none; 23 set-aside rows under the two declared decisions | no |
| Pre-registration digest | `d0034003…7b78` in the candidate, both harvest records, both arm environments and both night-gate C1 receipts | match |
| Estimator pins (4 files), validator `3dc75857…`, prewindow_check `d8458eea…`, chain `b5beea46…`, harness `692471b7…`, cap-rule text `6b4bcaea…`, roster `d8fbb403…`, launch templates `e62a461b…` and `1570b745…`, registry `4a3d96da…`, cap 1,710,000 | all recomputed at this worktree and equal to the sealed §7 `pins`; both windows' `chain.zsh.chain-source.sha256` equal the chain pin; both arm step-2 pin checks PASS | match |
| Machine pins | `powermetrics_sha256` `b762e5bf…` in every member row and in both T1 bindings; MLX 0.31.2; `os_build` 25G83 | match |
| Predecessor identity | P8 by id, file digest and derivation digest; predecessor epoch 25F84 differs from the target | match |
| Successor id | `d079_calibration_acceptance_v2_n24_25g83_r2`, pattern with N = 24, not the retired r1 id | match |
| Start-condition records (§6.2, §7) | `night/start_conditions.json` c1 `da1b4df0…`, c2 `e46d5fce…` (equal to the candidate); entries a to g present; every named evidence file in the packet hashes to its entry; clean dwell: script sha equals the pin, exit 0, `continuous_clean_s` 600; network-time receipts 633 s before chain start and 1243 s and 1246 s before each window's first capture on wall and monotonic clocks, same boot id; thermal, HID idle 0, load 1.59 and 0.45, agent census empty | pass |
| Blindness and sequence (§10) | both sessions terminal before `prepare-candidate`; the R9 commit `344e63fc` (14:55 PDT) is an ancestor of HEAD and precedes the first commit carrying a B of these windows (`0d3f6caf`, 16:02 PDT); C1's ledger pin commit `029ec385` (01:57 PDT) precedes C2's session open (16:02 PDT); harvest commits `cc58414b`, `47e16dcc`, `3d797485` are ancestors of HEAD | pass |
| Screen challenge (diagnostic) | members above 0.032898493715362: C1 d03, C1 d09, C2 d04, C2 d08 (4); the candidate's per-member flags and the hashed evidence `exceeds_prior_level_screen` flags agree; recorded under `rule_outcomes` as a count, and the issuer skips the veto under Revision 5 and 6 (issuer line 2781) | recorded, no veto, as the registration says |
| Prior maximum plus range (diagnostic) | Decimal 0.03289849371536248 + 0.00972358928879385 = 0.04262208300415633 from P8's own `source_statistics`; 0.03646 does not exceed it | recorded false |
| Known conditions (item 8) | verbatim registration lines 262 to 278; `displaysleep` 0 and HID idle 0 recorded in both receipts; no threshold moved | recorded |

Chain logs (custody originals, MANIFEST-matched): each window logs `session_open kind=derivation slots=12`, `settle_complete settle_s=600`, twelve `slot_start`/`slot_end … disposition=valid` pairs at a 600 s pitch, and `derivation_night_complete slots=12`; no `slot_unused`, abort or `window_exhausted` line; chain exit code 0; night-gate verdict GO, class `DIAGNOSTIC_NO_PACK`, conditions C1 PASS, C2 NOT_APPLICABLE, C3 to C5 PASS. Window timing in the candidate (durations 7424.121 s and 7428.155 s, start-to-start 59699.253 s, gap 52275.132 s) recomputes from `chain.started` and `chain.exited`.

Reproducibility: re-running `prepare-candidate` from this worktree with the packet ledger and the committed harvest records regenerated an R9 record identical to the committed one in every field except the four absolute `pinned_files.*.path` strings (digests equal), and the issuer then refused by design because that regenerated record is not committed at HEAD. Nothing in the worktree changed (`git status --porcelain` empty before and after).

## 6. Non-blocking observations for the D-138 gate

1. **Network-time receipt wording versus the sealed §5 text.** Both windows' `night/network_time_off.json` record exit 0 and stdout `Network Time is already off.`, while §5 says the receipt's standard output is "exactly `setUsingNetworkTime: Off`". The driver's recognizer (`joulewise/network_time_off.py`, `ADMITTED_OFF_STATEMENTS`) admits both macOS wordings of the OFF end state; that change landed in commit `2431dcaa` (2026-09-30 21:13 PDT), after the seal commit `46643f1d` (15:09 PDT) and after the first C1 attempt (`c1-20261001T0137Z`) was refused at t0 on the single-wording recognizer. The registration text was not amended. I rule this does not defeat condition (f): the receipt proves the required end state (network time OFF, exit 0, same boot, more than 600 s before the first capture on both clocks, 1243 s and 1246 s realized), and under §5's own requirement that network time "stays OFF" between windows, the setter necessarily prints the "already off" wording whenever the optional ON-then-OFF resync is not taken, so a literal reading would make the optional resync mandatory and contradict the text. The issuer's registered checks for this condition (one receipt, plan binding, settle at least 600 s) pass. The gap between the sealed wording and the recognizer should be closed by an erratum or a written ruling before the successor issues; it changes no number.
2. **Thermal condition (d) is satisfied vacuously.** `pmset -g therm` on this machine prints only "No thermal warning level has been recorded" lines and no `CPU_Speed_Limit` line; the receipt stores `cpu_speed_limit: null` and the gate's existing thermal predicate passed. The registration defines (d) as "the night gate's existing check", so this is as registered, but the phrase "every `CPU_Speed_Limit` as 100" describes an output this build does not emit.
3. **Two zero-capture refusals preceded C1.** `c1-20261001T0137Z` was refused at t0 (`night_probe_error`, "network time OFF receipt not admitted") and `c1-20261001T0555Z` at the arm battery gate (InstantAmperage −447 mA). Neither opened a ledger session or wrote a slot, so neither is a session or a null session under §7, and the issuer's session enumeration is unaffected. A-R5b licenses "one new-plan successor" per such refusal; whether a chain of two successors is within D-182's terms is for review, not for this gate, and it cannot select on any value because nothing was captured.
4. **Packet as committed omits its chain logs.** The nine `*.log` files listed in `MANIFEST.sha256` are gitignored and absent from the committed packet; a reader of the repository alone cannot verify item 3 without the custody originals. Consider committing them under a non-ignored name or recording that they live only in custody.
5. **R9 record embeds absolute worktree paths** (`pinned_files.*.path` under `/Users/edr/code/JouleWise-derive-rev6b1/`), which is why the record cannot be regenerated byte-identically from another checkout even though every digest and slot entry matches. Not a correctness issue.
6. **Candidate `selection` text omits the frame-range condition** that Revision 6 §8 adds to membership (it names only valid disposition and a resolved anchor). All 24 valid captures are within 100 to 150 ms, so the text's omission excluded nothing here; the frame condition was applied through the count replay and the issuer's `frame_excluded` path.

## 7. Outcome

ADMIT. Membership, every statistic, both degrees of freedom's quantiles, the three predictions, S, C and the level screen re-derive exactly from the primary artifacts; no registered refusal should have fired; diagnostics are recorded as diagnostics. The D-138 transaction remains the issuer of record and is outside this ruling.

## Appendix A: recomputation script (run as `python3 /tmp/coldgate_recompute.py` from the packet directory)

```python
import json, math, statistics
from decimal import Decimal, ROUND_HALF_EVEN, localcontext, getcontext
cand=json.load(open('2-candidate/candidate_acceptance_25g83_rev6.json'))
mem=cand['derivation_corpus']['members']
led=json.load(open('/tmp/coldgate_ledger_members.json'))   # {member_id: {slot, custody_locator, ...}} extracted from the packet ledger's finalization rows
vals=[Decimal(m['b_fiducial_s']) for m in mem]; ids=[m['member_id'] for m in mem]
ss=cand['decimal_derivation']['source_statistics']; Q=Decimal('0.000000000000000001')
with localcontext() as c:
    c.prec=80
    n=Decimal(len(vals)); mean=sum(vals,Decimal(0))/n; sd=(sum((v-mean)**2 for v in vals)/(n-1)).sqrt()
    mn=min(vals); mx=max(vals); rng=mx-mn
    print("min",mn,mn==Decimal(ss['minimum_s']),"max",mx,mx==Decimal(ss['maximum_s']),"range",rng,rng==Decimal(ss['range_s']))
    print("mean q",mean.quantize(Q,rounding=ROUND_HALF_EVEN),"sd q",sd.quantize(Q,rounding=ROUND_HALF_EVEN))
with localcontext() as c:
    c.prec=200
    win={}
    for m in mem: win.setdefault(led[m['member_id']]['custody_locator'].split('/')[4],[]).append(Decimal(m['b_fiducial_s']))
    K=len(win); N=len(vals); ssw=Decimal(0); mean2=sum(vals,Decimal(0))/N
    for k,v in win.items():
        wm=sum(v,Decimal(0))/len(v); ssw+=sum((x-wm)**2 for x in v)
        print("window",k,len(v),"median",statistics.median(v),"mean",str(wm)[:22],"sd",str((sum((x-wm)**2 for x in v)/(len(v)-1)).sqrt())[:22])
    print("s_within q",(ssw/Decimal(N-K)).sqrt().quantize(Q,rounding=ROUND_HALF_EVEN))
    msb=sum(Decimal(len(v))*((sum(v,Decimal(0))/len(v))-mean2)**2 for v in win.values())/(K-1); msw=ssw/Decimal(N-K)
    n0=(Decimal(N)-sum(Decimal(len(v))**2 for v in win.values())/N)/(K-1)
    print("ICC",max(Decimal(0),(msb-msw)/(msb+(n0-1)*msw)),"F",str(msb/msw)[:10])
    meds=[statistics.median(v) for v in win.values()]; print("median range / S",str((max(meds)-min(meds))/Decimal('0.014531'))[:30])
pairs=[]
for k in win:
    slots={led[m['member_id']]['slot']:Decimal(m['b_fiducial_s']) for m in mem if led[m['member_id']]['custody_locator'].split('/')[4]==k}
    for s in range(1,12):
        a,b=f"d{s:02d}",f"d{s+1:02d}"
        if a in slots and b in slots: pairs.append((slots[a],slots[b]))
def ranks(xs):
    srt=sorted(xs); return [Decimal(srt.index(x)+(len(srt)-1-srt[::-1].index(x))+2)/2 for x in xs]
with localcontext() as c:
    c.prec=80
    L=ranks([p[0] for p in pairs]); R=ranks([p[1] for p in pairs]); lm=sum(L)/len(L); rm=sum(R)/len(R)
    print("rho1",str(sum((a-lm)*(b-rm) for a,b in zip(L,R))/((sum((a-lm)**2 for a in L)*sum((b-rm)**2 for b in R)).sqrt()))[:25],"pairs",len(pairs))
getcontext().prec=70
def d_atan(x):
    x=Decimal(x); k=0
    while abs(x)>Decimal('0.1'): x=x/(1+(1+x*x).sqrt()); k+=1
    term=x; s=x; x2=x*x; i=1
    while abs(term)>Decimal(10)**-75: term=-term*x2*(2*i-1)/(2*i+1); s+=term; i+=1
    return s*(2**k)
PI=4*(4*d_atan(Decimal(1)/5)-d_atan(Decimal(1)/239))
def A_two_sided(t,nu):              # P(|T|<=t), A&S 26.7.3 (odd nu) / 26.7.4 (even nu)
    t=Decimal(t); th=d_atan(t/Decimal(nu).sqrt()); c=1/(1+t*t/nu).sqrt(); s=t/Decimal(nu).sqrt()*c; c2=c*c
    if nu%2==1:
        total=Decimal(0); term=c; j=3; total+=term
        while j<=nu-2: term=term*c2*Decimal(j-1)/Decimal(j); total+=term; j+=2
        return 2/PI*(th+s*total)
    total=Decimal(1); term=Decimal(1); j=2
    while j<=nu-2: term=term*c2*Decimal(j-1)/Decimal(j); total+=term; j+=2
    return s*total
def quantile(p,nu):
    target=2*Decimal(p)-1; lo=Decimal(0); hi=Decimal(100)
    for _ in range(260):
        mid=(lo+hi)/2
        if A_two_sided(mid,nu)<target: lo=mid
        else: hi=mid
    return (lo+hi)/2
res={}
for df in (23,22):
    for p in ('0.975','0.995'): res[(df,p)]=quantile(p,df); print(df,p,str(res[(df,p)])[:26])
sdl=ss['sample_sd_presentation_s']['value']; swl=cand['decimal_derivation']['within_window_prediction_derivation']['s_within_presentation_s']['value']
for label,tv,sdx in (("Q95",res[(23,'0.975')],sdl),("Q99",res[(23,'0.995')],sdl),("Q99_within",res[(22,'0.995')],swl)):
    print(label, repr(float(tv)*float(sdx)*math.sqrt(2)))
rng=Decimal(ss['range_s']); S=max(rng.quantize(Decimal('0.000001'),rounding=ROUND_HALF_EVEN),Decimal('0.010818'))
C=max(Decimal('0.010164834757777545'),Decimal(ss['prediction_99_two_draw_s']),Decimal(ss['prediction_99_within_window_two_draw_s']),S)
print("S",S,"C",C,"C-S",C-S,"level",Decimal(ss['maximum_s']).quantize(Decimal('0.000000000000001'),rounding=ROUND_HALF_EVEN))
```
