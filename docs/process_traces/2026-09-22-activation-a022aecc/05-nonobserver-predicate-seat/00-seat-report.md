# Seat report — lane QPE01-NONOBSERVER-PREDICATE-01 (brief 04), original landing and fix round 1

Branch `feat/2026-09-23-qpe01-registration-v3-nonobserver`, linked worktree
`JouleWise-wt-v3-a022aecc`. The original seat landed c8e6408b and 16900e3d and
was killed before writing this report. This report is written by the fix-round-1
seat (Opus 5.5, 2026-09-23). It covers both the original landing and this
round (commits 38d5052c … 2ff07212, one per fix item F1–F16; F11 is this file).

Terms used below, in plain words:

- **Envelope**: one 600-second capture slot of the pilot night; twelve per night.
- **Observer process**: a process the measurement itself started: the executor
  (the root of the night's process tree) and everything descended from it
  (collector, `sudo`, `powermetrics`, `top`, census, the 30-second recorder).
  Every other process is a **non-observer**.
- **Journal**: the 30-second recorder's file `evidence_busy_cores.jsonl`; each
  row names the busiest processes (`top_consumers`) and marks each one
  `observer: true` or `false`.
- **Whole**: `whole_envelope_observer_cpu_s`, the collector process's own CPU
  plus the CPU of every child it reaped, over one envelope
  (`RUSAGE_SELF + RUSAGE_CHILDREN`, `scripts/sample_quiet_predicate_evidence.py`
  `cpu_total`).
- **Span**: the collector's own clock window for the envelope,
  `end_stamp.monotonic_before_s − start_stamp.monotonic_before_s`.
- **Observer floor**: Σ whole ÷ Σ span over the night's readable envelopes, in
  cores (CPU-seconds per second).
- **Counterfactual**: the input or code state on which a test must fail if the
  defect it guards were present. **Failing-before evidence**: the failure line
  the test printed when run against the code before its fix.
- **Contract lenses**: the two read-only reviews of 16900e3d that this round
  cures — Opus (`lens-opus-contract.md`, findings S1–S7, N1–N10) and Fable
  (`lens-fable-contract.md`, findings S1–S7, N1–N10). Their files live in the
  magistrate's job scratch area (`~/.claude/jobs/7a0f14bd/tmp/`), not in the repo.

## 1. What the original landing did (3b921fe1 → 16900e3d, 13 files, +1667 −58)

- **Registration v3** (`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`):
  v2 plus the `non_observer_process_busy` exclusion and rule object (30
  core-seconds per envelope, abort after 2 consecutive), `t0_non_observer_share_max: 0.5`,
  the `observer_floor` object, and ruling 10's `ruling` append. Chain digest unchanged.
  Pinned in `night_gate.RULED_REGISTRATIONS`; v2 kept as superseded history.
- **Observer marking**: the recorder is run with the executor's pid
  (`--observer-pid`), so `sample_interval` marks every process descended from
  the chain root.
- **Per-envelope rule** in `pilot_summary`: per non-observer process (pid plus
  start time), Σ busy cores × interval seconds over journal rows lying wholly
  inside the envelope; ≥ 30 core-seconds excludes the envelope and names the
  process, pid and core-seconds.
- **t0 and arm-check predicate**: one 30 s observation; any non-observer at
  ≥ 0.5 busy cores refuses (`night_refused_not_quiet` at t0 with ruling 10's
  exact detail text; `armable: false` at the arm check).
- **Abort**: two consecutive excluded envelopes end the chain with a typed
  refusal, reason `non_observer_process_busy`.
- **Observer floor** (synthesis 35 interim): Σ whole ÷ Σ span, per-envelope
  components, `observer_variation_cores` (sample standard deviation of the
  per-envelope shares); the v2 stop branch unchanged in form, fed the corrected number.
- **Forced edits outside the brief's scope**: `joulewise/arm_retry.py`,
  `tests/test_arm_retry.py`, `docs/phase_2/derivation_night_runbook.md` (see §6).
- **Diagnostic re-analysis** script and output in this directory.

## 2. What fix round 1 did (16900e3d → 2ff07212, 11 files, +755 −108)

| Item | Commit | Change |
|---|---|---|
| F1 (Opus S1, magistrate ruling) | 38d5052c | The 30 s load recorder is launched by the EXECUTOR as the collector's sibling, so it is not inside whole. `power_recorder_residue` = whole − round_block (no load-recorder subtraction). Each component carries `cpu_s` and `inside_whole` (round_block and residue true, load_recorder false). New reported-only `observer_floor_including_load_recorder_cores` = (Σ whole + Σ load_recorder) ÷ Σ span. The registration's `observer_floor.components` text (magistrate-authored, not ruled) says so in plain words; the four ruled strings are unchanged byte for byte. `observer_floor_components_role` states the same fact. |
| F2 (Opus S2, Fable N5) | 18029a86 | `pilot_summary` always writes its own re-derived list under `non_observer_process_busy` (empty when clean), keeps the executor's in-chain list under `executor_non_observer_process_busy`, and records `non_observer_verdict_disagreement`. |
| F3 (Opus S3, Fable S1) | 15ef8f2b | `machine_quiet_check` turns any sampler or `non_observer_offender` exception into `Refused("non-observer interval observation failed: <type>: <message>")`, so `check()` writes `check.json` with `armable: false`. |
| F4 (Opus S4) | d41a64bb | `Refused` gains an optional `evidence` mapping merged into the failing row; the non-observer refusal persists `top_consumers_at_decision`, `interval_s`, `bar_busy_cores`. |
| F5 (Opus S6) | ff65cae9 | Guard test (not defect-shaped): a root recorded under v2 still classifies `retained`. |
| F6 (Opus N3) | d156609b | v3 table entry's `records` gain ruling 31 and synthesis 35; comment reads "rulings 10 and 31; syntheses 15, 25 and 35". |
| F7 (Opus N5, Fable S6) | e53fefa9 | README names v3 (digest, ruling 10 and ruling 31 as adjudicated by synthesis 35), corrects the observer-cost sentence, and adds one paragraph on the three non-observer rules. The summary's `observer_definition` = the ruled `definition` sentence + ", with the 30 s load recorder a sibling process reported beside it (see observer_floor_components_role)". |
| F8 (Opus N6, Fable N3) | f6cdeef5 | Test: `night_gate.T0_NON_OBSERVER_SHARE_MAX` == the registration's `t0_non_observer_share_max`. |
| F9 (Opus N7, N8) | 28b84b98 | Test comment counts five keys; the floor test's fixture gains round clock support so its stated counterfactual (0.0017 cores on main) actually happens. |
| F10 (magistrate; Ed's D-182 addendum 2026-09-23 01:06 PDT) | ce2f13e5 | The abort's cause text in `arm_retry.COLD_GATE_CODES` and its two byte-identical table copies names the one licensed new-plan successor (lane QPE01-ABORT-SUCCESSOR-01; none until that lane lands). |
| F12 (magistrate bench finding, Fable S7) | dc6c4bb9 | (a) The LifecycleTests' shared arguments inject the module's one fake observation; a module-level guard makes the production sampler raise inside `tests/test_evidence_night.py`. (b) `check()` runs `machine_quiet` only when the sealed custody `chain.zsh` has payload kind `quiet_predicate_evidence` (read with the gate's own `probe_payload_kind`), otherwise records `{verdict: skipped, reason: "not an evidence night", payload_kind}`; an unreadable kind fails closed. |
| F13 (Fable N1) | 2f31898b | v3 re-serialised in v2's canonical form (`json.dumps(obj, sort_keys=True, indent=2) + "\n"`); digest computed once from those bytes and pinned in the gate constant, the test literal and the README. |
| F14 (Fable N4) | d0dc4a1a | C3's PASS detail names the non-observer predicate when it ran; a calibration receipt keeps its historical text. |
| F15 (Fable S5) | 3a4844c8 | The archive test asserts each night's replay-guard state (0217 `REPLAY_NEVER_EVIDENCE`, 2100 `SPREAD_RECORDED`). |
| F16 (Fable N8, adopted) | 2ff07212 | On a v3 night, journal rows that name processes but mark none raise `ValueError("recorder journal carries no observer-marked consumer; ancestry marking failed")`. |

## 3. Registration and table digests

| State | v3 registration SHA-256 | `RULED_REGISTRATIONS` serialization SHA-256 |
|---|---|---|
| 16900e3d (original landing) | `b6cb513fe4aa8b2c5557b589fae07ef4149d480cd1c831aa267ecb37c97104fa` | `c91f6898f0cb2e484c4c0c11a63172a9af0184edec1ff1cbec675d6c0a68c717` |
| after F1 (components text) | `9491bc370b515c7d56d21f87e0c6721be8cb2b6501b430b9dce75a93f59a6f0a` (interim) | `1499b108886972e73c6e4361d76b455b31f4846a643248dc2a9896a7daed7dbe` |
| after F6 (records) | unchanged | `8b394f8e3e373cf2fd94493b918ea91a29eff863c66231a29d7a9564c6cd8fae` |
| **after F13 (canonical form) — final** | **`69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616`** | **`9ad277ce180bc5289e2e29391c20312a95a0847f72ba09bfeb32ade841e851a6`** |

The final registration bytes differ from 16900e3d's only in the
`observer_floor.components` string and in key order/indentation (parsed
objects otherwise equal). v2 (`2c539240…79f1`) and v1 are unchanged. The
chain digest `568a2771…51b7ea` is unchanged.

## 4. Regression ledger

"Main" is 3b921fe1 (before the lane). "Pre-fix" is 16900e3d (before this
round). Failing-before runs for this round used a scratch copy of the
16900e3d tree (`git archive 16900e3d`, made a standalone git repository under
/tmp so the tests that clone the repository work) with this round's final
four test files laid over it; nothing in any worktree was touched.

### 4a. Original landing (reconstructed by the Opus and Fable lenses)

| Test | Regression | Counterfactual | Before (main) |
|---|---|---|---|
| `test_regression_0_the_chain_root_marks_the_power_sampler_the_recorder_pid_does_not` | R0 mechanism | sibling process table | passes on main (documents the mechanism; not defect-shaped) |
| `test_regression_0_the_recorder_refuses_to_run_without_a_chain_root` | R0: no pid refuses | pid missing/0/−1/"1000"/1000.0 | hangs on main (real sampler starts) |
| `test_regression_0_record_covariates_hands_the_pid_to_every_observation` | R0: pid forwarded | `sample_interval` without `observer_pid` | ERROR: unexpected keyword `observer_pid` |
| `test_regression_0_the_executor_launches_the_recorder_with_its_own_pid` | R0: executor passes its pid | argv without `--observer-pid` | FAIL: `'--observer-pid' not found` |
| `test_regression_1_a_full_core_daemon_excludes_every_envelope_it_ran_in` | R1 (synthetic) | 20 rows × 0.9995 cores × 30.355 s | FAIL: excluded lists empty |
| `test_regression_6_the_integral_catches_the_burst_a_median_would_admit` | R6 | 8 × 1.5 cores | FAIL: `[] != ['non_observer_process_busy']` |
| `test_a_v2_night_never_emits_a_reason_its_registration_does_not_carry` | v2 guard | v2 protocol; half-written rule | ERROR: no `non_observer_rule` |
| `test_regression_3_two_consecutive_exclusions_abort_the_chain_by_name` | R3 | busy envelopes {1, 2} | FAIL: rc `0 != 2` |
| `test_regression_3_one_exclusion_then_a_clean_envelope_never_aborts` | R3 counterfactual | busy {1, 3} | FAIL |
| `test_regression_2_frozen_protocol_takes_v3_and_refuses_v1_and_v2` | item 1 | v2 bytes | FAIL: PROTOCOL_PATH still v2 |
| `test_every_superseded_registration_is_history_and_never_armable` | R4 limbs 1–2 | v2 plan | ERROR: no V2 constant |
| `test_ruled_registration_serialization_requires_dated_ruling_amendment` | table re-pin | — | FAIL: digest differs |
| `test_a_busy_non_observer_process_refuses_at_t0_and_at_the_arm_check` | R2 at t0, both branches | fseventsd 0.6 cores unmarked/marked | ERROR: `Probes` has no `observe_interval` |
| `test_the_non_observer_predicate_is_spent_only_on_an_evidence_night` | R2 scope | calibration payload | ERROR |
| `test_an_unreadable_or_unmarked_observation_is_a_probe_error_never_a_pass` | R2 fail-closed at t0 | sampler raises; no metrics; unflagged | ERROR |
| `test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text` | R2 arm half | fseventsd 0.998 | ERROR: no `quiet_observer` |
| `test_the_floor_is_the_whole_envelope_over_the_collectors_own_span` | 6(a)/(b) | round block 1 s, whole 105 s | ERROR on main: `TypeError` on None (cured to a numeric failure by F9, below) |
| `test_the_variation_is_the_sample_sd_of_the_per_envelope_shares` | 6(a) | alternating ±2 s | ERROR: no `observer_variation_cores` |
| `test_a_session_without_the_whole_envelope_cost_or_span_refuses` | 6(d) | drop whole / start / end stamp | FAIL: ValueError not raised |
| `test_both_archived_nights_re_derive_to_the_corrected_floor` | 6(d) | archive bytes | FAIL: `0.05309837244298898 != 0.17572` |
| `test_every_cold_assignment_is_explicit` (arm_retry) | registry consistency | — | FAIL: code missing (forced the out-of-scope files) |

### 4b. This round

| Test (new or changed) | Item | Counterfactual | Failing-before line (pre-fix modules) | After |
|---|---|---|---|---|
| `ObserverFloorTests.test_the_residue_no_longer_subtracts_the_sibling_load_recorder` (new) | F1(a) | load recorder 0.2 s > 0 per envelope: old formula 105 − 1 − 0.2 = 103.8, ruled 105 − 1 = 104.0 | `TypeError: 'float' object is not subscriptable`; numeric probe on the 16900e3d module: `16900e3d residue on the F1 fixture: 103.8 (ruled: 104.0)`, and `observer_floor_including_load_recorder_cores` absent | OK |
| `…test_the_floor_is_the_whole_envelope_over_the_collectors_own_span` (changed) | F1(b), F9 | inside-whole identity round_block + residue == whole within 1e-9, labelled definitional; round clock support added | pre-fix: `AssertionError: 1.0 != {'cpu_s': 1.0, 'inside_whole': True}`; main (3b921fe1): `AssertionError: 0.0016666666666666668 != 0.175 within 7 places` | OK |
| `…test_both_archived_nights_re_derive_to_the_corrected_floor` (changed) | F1(c), F15 | archive bytes; companion 0.183 / 0.166 ± 0.002; floor 0.1757 / 0.1591; guard state per night | `TypeError: 'float' object is not subscriptable` (×2) | OK |
| `…test_the_registration_pins_the_corrected_components_text` (new) | F1(d), F13 | literal digest pin; four ruled strings verbatim; components text names the sibling fact | `AssertionError: 'b6cb513f…104fa' != '69321c69…3616'` | OK |
| `NonObserverAbortTests.test_regression_5_the_summary_re_derives_the_executors_own_exclusion_set` (rewritten) | F2 | reads the summary's and the executor's lists under distinct keys; `excluded` follows the summary's list | `KeyError: 'executor_non_observer_process_busy'` | OK |
| `…test_regression_5_a_tampered_executor_verdict_is_caught_not_passed_through` (new) | F2 mutation | executor's list on clean envelope 02 tampered to name `fakeoffenderd` | `KeyError: 'executor_non_observer_process_busy'`; probe on the 16900e3d module: `tampered envelope 02: non_observer_process_busy = ['fakeoffenderd'] excluded = []` and the old comparison read `{1: [], 2: ['fakeoffenderd'], 3: ['fseventsd'], 4: []}` — the pass-through the test now catches | OK |
| `NonObserverProcessTests.test_regression_1_…` (changed) | F2 / Fable N5 | clean envelope must carry the key, empty | `KeyError: 'non_observer_process_busy'` | OK |
| `PrepareTests.test_the_arm_check_records_an_unreadable_observation_as_not_armable` (new) | F3 | malformed consumer; sampler raises RuntimeError; no metrics | three escaping errors: `joulewise.night_gate.ProbeError: malformed consumer in the non-observer observation`, `RuntimeError: top died`, `joulewise.night_gate.ProbeError: non-observer observation carries no metrics` | OK |
| `PrepareTests.test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text` (changed) | F4 | fail row must carry `top_consumers_at_decision` naming fseventsd | `KeyError: 'interval_s'` | OK |
| `LifecycleTests.test_a_root_recorded_under_the_superseded_v2_registration_stays_retained` (new) | F5 | GUARD, not defect-shaped: holds by construction | passes on pre-fix (expected) | OK |
| `EvidenceRegistrationTests.test_the_v3_entry_cites_every_adopted_cold_gate_record` (new) | F6 | records must hold ruling 31 and synthesis 35, not ruling 21 | `AssertionError: '…/31-coldgate-fable-observer-floor-design-ruling.md' not found in (…)` | OK |
| `…test_ruled_registration_serialization_requires_dated_ruling_amendment` (re-pinned ×3) | F1, F6, F13 | table bytes | `AssertionError: 'c91f6898…c717' != '9ad277ce…51a6'` | OK |
| `ObserverFloorTests.test_the_summary_observer_definition_is_the_ruled_sentence_plus_the_sibling_fact` (new) | F7 | string equals the registration's ruled sentence + suffix | `AssertionError: 'SELF + reaped CHILDREN, including collector, rec[39 chars]cted' != 'SELF + all reaped CHILDREN, …'` | OK |
| `EvidenceRegistrationTests.test_the_gate_share_equals_the_registrations_t0_share` (new) | F8 | drift guard: both are 0.5 today | passes on pre-fix (drift guard, not defect-shaped) | OK |
| `StartDriftCadenceTests.test_regression_2_frozen_protocol_takes_v3_and_refuses_v1_and_v2` (changed) | F9 comment, F13 | v2 and v3 bytes must equal their canonical serialisation | `AssertionError: b'{\n[1151 chars]    "statistic": …' != b'{\n[1151 chars]    "abort_after_consecutive": 2, …'` | OK |
| `tests.test_arm_retry` (unchanged; pins the three table copies) | F10 | three copies byte-identical | n/a (text change; module passes) | OK (33) |
| `LifecycleTests.test_the_arm_check_spends_the_predicate_only_on_an_evidence_chain` (new) | F12(b), F12(a) guard | calibration chain must not call the observer; evidence chain calls it once; no observer → `ProductionSamplerInvoked` | `AssertionError: Lists differ: ['observed'] != []` | OK |
| `LifecycleTests.test_an_unreadable_payload_kind_fails_the_arm_check_closed` (new) | F12(b) | ambiguous chain (two declarations) | `AssertionError: Refused not raised` | OK |
| `ProductionSamplerGuardTests.test_the_production_sampler_is_never_reached_from_this_module` (new) | F12(a) | default observer path must raise inside the module | passes on pre-fix modules (the guard lives in the test module itself) | OK |
| `EvidenceRegistrationTests.test_a_busy_non_observer_process_refuses_at_t0_and_at_the_arm_check` (changed) | F14 | C3 PASS detail names the predicate on both branches | `AssertionError: 'agen[15 chars]play, load, and thermal predicates passed' != '…, thermal and non-observer process predicates passed'` (and the non-legacy twin) | OK |
| `…test_the_non_observer_predicate_is_spent_only_on_an_evidence_night` (changed) | F14 | calibration receipt keeps the historical text | passes on pre-fix (guard) | OK |
| `ObserverFloorTests.test_the_unmarked_archives_refuse_under_v3_rather_than_blame_the_sampler` (renamed from `test_the_contaminated_night_loses_every_envelope_under_v3`) | F16 | both unmarked archives under v3 | `AssertionError: ValueError not raised` (×2) | OK |
| `ObserverFloorTests.test_a_marked_journal_is_summarised_and_an_unmarked_one_refuses` (new) | F16 counterfactual pair | same rows marked (12 fseventsd exclusions) / every mark cleared (refusal) / no consumers (neither) | `AssertionError: ValueError not raised` | OK |

The magistrate's own bench finding behind F12(a): at 16900e3d, eighteen
LifecycleTests `check()` calls carried no observer, so each spent the real
`top -l 2 -s 30` sampler; the magistrate's four-module run passed 40 minutes
and was stopped. After F12, `tests.test_evidence_night` alone ran 109 tests
in 305 s with no sampler child process, and the four modules together ran in
4 min 14 s (below).

## 5. Executed results at 2ff07212

Four modules (`python3 -B -m unittest tests.test_quiet_predicate_campaign tests.test_night_gate tests.test_evidence_night tests.test_arm_retry`), tail:

```
Ran 374 tests in 253.710s

OK
python3 -B -m unittest tests.test_quiet_predicate_campaign     128.35s user 117.78s system 96% cpu 4:14.02 total
```

Neighbouring modules that import the registration, gate or generator
(`tests.test_gen_evidence_night tests.test_evidence_arm_sequence tests.test_night_agent_install`),
run as an extra check: `Ran 89 tests in 651.821s` / `OK`. None of them calls
the arm check; their run time comes from their own installer and generator
subprocess fixtures.

Diagnostic re-analysis (`python3 -B diagnostic_reanalysis.py`), diffed against the committed JSON:

```
DIAGNOSTIC OUTPUT IDENTICAL to committed docs/process_traces/2026-09-22-activation-a022aecc/05-nonobserver-predicate-seat/diagnostic_reanalysis.json
```

That output is ruling 10 §4's labelled diagnostic: night 20260922-2100, twelve
exclusions each naming `fseventsd` (574.7–605.8 core-seconds), envelope 1 also
naming `mediaanalysisd` (528.1); night 20260922-0217, zero exclusions (largest
6.3 core-seconds). It states its observer set explicitly (the seven basenames
of ruling 10 §4) because neither archived journal carries observer marks.

Archive re-derivation (`tests.test_quiet_predicate_campaign.archive_summary` into /tmp):

```
20260922-0217 (v2 retention rules): status=REPLAY_NEVER_EVIDENCE observer_floor_cores=0.17572 observer_floor_including_load_recorder_cores=0.18297 observer_variation_cores=0.00214 stop=null
20260922-0217 (v3): ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed
20260922-2100 (v2 retention rules): status=SPREAD_RECORDED observer_floor_cores=0.15909 observer_floor_including_load_recorder_cores=0.16624 observer_variation_cores=0.00267 stop=["sized_pairs_above_24", "observer_floor_above_smallest_holdable_share"]
20260922-2100 (v3): ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed
```

For 0217 the summary's `block_two_stop` is null because today's bench-replay
guard blanks that archive (it predates `power.recorder_kind`); the stop branch
called directly on its floor gives `{'outcome': 'no cutoff qualifies', 'causes': ['observer_floor_above_smallest_holdable_share'], 'pairs': None}`.
**0217's energies (joules, pair SD, s_upper) are not verifiable by this
route**; only 2100's are compared byte for byte with its archive.

## 6. Deviations (for the magistrate to ratify in the PR body)

1. **Three files edited outside brief 04's exhaustive scope** by the original
   seat: `joulewise/arm_retry.py`, `tests/test_arm_retry.py`,
   `docs/phase_2/derivation_night_runbook.md`. Justification (Fable lens S2):
   mechanically forced — the ruled abort reason must be a registered driver
   code (`NIGHT_DRIVER_REASON_CODES`), `tests/test_arm_retry.py` requires
   `COLD_GATE_CODES` = gate codes ∪ driver codes and pins the table text in both
   documents, and the ruling forbids the alternative (a generic
   `night_probe_error`). The seat should have returned NEEDS_SCOPE instead.
   This round's WRITE_SCOPE includes all three.
2. **`observer_floor.supersedes` says 0.176 / 0.159, not ruling 31's 0.178 /
   0.161.** Justification (Fable lens S3): ruling 31 is internally
   inconsistent — 0.178 / 0.161 are its §1 "Σ whole ÷ round support" figures, a
   denominator its own §3 rules wrong; its ruled statistic (whole ÷ span) gives
   0.17572 / 0.15909, and its archived-summary addendum text, brief 04 item
   6(c) and the magistrate's landed addenda (90c30e4f) all say 0.176 / 0.159.
3. **`non_observer_process_busy.bar_basis` reads ~7.7 J at 0.3194 W**, not
   ruling 10's ~7.5 J at 0.3125 W. Justification (Fable lens S4): synthesis 25
   withdrew the 0.3125 W figure "everywhere" in favour of exhibit C8's
   0.3194 W, and brief 04 says a synthesis governs where it amends a ruling;
   0.05 × 480 s × 0.3194 W = 7.67 J. The replacement sentence's wording is the
   seat's.
4. This round, beyond the letter of an item: (a) F7 also corrected the README's
   older sentence that placed the recorder inside the observer cost, since it
   stated the same S1 error; (b) F12(b) reads the payload kind from the sealed
   custody `chain.zsh` rather than from `prepare.json`, because
   `candidate_state` forces every candidate's `state.kind` to
   `quiet_predicate_evidence` — the chain text is the only place a candidate
   can differ, and it is what the t0 gate reads; (c) F16 renamed
   `test_the_contaminated_night_loses_every_envelope_under_v3`, whose name no
   longer describes what it asserts.

## 7. Open questions

- **Opus N9** — regression 0 is proven in three pieces (ancestry marking,
  `record_covariates` forwarding, the executor's argv); no single test runs
  recorder → `sample_interval` → marking over a chain-shaped process table.
- **Opus N10** — (a) on a bind-loop plan carrying an evidence payload,
  `evaluate_dynamic_hard` would spend 30 s per hard phase; bind-deadline
  interaction unverified. (b) The executor reads the journal when an envelope
  ends and the summary at night's end, so a late recorder row could make them
  disagree; F2 now records that as `non_observer_verdict_disagreement: true`
  rather than hiding it, but nothing acts on the flag.
- **F16 in the chain**: the evidence-quality guard lives in `pilot_summary`
  only. If marking failed in production, the executor's in-chain verdict (which
  does not run the guard) would still exclude envelopes 1 and 2 naming
  `powermetrics` and abort with reason `non_observer_process_busy`; the final
  summary would then refuse with the real cause ("pilot summary failed: …
  ancestry marking failed"). Whether the in-chain verdict should carry the same
  guard is not decided here.
- **The ruled `definition` sentence** still says "including … load recorder";
  per the magistrate's ruling it is left as ruled and held for the block-two
  consult. The summary's `observer_definition` and `observer_floor_components_role`
  state the sibling fact beside it.

## Fix round 2

Written by the fix-round-2 seat (Opus 5.5, 2026-09-23), branch
`feat/2026-09-23-qpe01-v3-round2`, linked worktree `JouleWise-wt-v3r2-7a0f14bd`,
starting from 0e5578fb (the head the delta re-audit reviewed). The items are the
delta re-audit's D1, D2, D3 and N-b
(`/Users/edr/.claude/jobs/7a0f14bd/tmp/lens-opus-delta-round1.md`). Files
touched: `joulewise/quiet_predicate_campaign.py`, `joulewise/evidence_night.py`,
`tests/test_quiet_predicate_campaign.py`, `tests/test_evidence_night.py` and
this file; nothing else.

Two words used below: a **mutation** is a deliberate re-break of the code,
applied only in a throwaway copy, to see whether a test notices; the test
**kills** it if it fails. The **in-chain verdict** is the executor's
per-envelope decision taken while the night runs; the **summary** is
`pilot_summary`, re-derived from disk afterwards.

| Item | Commit | What changed |
|---|---|---|
| R1 (D1) | 0fd965fe | The in-chain verdict runs `require_observer_marked` on the envelope's joined journal rows BEFORE `non_observer_busy`. A journal whose consumers carry no observer mark now raises a plain `ValueError` ("recorder journal carries no observer-marked consumer; ancestry marking failed"), so the refusal document's reason is `night_probe_error`, never `non_observer_process_busy`. |
| R2 (D2) | 1226e8d9 | New test `ObserverFloorTests.test_ruling_10_regression_1_on_marked_copies_of_both_archived_journals`: ruling 10 §5 regression 1 on both archived nights through production `pilot_summary` under v3, with consumers whose command basename is in {powermetrics, Python, top, sudo, ps, pgrep, sysctl} marked in a /tmp copy of each journal (ruling 10 §4's explicit diagnostic assumption, standing in for the ancestry marks the archives lack). `archive_summary` gained the optional basename argument. |
| R3 (D3) | fac33045 | New test `ObserverFloorTests.test_the_companion_above_the_smallest_share_is_never_a_stop_cause`: whole 29.9 s and load recorder 0.5 s per 600 s envelope, so the ruled floor (0.04983 cores) is below the 0.05-core `smallest_holdable_share` and the reported companion (0.05067) is above it; `block_two_stop` must carry no `observer_floor_above_smallest_holdable_share` cause. |
| R4 (N-b) | 308f24ac | `evidence_night.check` builds one list of failing checks with the same test that decides `passed`, and the generic refusal text lists only that list, so a `machine_quiet: skipped` row is never named as failed. |

### Counterfactual evidence

**R1.** The new test `NonObserverAbortTests.test_a_marking_failure_in_chain_is_a_probe_error_never_a_busy_daemon`
takes the regression-3 journal (fseventsd at 6 busy cores in envelopes 01 and
02 of the six-second scaled protocol) with every `observer` mark cleared. It
asserts: `refusal.json` reason `night_probe_error`; the refusal detail and the
outcome error carry the marking-failure text; the detail does not name
`NonObserverAbort`; no envelope row, executor or summary, names `fseventsd` as
an offender; the chain stops at `envelope-01`. Its second half is the
counterfactual pair: the same journal WITH the power sampler marked still
aborts with reason `non_observer_process_busy` naming "fseventsd pid 341 36.0
core-s (bar 30)".

Run at 0e5578fb (test added, production code not yet changed):
```
AssertionError: 'non_observer_process_busy' != 'night_probe_error'
Ran 1 test in 0.472s
FAILED (failures=1)
```
After the change, the same scenario (probe through the test harness):
```
PROBE rc 2 summary present True envelope rows 0
PROBE refusal night_probe_error | evidence chain refused: ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed
PROBE outcome error ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed
```
The test harness (`FrozenExecutorTests.exercise`) now returns `summary = None`
when a night writes no `summary.json`, so a night whose summary itself refused
fails on the refusal assertion rather than on a missing file.

**R2.** Output of production `pilot_summary` under v3 on the marked /tmp
copies (the numbers the test pins):
```
2100 INCONCLUSIVE retained 0
  1 ['non_observer_process_busy'] [('fseventsd', 575.6), ('mediaanalysisd', 528.1)]
  2..12 ['non_observer_process_busy'] fseventsd only, 544.7 .. 575.5 core-s
0217 REPLAY_NEVER_EVIDENCE; non_observer_process_busy on 0 of 12 envelopes
```
The test asserts each night's status (21:00 `INCONCLUSIVE`, 02:17
`REPLAY_NEVER_EVIDENCE`) so neither half can pass vacuously, keeping fix round
1's F15 guard-status assertions (unchanged in
`test_both_archived_nights_re_derive_to_the_corrected_floor`). It is skipped by
name ("the 2026-09-22 harvest archives are not on this machine") when either
archive is absent. Mutation probes, each patched in for one run of this test
only:
```
PROBE rule excludes nothing -> KILLED (status no longer INCONCLUSIVE)
PROBE observer mark ignored (every consumer counted) -> KILLED AssertionError: {'powermetrics'} is not false
```

**R3.** Mutation M9 (the delta re-audit's: the companion fed to `stop_branch`
at `quiet_predicate_campaign.py:1343`) applied in a scratch copy of HEAD at
`/tmp/r2-7a0f14bd-m9`:
```
1343:    stop = stop_branch(s_upper=s_upper, observer_floor=observer_floor_including_load_recorder, protocol=protocol)
AssertionError: 'observer_floor_above_smallest_holdable_share' unexpectedly found in ['observer_floor_above_smallest_holdable_share']
Ran 2 tests in 0.167s
FAILED (failures=1)
```
The failure is the new test's; the older sibling test still passes under M9,
as the delta re-audit found. The new test also asserts that its fixture
straddles the share (floor below 0.05, companion above), so it cannot become
vacuous by a fixture edit.

**R4.** New test `LifecycleTests.test_the_generic_refusal_names_only_failed_checks_never_a_skipped_one`:
courier absent from PATH, chain not an evidence night. Run at 0e5578fb (test
added, production code not yet changed):
```
AssertionError: False is not true : pre-arm checks failed: courier, machine_quiet; see /private/tmp/lifecycle-…/lifecycle/check.json
Ran 1 test in 1.422s
FAILED (failures=1)
```
After: the text reads "pre-arm checks failed: courier; see …".

### Deviations and observations

1. **R4 wording.** The brief asks for the text to list checks whose verdict is
   "fail". The code lists the checks that fail the same test `passed` uses
   (verdict "pass", or `machine_quiet` "skipped"). The check vocabulary today
   is exactly pass / fail / skipped, and only `machine_quiet` is ever skipped,
   so the two lists are identical now; the shared test also guarantees that
   any future verdict that blocks arming is named rather than producing an
   empty list.
2. **R1 envelope row.** The guard raises before envelope 01's row is appended
   to `evidence_envelopes.jsonl`, so on a marking failure that journal is
   empty (the envelope directory and its session remain). Nothing is admitted
   either way; the refusal document and the outcome error both carry the
   cause. Recorded so a reader of that file on such a night is not surprised.
3. The seat report's §7 open question "F16 in the chain" is closed by R1.

### Test tail

```
$ python3 -B -m unittest tests.test_quiet_predicate_campaign tests.test_evidence_night
...
evidence_end outcome=complete cleanup_proven=True network_time_restored=True
...............................................................................................................
----------------------------------------------------------------------
Ran 265 tests in 315.778s

OK
```
No test was skipped: both harvest archives are on this machine.
