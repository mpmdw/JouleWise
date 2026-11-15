# Cold review: R1 follow-up rehearsal night kit (2026-11-11)

Reviewer: Opus 5.5, cold seat (the research lead, Fable, unavailable). Target `origin/ops/2026-11-11-r1-followup-kit`
@ `bcd1a03cc` (round 1 `a85ee8ec6`, round 2 ending `555e06cc9`). Reviewed against RL-59, 61, 62, 64, 72, 73, 74, 75,
76, 78 and 79 (read verbatim at `origin/audit/2026-11-10-fable`) and the adopted plan
(`origin/design/2026-11-11-r1-followup`). Anything that needs a new ruling is parked below, not decided.

**Blinding.** Code, the rehearsal design, the rulings and synthetic tests only. No v4, Block 6 or BYTES output,
custody, night-*, archive or restricted path was opened; no SSH. The protocol was read only at WP14(a) lines
227-231. Worktree `jw-wt/rev-kit` (mutants in `jw-wt/rev-kit/.mut`), `TMPDIR` on `/Volumes/JW-EXT`, every test
under `nice -n 10`, the host-command guard from `ops/2026-11-11-w1-presign` (`tests/__init__.py`,
`tests/host_command_guard.py`, `tests/_host_guard_site/`) overlaid uncommitted for every run.

## Verdict: ADMIT-WITH-FIXES

The science-bearing behaviour matches the rulings. `thermal_gates.py` and the registered classifier are
byte-identical to `b4a6c217f`. The WP14(a)-R1-SLOW row is RL-78's text exactly. The selection is made once,
the fallback is RL-78 E2's rule, and the night confirms rather than re-ranks. Recorded keys reach no gate.
The timeout run is restricted to the step kinds. The window is 126,480 s. No kit test reaches a real host
command. Under the default, the `workload.py` edit is byte-identical apart from process RSS. I checked this
independently, including the G0-timeout path.

The fixes are to tests and wiring, and none changes a ruled quantity. Four are needed before the native smoke:

- the RL-72 E3 witness fails on this host (F-1);
- the coverage bar and the night's confirm-not-rerank wiring are not held by any test (F-2, F-3);
- the Part B wall cap is likely too short natively (F-4).

One further fix comes before the W1 line takes the kit: the committed v4 kit was not regenerated after
`align_v4_kit.py` changed (F-11).

Fixes that change executed bytes (F-4, and F-6 if it is done in the driver) need a delta review before the
native smoke.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | `thermal_gates.py` identical to W1 line `b4a6c217f` | PASS (also equal to `82c14c9ea`, `bcc051881`). Classifier `smc_enumeration.py` unchanged too. R1-only behaviour enters through session hooks set by the R1 factory (`g0_timeout_hook`, reference install, smoke stop); nothing forks the gate |
| 1 | Condition-13 test, seven files | PASS with gap. `R1_EXECUTED_SOURCES` = driver, `r1_runtime.py`, `thermal_gates.py`, `r1_runtime.json`, `r1_phase_table.py`, `workload.py`, `thermal.py`. The test mutates each file, a missing commit and a missing phase module. It iterates the tuple instead of pinning it (F-5). Called by `require_registration`, production driver startup, `smoke` and `prepare`. The earlier signing gate F-1 (not this review's F-1) closes once F-5 is fixed |
| 2 | Timeout runs flagged only for step kinds | PASS. `TIMEOUT_RUN_KINDS` = step-30b, step-d, the three legs and the planning turns. Gated D and X-G use the plain reference hook with no callback, so W1's stop applies |
| 2 | Default bundle byte-identical | Production PASS, test FAIL (F-1). My old-vs-new adapter comparison differs only in `memory_snapshots[*].process_rss_bytes`, for a released member and for a G0-timeout member with no callback |
| 3 | `record_keys` absent: journal identical | PASS (`test_absent_field_matches_old_journal_bytes`). `keys()` deduplication cannot change the absent case, because `s_fast != s_slow` is enforced and fans are F-keys |
| 3 | No gate reads a recorded key | PASS. The gate reads `policy['sensors']['s_fast'/'s_slow']` per key. The detector test killed both a policy mutant and a temporary gate-module mutant (M2a, M2b) |
| 3 | Tf08 recorded for every R1 member | PASS. Every step, leg, planning, gated and X-G policy carries `sensors_policy(config)`, which includes `record_keys`. The predecessor gets a sidecar-only policy (parked P-1). The W1 side is not wired (P-2) |
| 3 | Desk prints Tf08 excess | PASS. `night_desk` reports the start excess over step-D's pre-warmup Tf08 median, by condition, plus the pairwise within-window comparisons. Temperatures and config condition only |
| 4 | Classifier unchanged; one pick at Part B | PASS. `select_smoke_sensors` uses the registered picks. The fallback applies only when the slow pick is null and the heatsink class is empty: longest `t_band_s` ≤ 300 s, R0-classified, degC, unclamped, not above junction, not heat-order-excluded, resolving, noise ≤ 0.15, not the fast pick or its alias, no lower τ bound |
| 4 | Night confirms, never re-ranks | PASS by reading. `thermometry()` confirms the configured pair. The summary reports the confirmed pair and keeps `registered_picks` as a disclosure. The kit accepts the fixed pair only with `night_confirmation.ok`. The wiring is untested (F-3) |
| 4 | No hand substitution | PASS. `validate_sensor_ruling` re-derives the selection from the smoke table and requires config = table selection = re-derivation. The table's R0 key set must equal the config's. The ruling binds the table's SHA-256 |
| 5 | Sampler out of process | PASS. A `spawn` child owns the reader and ticker in production. The test holds the GIL in the parent with a `PyDLL` `usleep` across four labelled phases, which is a real starvation test. Coverage is checked on pre_warmup_idle, quiet, load and recovery. The bar itself is not mutation-held (F-2) |
| 6 | E2 window | PASS. Subtotal 58,711.9616 s, largest unit 7,563.9952 s, floor 99,768 s, span 108,768 s, `window_max_s` 126,480 s. Prepare refuses on any other value, and PREQUAL requires an installed R1 plan to have ≥126,480 s and span ≥108,768 s. The test compares the prepare packet with the computation. It does not compare an installed NightPlan; the plan is lead-built, so PREQUAL's ≥ check is the backstop |
| 6 | E4 bars | PASS. Each leg's release is checked against every other leg's capture plus band, on both roles. The G0 band is one-sided, as in `thermal_gates` line 576. B's slow capture must lie within [min(A1,A2) − 0.5, max + 0.5]. A failure of either is inconclusive |
| 6 | E5 default band, 1,200 s cap | PASS. `bands()` refuses a floor ≠ 1.0 and uses max(1.0, 3 × soak SD). `g0_timeout_s` is 1,200 for every model member |
| 7 | RL-62/73 at prepare | PASS with gap. Both public preflights run first, before the sensor ruling, source identity and anything else. They refuse on `ok` false, write a REFUSED record, and are recorded in the arm-input packet. Nothing requires that packet at arm or at driver startup (F-6) |
| 7 | Armcheck version | The kit took `bcc051881` (merge `71e970c13`). Its `align_v4_session.py` is byte-identical to `bcc051881`. Both preflight functions equal the armcheck head (`f9d48635c`). The head also changes `held_window_check` (RL-79) and `main`, and carries test fix `f9d48635c`. The kit has neither (F-7) |
| 8 | WP14(a)-R1-SLOW | PASS. Byte-equal to RL-78's quoted text after removing the quote markers |
| 8 | Workload row (R1-FOLLOWUP-TIMEOUT) | PASS against RL-72 E3/E7: names the callback, its step kinds, the inert default, and gated D/X-G keeping W1's stop |
| 8 | thermal.py row (R1-RECORD-KEYS) | PASS against RL-78 E3. The R1-PHASE-TABLE row's condition-13 sentence still omits `thermal.py` (F-8) |
| 9 | Tests | See below. One kit-test failure (F-1); first-group failure reproduced and attributed (F-7) |
| 9 | Host-command guard | PASS. No refusal recorded in any run. The kit tests contain no `sudo`/`pmset`/`launchctl`/`caffeinate` call |

### Test runs (Python 3.13, guard installed, serial, nice 10)

At `bcd1a03cc`:

| Module | Result |
|---|---|
| `tests.align.test_r1_followup` | 12 tests, **1 failure**: `DefaultBundleTests`, `metadata.json` `process_rss_bytes` (F-1) |
| `tests.align.test_r1_round2` | 14 tests OK |
| `tests.align.test_v4_registration` | 23 tests OK (includes `R1ExecutedSourceTests`) |
| `tests.align.test_v4_executed_closure` | 6 tests OK |
| `tests.align.test_v4_dynamic_closure` | 10 tests OK |
| `tests.align.test_v4_series` | 16 tests, **15 errors** |
| `tests.align.test_v4_series_e2e` | 10 tests, **4 errors** |
| `tests.align.test_v4_series_r20` | OK |
| `tests.align.test_v4_replacement_windows` | 20 tests OK |

With test-only commit `f9d48635c` applied uncommitted to the working tree:

| Module | Result |
|---|---|
| `tests.align.test_v4_series` | 16 tests OK |
| `tests.align.test_v4_series_e2e` | 10 tests OK |
| `tests.align.test_r1_rehearsal` | 76 tests OK |
| `tests.align.test_r1_inventory` | 14 tests OK |
| `tests.test_align_r1_thermal_replay` | 19 tests OK |
| `tests.align.test_v4_kit` | 116 tests, **7 failures, 10 errors** |
| `tests.align.test_thermal_gate` | 44 tests OK. Run at `bcd1a03cc` in `.mut`, without `f9d48635c` |
| `tests.align.test_r1_runtime_contract` | 11 tests, **2 failures**. Run at `bcd1a03cc` in `.mut`. Both are kit-caused (F-13) |
| `tests.align.test_thermal_sidecar` | 9 tests, **2 failures**. Run at `bcd1a03cc` in `.mut`. `test_measurement_core_matches_pre_pr_bytes` fails for `b5/driver.py` and `b5/harvest.py`. The kit changed neither file nor this test relative to `82c14c9ea`; the test is also identical to the armcheck head. Inherited from the W1 line's pins, not the kit |
| `tests.align.test_v4_next_arm_packet` | Interrupted after 23 min with no failure so far (37 tests passed). Not completed |
| `tests.align.test_w1_prequal` | Interrupted after 21 min in its git tamper matrix, under load average about 50, with no failure printed. Not completed. The kit edited `w1_prequal.py`, so this module is owed |

**`test_v4_kit` attribution.** I ran the module at `bcc051881` in `.mut`. Eleven of the failures fail there as
well, so they are inherited armcheck fixture debt: `KeyError: 'plan_path'` (×7) and `held_window: Git evidence
unavailable` (×4). The armcheck head repaired them with `a501ba701`/`510ac023a` and the held-window acceptance
stand-in.

Six fail only on the kit:

- Five come from **"generated v4 kit drifted: configs/campaigns/align_v4/plan_tree.json"**. The kit edited
  `scripts/align_v4_kit.py` and did not regenerate the committed kit, and `plan_tree.json` records the
  generator's SHA-256 (`9d858085…`) (F-11).
- One is `test_an_inconclusive_designed_state_refuses_w1`. It still expects the old `INCONCLUSIVE (R6-2)` text,
  which the kit replaced with `INCONCLUSIVE (RL-72)`; this is a stale expectation (F-12).

**Full-profile first-group failure: reproduced and attributed.** The `dct_series_window` scenario fails with
`TypeError: FakeArmHost.__call__() got an unexpected keyword argument 'check'` from `_watchdog_post_install` at
`scripts/align_v4_session.py:1798`. After that error, the C windows cascade into `triage does not arm the next
frozen window (C1)`.

The post-install watchdog check came in with the armcheck revision `bcc051881` that the kit merged. The witness
fixtures were repaired afterwards, in test-only commit `f9d48635c` (armcheck) / `82453785b` (presign): a
span-aware watchdog fixture and a staged plan for the e2e prepare. The kit did not take that commit. The failure
is inherited, not caused by the kit. With `f9d48635c` applied, `test_v4_series` passes 16/16 (see the run table).
The 850 s timeout of the full profile was not re-run here.

## Mutants

All were run in `.mut`, one at a time, then reverted. "Killed" counts only a failure from a relevant test. The
flaky RSS test (F-1) is excluded from the runs below, because in the first pass it "killed" every M4 mutant for
the wrong reason.

| Mutant | Target | Result | Killed by |
|---|---|---|---|
| M1a | `sensor_admissibility` checks the night's own picks (re-rank) | **KILLED** | `test_night_confirms_admissibility_and_never_reranks` |
| M1b | `Segment.thermometry` confirms the night's registered picks instead of the configured pair | **SURVIVED** | none (101 tests: round2, followup, rehearsal). F-3 |
| M1c | step summary reports the registered picks instead of the confirmed pair | **SURVIVED** | none. F-3 |
| M7 | confirmation drops the alias check | **KILLED** | `test_fallback_rejects_alias_..._coverage` |
| M5 | fallback regains a τ > 60 s floor | **KILLED** | `test_registered_pair_and_fallback_longest_return_without_tau_floor` |
| M2a | a recorded key supplies the slow gate role | **KILLED** | `test_recorded_key_is_journalled_but_no_gate_reads_it` |
| M2b | gate module reads Tf08 (temporary edit of `thermal_gates.py`; checks that the detector works) | **KILLED** | same |
| M3a | gated D and X-G added to `TIMEOUT_RUN_KINDS` | **KILLED** | `PolicyTests` disjointness assertion (static) |
| M3b | reference hook installs the timeout callback for every kind | **SURVIVED** | none. F-3 |
| M3c | `workload.py` dispatches a timeout with no hook | **KILLED** | `DispatchTests` (enabled=False) |
| M4a | coverage bar 99% → 50% | **SURVIVED** | none. F-2 |
| M4b | consecutive-empty test dropped | **SURVIVED** | none. F-2 |
| M4c | read-error test dropped | **SURVIVED** | none. F-2 |
| M4d | pre-warmup idle phase dropped from the smoke table | **SURVIVED** | none. F-2 |
| M6 | `workload.py` dropped from `R1_EXECUTED_SOURCES` | **SURVIVED** | none. F-5 |

Of the four refusals in the brief, three are held only at the helper level:

- **confirm-not-rerank:** held at the helper; the runtime wiring is not.
- **`record_keys` does not gate:** held. Both mutants are killed.
- **timeout-run step-kind restriction:** held statically and in `workload.py`; the hook wiring (M3b) is not.
- **coverage bar:** not held.

## Findings

**F-1 (MEDIUM, test fix; before native smoke).** `DefaultBundleTests`, the witness RL-72 E3 makes a term of
the edit, fails on this host. `metadata.json` and `events.jsonl` carry
`memory_snapshots[*].process_rss_bytes`, which differ between the two in-process adapter runs. Production
behaviour is not affected. My independent comparison found RSS to be the only difference. It also covered the
G0-timeout member with no callback, which is the only path where the edit executes, and which the kit's
witness does not cover (it runs a released member). Fix:

- normalise or patch the RSS field;
- add the timeout-without-callback member to the equality.

**F-2 (MEDIUM, test fix).** The smoke Part B sampler bar is not held by tests. In
`align_r1_followup_kit.phase_coverage`, lowering 99% to 50%, dropping the read-error test, dropping the
consecutive-empty test, and dropping the pre-warmup idle phase from `smoke_table` all survive (M4a-d). Fix: add
negative cases on `phase_coverage` for 98% cells, a 1% read-error fraction and two consecutive empty cells.
Assert that `smoke_table` emits exactly the four RL-76 phases.

**F-3 (MEDIUM, test fix).** The night's confirm-not-rerank rule is held only at the helper and the kit. If the
runtime wiring in `Segment.thermometry` is changed to confirm the night's own registered picks, the mutant
survives (M1b). Swapping the summary's reported pair for the registered picks gives the result in M1c. Fix: add
a `Segment.thermometry` (or step-d) test where the night's registered ranking differs from the configured pair.
Assert that the confirmation and summary name the configured pair. Assert that an inadmissible configured pair
yields `r1.sensor_inadmissible` and a desk refusal.

Gated D and X-G keep W1's stop because the reference hook checks `segment.kind in TIMEOUT_RUN_KINDS`. Removing
that guard survives as well (M3b). Add a test that runs a gated D member and an X-G member through
`Segment.reference_hook` with a G0 timeout, and asserts no turn and no `r1.g0_timeout_run`.

**F-4 (MEDIUM, executed-byte fix or ruling; before native smoke).** After G0 release, smoke Part B arms a
hard `SIGALRM` of 1,200 s (`r1_runtime.py`, `setitimer(..., 1200 if part B)`). That 1,200 s must cover:

- the 300 s quiet;
- one full D turn, which the runtime bounds with a re-armed 1,580 s deadman;
- the 600 s recovery;
- the classification.

The 1,200 s comes from the design's estimate ("about 20 more minutes", D7) and RL-72 E5's "Part B is twenty
minutes". It is not a ruled cap; the ruled 1,200 s is the G0 cap. Any D turn longer than about 300 s makes a good
Part B fail as "partial smoke is not a pass", and the synthetic clock cannot show this. Fix: bound Part B by the
member's own bounds (re-armed deadman + 600 s recovery + a close margin). This is still finite. Otherwise the lead
rules that twenty minutes is a hard bound (P-5). The fix changes executed bytes, so it needs a delta review before
the smoke.

**F-5 (LOW, test fix).** `R1ExecutedSourceTests` iterates `reg.R1_EXECUTED_SOURCES`, so removing a file from
the tuple survives (M6). Only `thermal.py` membership is asserted elsewhere. Fix: pin the literal seven-path set.

**F-6 (MEDIUM, wiring).** The RL-62/73 results live in the kit's `FOR_LEAD_ARM` packet. Neither the R1 arm nor
the non-synthetic driver startup requires that packet, checks its `executed_commit`, or carries its path and
SHA-256 into the arm record. The link is procedural. RL-79's rule for held-window releases is that a release
existing only on the measurement Mac is not a record. The same reasoning applies here. Fix: the driver refuses
unless it is given a packet with `status: FOR_LEAD_ARM`, matching `executed_commit` and both checks `ok`; the arm
record carries the packet's path, SHA-256 and the two results. Until then, the arm checklist names the packet.

**F-7 (INFO, merge hygiene).** The kit's `align_v4_session.py` is the `bcc051881` version. Before the W1 line
takes the kit, merge the armcheck head:

- RL-79's walk-every-final-window `held_window_check` (`7d472758a`);
- harvest holds (`785d94436`);
- test fix `f9d48635c`, which turns the series group green.

The two preflight functions are already identical to the head.

**F-8 (LOW, doc).** The R1-PHASE-TABLE row lists condition 13's files without `thermal.py`. R1-RECORD-KEYS adds
it, and `R1_EXECUTED_SOURCES` has it. Name all seven in one place.

**F-9 (LOW, test gap).** The driver and runtime branch on `args.synthetic` / `backend.name == "production"` for
the S6 record. Production emits `new_sensor_default` with `receipt_transferred: false`; synthetic emits the
`r1_slots.json` S6 = 1.5 "adopted" receipt. So no synthetic test exercises the production S6 record that W1 will
read. Add one that forces the production branch.

**F-11 (HIGH for the W1 line; does not block the R1 smoke).** The committed v4 kit is stale. The kit changed
`scripts/align_v4_kit.py` (`check_r1_evidence`), but `configs/campaigns/align_v4/plan_tree.json` still records
the old generator digest. On this tree, `test_committed_bytes_reproduce_without_reading_models` fails, and so
does every W1 prepare/install witness that runs the kit-regeneration check. W1's arm would refuse "generated v4
kit drifted". Fix:

1. regenerate the kit;
2. commit it;
3. regenerate the closure trace;
4. rerun `test_v4_kit`, `test_v4_executed_closure` and `test_v4_dynamic_closure`.

**F-12 (LOW, test).** `test_an_inconclusive_designed_state_refuses_w1` expects the pre-kit refusal text.
Update the expectation. The behaviour, which is to refuse, is correct and stricter: an inconclusive X-G now
refuses too, where before it was exempt.

**F-13 (LOW, test/doc).** Two `test_r1_runtime_contract` failures come from kit edits:

- `docs/align/r1_runtime_contract.md` does not list the new `capture-predecessor-30b` kind in the form
  `test_contract_doc_lists_every_kind` checks.
- `Round6ContractTests` still asserts that `step-30b` has no INCONCLUSIVE result. RL-72 E3 now lets step-30b time
  out and run, so the kit's addition of step-30b to `G0_INCONCLUSIVE_KINDS` is ruled.

Update the doc and the test. The report listed these modules as owed and did not run them at the final head.

**F-10 (INFO).** The fallback fires only when the registered slow pick is null **and** the heatsink class is
empty. A heatsink-class key that is clamped therefore yields no fallback, and the case holds for the lead. This is
conservative and consistent with "the registered slow class is empty".

## Parked for the research lead

- **P-1. The ordinary 30B predecessor.** RL-72 D1 says "the already-bound 30B template; no configuration
  change". RL-78 says "Tf08 is recorded for every member". To meet the later ruling, the kit derives a
  sidecar-only config from the bound template. That config adds an in-process sensor thread and strips
  `launch_lineage_required`; the other R1 members are non-claim and carry no lineage either. Which ruling governs
  the predecessor?
- **P-2. "In every member" on the W1 side.** The WP14(a)-R1-SLOW row says Tf08 is journalled in every member.
  W1's `inputs.R1.thermal_policy.sensors` has no `record_keys` requirement in `align_v4_kit.py`, and W1's ungated
  30B anchors have no sidecar. Either the W1 kit and templates must carry it before signing, which is a W1 config
  change, or the row's scope needs a ruling.
- **P-3. Scope of the coverage bar.** As built, every degC inventory key must meet ≥99% cells, <1% read errors
  and no two consecutive empty cells in every phase. A single intermittently erroring key that matters to no one
  fails the smoke and blocks the arm. RL-74/76 state the bar for the sampler. Should it be read per key, over all
  keys, or per sweep?
- **P-4. Condition-13 scope.** `joulewise/align/apple/r1_runtime_contract.py`, which the kit edited, and the
  launcher `scripts/align_r1_runtime.py` execute in the night and are bound strict in the receipt. They are not
  among the condition-13 files. RL-61's rationale ("a receipt that lists the rehearsal's code should list the code
  that rehearsed") would cover at least the contract. Should it join?
- **P-5. Part B duration.** If "Part B is twenty minutes" (RL-72 E5) was meant as a hard bound, F-4's fix needs
  that ruling changed. If it was an estimate, F-4 is an engineering fix.

## Native checks still owed

None of these were run here; all are hardware-bound.

1. Smoke Part A, ≤1,800 s, on the final committed bytes. Must show: native pre-warmup R_D capture, W1 verifier
   acceptance, release within 1,200 s, re-arm, no timeout run, host mode readback/restore, clean teardown.
2. Smoke Part B. Must show:
   - the spawned inventory process's readiness within 20 s on the real SMC;
   - its monotonic domain matching the member's;
   - the sampler bar on all four phases;
   - Part B finishing inside its wall cap (F-4).
   The resulting table goes to the lead for the RL-78 check.
3. The real weight and installed-stack preflights with the measurement interpreter.
4. `JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx` on Metal.
5. Off-MBP, after the fixes: complete `tests.align.test_w1_prequal` and `tests.align.test_v4_next_arm_packet`
   runs, then the full-profile dynamic trace (no `--bounded`) on a tree that includes `f9d48635c`, then both closure modules
   again.
6. A repeat of the affected smoke if any fix above changes executed bytes.
