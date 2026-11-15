# Delta cold review: R1 follow-up kit, rounds 3-4 (2026-11-11)

Reviewer: Fable 5.2, cold seat. Target `ops/2026-11-11-r1-followup-kit`, range `bcd1a03cc..3e2559e7c`
(Sol rounds 3 and 4, plus the merges `b0a39479d` and `8c07cf7f8`). Reviewed against the Opus cold review at
`bcd1a03cc` (`docs/run_reports/2026-11-11-r1-followup-kit-coldreview.md`, commit `51b6aeb14`) and RL-72 to RL-84,
read verbatim at `origin/audit/2026-11-10-fable`. No code was changed.

**Blinding.** Code, rulings, review text and synthetic fixtures only. No Block 6, BYTES held-out or v4 sealed
outcome path was opened. No SSH. No sudo, pmset, launchctl or caffeinate; the host-command guard logged no
refusal in any run of mine.

**How it was run.** Worktree `jw-wt/kit-delta-review`, mutants in `jw-wt/kit-delta-review-mut` (both removed
afterwards). `nice -n 10 python3.13 -B`, `TMPDIR=/Volumes/JW-EXT/scratch/kit-review`. The host ran at load average
65 to 75 throughout, so wall times below are not timing evidence. The repository named in the brief
(`~/code/CapstoneProject/JouleWise`) is not a git checkout; the worktrees hang off `jw-wt/handoff`.

## Verdict: ADMIT-WITH-FIXES

The round 3-4 fixes do what the first review asked, with one exception (F-1). All eight mutants that survived
at `bcd1a03cc` are now killed. RL-84's P-1, P-3 (the bars), P-4 and P-5 are installed as ruled, and the two
DEVIATIONS edits match RL-84's quoted text.

The executed-byte changes that RL-84 P-5 sent to delta review are admitted: the Part B post-G0 watchdog
(`r1_runtime.py:113-119`, `:1687-1691`) and the predecessor without a sidecar (`r1_runtime.py:1937-1952`).
**Smoke Part A may run on these bytes.**

Two new findings are HIGH and neither blocks Part A:

- **D-1.** The Part B selection no longer uses the registered classifier's picks unchanged. It re-runs the
  chooser on the six R0-listed keys only. Where the classifier's own pick is a key outside that list, the kit
  now picks a different key without a refusal or a flag; at `bcd1a03cc` it refused and the case went to the
  research lead. RL-84 did not order this. It needs a ruling or a revert before the Part B table is used for
  the sensor ruling.
- **D-2.** The night chain now requires `ALIGN_R1_PREPARE_PACKET`, and an armed night has no way to receive it.
  As built, the armed R1 night refuses in the chain's first line. It must be fixed before the arm.

## Finding by finding

| Finding | Status | Evidence |
|---|---|---|
| F-1 E3 bundle equality fails on RSS | **PARTIAL** | RSS is patched at its source (`tests/align/test_r1_followup.py:240-244`, `:269`) and the G0-timeout-without-callback member is now compared (`:259`). The test still fails on this host: `metadata.json` carries the live `ioreg` battery text, and `UpdateTime`/`Voltage` change between the two adapter runs. It failed in the module run and in at least two of four isolated reruns. See D-3 |
| F-2 coverage-bar mutants survive | **FIXED** | `tests/align/test_r1_round3.py` `CoverageBarTests`, `tests/align/test_r1_round4.py` `PerKeyCoverageTests`. M4a-d and the sweep-bar variants are all killed |
| F-3 night confirms own picks; hook for gated D/X-G | **FIXED** | `test_r1_round3.py` `RuntimeWiringTests`: `Segment.thermometry` with the night's ranking differing from the configured pair, and every gated D kind plus X-G through the real `reference_hook` on a timeout. M1b, M1c and M3b are killed |
| F-4 Part B 1,200 s cap | **FIXED** | `smoke_post_g0_budget` = quiet 300 + re-armed turn bound 1,580 + recovery 600 + close 120 = 2,600 s, installed at `r1_runtime.py:1691` and written to `smoke_part_a.json`. G0 keeps 1,200 s. Still finite. Restoring 1,200 s, or dropping recovery from the sum, is killed |
| F-5 condition-13 test iterates the tuple | **FIXED** | `tests/align/test_v4_registration.py:441-450` pins the literal ten-path set and its length. Dropping `workload.py` or the classifier is killed |
| F-6 nothing requires the prepare packet | **PARTIAL** | Driver side fixed: `require_prepare_packet` (`scripts/align_r1_rehearsal.py:1483-1516`) checks schema, `FOR_LEAD_ARM`, `executed_commit`, both checks `ok is True`, and the ten source hashes; called at `:1658` before the host lock; the arm record carries path, SHA-256 and both results. Four mutants killed. The delivery to the armed chain is broken (D-2) |
| F-7 armcheck base | **FIXED** | Merge `b0a39479d` takes the presign batch at `5df1afbf8`. `7d472758a`, `785d94436` and `82453785b` (presign's copy of `f9d48635c`) are ancestors of the head |
| F-8 R1-PHASE-TABLE omits `thermal.py` | **FIXED** | `docs/align/v4/DEVIATIONS.md:23` carries RL-84's sentence |
| F-9 production S6 branch untested | **FIXED** | `test_production_s6_record_never_transfers_the_tf08_receipt` |
| F-11 `plan_tree.json` stale (HIGH) | **FIXED** | `plan_tree.json:72` records `7a7244d2…`, the SHA-256 of `scripts/align_v4_kit.py` at the head; `identity_pins.json:6` matches the tree's SHA-256. `test_committed_bytes_reproduce_without_reading_models` passes. Both closure modules pass at `3e2559e7c` (orchestrator run) |
| F-12 stale `INCONCLUSIVE (R6-2)` expectation | **FIXED** | `tests/align/test_v4_kit.py:957`; the test passes |
| F-13 contract doc and step-30b expectation | **FIXED** | `docs/align/r1_runtime_contract.md:25-27`; `tests.align.test_r1_runtime_contract` 11 tests OK |
| RL-84 P-1 no predecessor sidecar | **FIXED** | `r1_runtime.py:1937-1952`: the sensors-policy line is gone, the "ordinary unmodified 30B template" refusal stays, the lineage tag is the only derivation and is recorded as `template_derivation` beside `template_sha256`. Re-adding the sidecar is killed |
| RL-84 P-1 row edit | **FIXED** | `DEVIATIONS.md:18` is RL-84's replacement sentence word for word |
| RL-84 P-2 W1 kit carries `record_keys` | **NOT ON THIS BRANCH** | `scripts/align_v4_kit.py` here has no `record_keys` check. The work is on `origin/ops/2026-11-11-w1-tf08-record` (`check_w1_record_keys`), which this review did not cover. On the R1 side, Tf08 is record-only for every sidecar member and the kit refuses a config without it (`align_r1_followup_kit.py:113-114`). Owed before W1 signing, not before the R1 smoke |
| RL-84 P-3 per-key bar | **FIXED for the bars; D-1 for the selection** | `phase_coverage` (`align_r1_followup_kit.py:155-199`): the sweep bar (≥99%, never two missed in a row) fails the smoke; a key's bar rejects that key and lists class, phase and reason (`:254-257`); Tf08 failing or absent fails the smoke (`required_keys`). Smoke saves diagnostics, then refuses (`:314-317`) |
| RL-84 P-4 ten files | **FIXED** | `v4_registration.py:482-489` is exactly RL-84's ten paths. Prepare and the driver both hash all ten |
| RL-84 P-5 twenty minutes is an estimate | **FIXED** | As F-4. This review is the delta review P-5 asked for |

## Smoke Part B: does the classifier pick once, with the fixed fallback, and the night only confirm?

- **Fallback rule: holds.** `select_smoke_sensors` and `sensor_admissibility` (`r1_runtime.py:438-478`) are
  unchanged in the delta. The fallback fires only on an empty slow class, takes the longest `t_band_s` ≤ 300 s,
  and has no lower τ bound.
- **The night confirms and never re-ranks: holds, and is now held by tests.** `Segment.thermometry`
  (`r1_runtime.py:2007-2042`) confirms the configured pair and reports it; the night's own picks
  are kept only as `registered_picks`.
- **No hand substitution: holds.** `validate_sensor_ruling` (`align_r1_followup_kit.py:98-115`) requires
  config = table selection = re-derivation, and the ruling binds the table's SHA-256.
- **"The registered classifier's picks, unchanged": does not hold in one case.** See D-1.

## New findings

**D-1 (HIGH; ruling or revert before the Part B table is used).** `smoke_selection`
(`align_r1_followup_kit.py:202-214`) filters the classifier's ranking to `r0_classified_keys` before it
re-runs `select_keys`, and recomputes `heatsink_candidates` from the filtered rows. RL-84 P-3 orders the
coverage filter. It does not order the R0 filter, and RL-78 puts "R0-classified" on the fallback's candidates
only (E1: "the registered classifier's picks on the D step, unchanged").

`r0_classified_keys` is six keys. The native inventory is much larger. Two cases change behaviour, both
reproduced on synthetic classifier input:

| Case | `bcd1a03cc` | `3e2559e7c` |
|---|---|---|
| The classifier's fast pick on D is a key outside the six | selection not ok; held for the lead | picks the best of the six, `ok`, no flag |
| A key outside the six is heatsink-class on D (the registered slow class is not empty) | selection not ok; held for the lead | treats the class as empty, fires the fallback, `ok` |

The second case contradicts the WP14(a)-R1-SLOW row's condition "where the registered slow class is empty".
The table still prints the unmodified classifier result, so the difference can be seen by comparing
`selection` with `classification_table`, but nothing marks it. Removing the R0 filter survives every test
(mutant N10), so no test states which behaviour is intended. Sol's report says round 4 made no new
research-policy choice; this is one.

Fix, either:

- filter on coverage only, and leave the R0 test in `sensor_admissibility`, which restores the refusal; or
- the research lead rules that the pick is made among the R0-listed keys, the row is edited to say so, and a
  test pins it.

The kit script is not a condition-13 file. The native Part B run does not need to wait: `smoke_table` is a
pure function of the saved segment and can be recomputed after the fix.

**D-2 (HIGH; before the arm, not before the smoke).** `scripts/night_chains/align_r1_rehearsal.zsh:6` exits
unless `ALIGN_R1_PREPARE_PACKET` is set. The chain's environment is built by `_chain_environment`
(`scripts/run_night.py:706-758`) from the night agent's own environment plus a fixed set of keys. The night
agent's plist template sets `PATH` only (`configs/launchd/com.joulewise.night.plist.template`), and
`extra_env` is accepted only for `TRANSACTION_PACK` with two fixed keys (`run_night.py:1103-1106`). The plan
has no field for it. So the variable cannot reach an armed chain, and the R1 night would stop at
`r1.prepare_packet.missing` in its first second. The tests set the variable by hand
(`tests/align/test_r1_rehearsal.py:917`, `:1043`), so they do not see this.

The check also sits above the trap and the startup `restore_automatic` (`:8-27`), so a refusal there skips
the Automatic restore that the chain otherwise always performs, including after a previous SIGKILL.

Fix: give the packet a fixed location the chain derives itself (for example under `$MEASUREMENT_ROOT`, as
`POWER_MARKER` is), keep the driver's refusal, and move the check below the restore. The chain is plan-pinned
and not a condition-13 file. A witness should run the chain with the environment `_chain_environment`
produces.

**D-3 (MEDIUM; test fix, before signing).** F-1's witness is still not deterministic. The bundle's
`metadata.json` embeds the live `ioreg` battery read, so the equality depends on the host's battery not
updating between the two adapter runs (once a minute, and the voltage moves on its own). On this Air it failed
three times in five. Production is unaffected; the only differing fields are host battery state. Fix as for
RSS: patch the battery read at its source, with nothing excluded by parsing. RL-72 E3 makes this witness a
term of the `workload.py` edit, so it should pass reliably before signing.

**D-4 (LOW; disclosure).** The phase accounting loses up to one cell at a phase's leading edge, and counts a
sweep that straddles the end as a read error for every key. This follows the registered `rank()`, and it is
harmless for long phases. I simulated a perfectly healthy 1 Hz sampler against `phase_coverage`:

| Phase length | Sweep bar fails | Tf08 bar fails |
|---|---|---|
| 300 s, 600 s | 0% | 0% |
| 150 s | 0% | 0% |
| 100 s | 0% | 3% to 41%, rising with sweep duration |
| 60 s and under | about 50% | about 50% |

Pre-warmup idle (300 s), quiet (300 s) and recovery (600 s) are safe. The load phase is the D turn, whose
native length I did not look up. If it is under about 150 s, a healthy smoke can fail on Tf08's bar. Sol met
the same effect in the two-cell sampler test and re-anchored the fixture (`test_r1_followup.py:44-50`). Worth
one line to the lead with the expected D-turn length before Part B.

**D-5 (INFO).** The prepare packet has no age bound. The driver proves it names this commit and these ten
files; it does not prove the RL-62/73 checks were run recently. The weights or the installed stack could
change between prepare and the night.

**D-6 (INFO).** `origin/ops/2026-11-11-w1-presign` has moved past the merged `5df1afbf8` (three test and doc
commits). Take them with the next merge.

## Mutants

Run one at a time in `jw-wt/kit-delta-review-mut`, each reverted; the worktree was clean at the end.
"Killed" means a relevant test failed. The flaky bundle test (D-3) was not in any mutant's test set.

| Mutant | At `bcd1a03cc` | At `3e2559e7c` | Killed by |
|---|---|---|---|
| M1b `thermometry` confirms the night's own picks | survived | **KILLED** | `test_night_confirms_and_reports_smoke_pair_and_refuses_inadmissible_pair` |
| M1c summary reports the registered picks | survived | **KILLED** | same |
| M3b reference hook installs the timeout callback for every kind | survived | **KILLED** | `test_gated_d_and_xg_reference_hooks_do_not_dispatch_timed_out_turns` |
| M4a key bar 99% → 50% | survived | **KILLED** | `test_each_bar_independently_refuses_in_every_phase` |
| M4b key consecutive-empty test dropped | survived | **KILLED** | same, and `test_each_key_bar_rejects_only_that_key_in_every_phase` |
| M4c key read-error test dropped | survived | **KILLED** | same two |
| M4d pre-warmup idle phase dropped | survived | **KILLED** | `test_smoke_table_emits_exactly_all_four_rl76_phases` |
| M6 `workload.py` dropped from condition 13 | survived | **KILLED** | `test_condition13_names_exactly_the_ten_ruled_sources` |
| M6b classifier dropped from condition 13 | new | **KILLED** | same |
| M4a2 sweep bar 99% → 50% | new | **KILLED** | `test_sweep_bar_fails_smoke_even_with_no_candidate_keys` |
| M4b2 sweep consecutive-miss test dropped | new | **KILLED** | same |
| N1 Tf08 not required | new | **KILLED** | `test_tf08_failure_or_absence_fails_smoke_with_healthy_sweeps` |
| N2 selection ignores per-key coverage | new | **KILLED** | `test_prewarm_rejection_excludes_registered_and_fallback_roles` |
| N3 predecessor regains the sidecar | new | **KILLED** | `test_ordinary_predecessor_has_no_sidecar_and_only_strips_lineage_tag` |
| N4a packet commit check dropped | new | **KILLED** | `test_requires_matching_commit_and_both_ok_and_records_packet_identity` |
| N4b packet `ok` accepted when merely truthy | new | **KILLED** | same |
| N4c packet source-hash comparison dropped | new | **KILLED** | same |
| N5 Part B timer back to 1,200 s | new | **KILLED** | `test_post_g0_watchdog_fits_realistic_d_turn_and_is_installed` |
| N6 smoke does not refuse on failed coverage | new | **KILLED** | `test_smoke_refuses_failed_bars_or_selection_after_saving_diagnostics` |
| N7 prepare re-derives without the coverage filter | new | **KILLED** | `test_prepare_requires_smoke_pair_coverage_ruling_and_default_band` |
| N8 sweep bar left out of the smoke's pass | new | **KILLED** | `test_sweep_bar_fails_smoke_even_with_no_candidate_keys` |
| N9 driver does not require the packet | new | **KILLED** | `test_production_driver_refuses_before_any_host_command_without_prepare` |
| N10 `smoke_selection` drops the R0 filter | new | **SURVIVED** | none (D-1) |
| N11 post-G0 budget drops recovery | new | **KILLED** | `test_post_g0_watchdog_fits_realistic_d_turn_and_is_installed` |

## Test runs at `3e2559e7c`

Mine:

| Module | Result |
|---|---|
| `tests.align.test_r1_followup` | 12 tests, **1 failure** (`DefaultBundleTests`, D-3) |
| `tests.align.test_r1_round2` | 14 OK |
| `tests.align.test_r1_round3` | 8 OK |
| `tests.align.test_r1_round4` | 8 OK |
| `tests.align.test_v4_registration` | 24 OK |
| `tests.align.test_r1_runtime_contract` | 11 OK |
| `tests.align.test_r1_rehearsal` | 76 OK |
| `tests.align.test_v4_kit`, the F-11 and F-12 tests only | 2 OK |

The orchestrator's, read from `/Volumes/JW-EXT/scratch/kit-verify/results.txt` at 13:42 PST:

| Module | Result |
|---|---|
| `tests.align.test_v4_executed_closure` | OK |
| `tests.align.test_v4_dynamic_closure` | OK |
| `tests.align.test_v4_next_arm_packet` | running; no failure printed so far |
| `tests.align.test_w1_prequal` | not yet reported |
| full-profile dynamic trace | not yet reported |

## Owed before the native smoke

1. Nothing in the delta blocks **Part A** on `3e2559e7c`.
2. Before the **Part B table goes to the lead for the sensor ruling**: D-1 resolved, by revert or by ruling.
   The native Part B run itself can go first; recompute the table from the saved segment afterwards.
3. One line to the lead on D-4 with the expected native D-turn length.
4. The orchestrator's `test_v4_next_arm_packet`, `test_w1_prequal` and full-profile dynamic trace, where not
   yet reported above. The committed trace is still the inherited baseline until the full trace passes and
   is moved into place.

## Owed before the arm

1. D-2: a way for the packet to reach the armed chain, the check moved below the Automatic restore, and a
   witness through `_chain_environment`.
2. D-3: the E3 witness made deterministic.
3. A short delta review of the D-1 and D-2 fixes. Neither touches a condition-13 file, so no smoke repeat
   follows from them.
4. The prepare packet generated on the final commit, with the real weight and installed-stack preflights.

## Owed before W1 signing

- RL-84 P-2 from `ops/2026-11-11-w1-tf08-record`, with its own cold review.
- The night must run the final bytes of all ten condition-13 files; any later edit to one of them repeats
  the affected smoke.

---

# Round 5 delta (2026-11-11, 15:20 PST)

Reviewer: Fable 5.2, cold seat. Range `4c41fe241..e74b64793` (Sol round 5: `52060d393` code and tests,
`f7174e0b7` and `e74b64793` reports). Code changes are four lines in `scripts/align_r1_followup_kit.py` and
eleven in `scripts/night_chains/align_r1_rehearsal.zsh`; the rest is tests and reports. No condition-13 file
changed. No code was changed by this review.

**Blinding and host.** Code, rulings and synthetic fixtures only. No sudo, pmset, launchctl or caffeinate; the
host-command guard log stayed empty. `nice -n 10 python3.13 -B`, `TMPDIR=/Volumes/JW-EXT/scratch/kit-r5-review`,
one module at a time, load average 67 to 89. Worktrees `jw-wt/kit-r5-base`, `kit-r5-head`, `kit-r5-mut`, removed
afterwards. `scripts/test_timings.json` was not touched.

One thing to check: when I restarted my first `test_run_night` run to add `-v`, I stopped it with
`pkill -f "unittest tests.test_run_night"`. That pattern is not limited to my process. If another seat was
running `tests.test_run_night` on the Air at 14:43 PST, I killed it.

## Verdict: ADMIT-WITH-FIXES

D-1, D-2 and D-3 are fixed as ruled, and D-4 is reported. Round 5 introduces no regression in
`test_run_night`, and the dynamic closure passes at `e74b64793`. The Part B table may be computed and sent
to the lead on these bytes. Two residuals on the packet route remain, neither a blocker for the smoke:

- **D-7 (MEDIUM, before the arm).** A packet left at the fixed path by an earlier night is accepted if that
  night ran the same commit. Nothing binds the packet to this plan or to a date.
- **D-8 (LOW, test gap).** No test stops the chain from honouring an inherited `ALIGN_R1_PREPARE_PACKET`.

## Finding by finding

| Finding | Status | Evidence |
|---|---|---|
| D-1 R0 filter on the ranking | **FIXED** | `align_r1_followup_kit.py:211-212` filters on coverage only, which is RL-84 P-3. R0 membership is tested in `sensor_admissibility` (`r1_runtime.py:449`), so it limits the fallback's candidates (RL-78 item 2) and refuses a registered pick outside the six. Both refusals are back and pinned: `test_fast_pick_outside_six_is_held_for_lead_without_substitution` and `test_heatsink_outside_six_refuses_instead_of_falling_back` (`test_r1_round4.py`), using the production six-key list. Both assert no fallback and an unmodified classifier input. Mutant R1 killed by both |
| D-2 packet never reaches the chain | **FIXED, with D-7 and D-8** | See below |
| D-3 volatile ioreg fields in the E3 witness | **FIXED** | The battery read is patched at `battery_float.run_bundle_probe`, the source the controller calls (`controller.py:1692`). The test asserts both probes ran and both records passed, and still compares every byte. 4 of 4 isolated runs passed here, plus the module run; it failed 3 of 5 before |
| D-4 leading-edge loss in phase accounting | **REPORTED** | `2026-11-11-r1-followup-kit.md:768-777` states that the registration gives the D turn a token cap and a 1,580 s deadman, with no minimum duration. The lead still needs the native D-load length from the smoke journal |
| D-5 packet has no age bound | **OPEN, now D-7** | The fixed path makes it matter more |
| D-6 presign branch has moved | not in scope this round | |

## D-2: is the route registered and pinned, and can a stale packet be picked up?

**The route is registered and pinned.** The chain sets
`ALIGN_R1_PREPARE_PACKET="$MEASUREMENT_ROOT/.align-r1-prepare.json"` unconditionally
(`align_r1_rehearsal.zsh:43`), so an inherited value is overwritten. `MEASUREMENT_ROOT` comes from the plan
through `_chain_environment` (`run_night.py:727`), and the chain's bytes are pinned by the plan's SHA-256
sidecar (`run_night.py:5147-5154`). No plist variable, plan field or `extra_env` was added. The check now sits
below the traps, the startup restore and the marker restore (`:17-38`, then `:43-47`).
`ChainEnvironmentTests` builds the environment from the plist template's PATH-only set through the real
`_chain_environment`, runs the real chain, and checks delivery, the refusal, and at least three Automatic
restores in both cases. `run_night` has no clean-tree check on the measurement root, so the untracked dotfile
does not trip admission; it sits beside `.align-r1-high-power`.

**A stale packet: refused across commits, accepted within one.** The driver's `require_prepare_packet`
(`align_r1_rehearsal.py:1483-1516`) is unchanged. It refuses a packet that names another commit or whose ten
source hashes differ (mutants R2f and R2g killed). It checks nothing else about when or for what the packet
was made:

- the packet has no plan id, night id or timestamp, and the driver reads none;
- the chain and the driver never remove or move the file, so it persists after the night;
- the plan does not carry the packet's SHA-256.

So a second arm at the same commit reuses the first night's packet with no refusal. That is the case the
packet exists for: weights or the installed stack changing between prepare and the night (RL-62/73). Two
things limit it. `prepare` opens its output with mode `x`, so a new prepare at that path fails loudly until
the old file is deleted. And the arm record carries the packet's SHA-256. Neither stops an arm that skips
prepare.

**D-7 fix, either:**

- the driver moves the packet into the night's output directory once it has validated it, so each arm needs a
  fresh prepare; or
- the arm step is written as "delete the old packet, run prepare, arm", and the lead checks the packet hash
  in the arm record against the one prepare printed. This needs no code.

The first is a change to `scripts/align_r1_rehearsal.py`, which is a condition-13 file and would repeat the
smoke. If the smoke has already run by then, take the procedural route.

**D-8.** Mutant R2d makes line 43 `${ALIGN_R1_PREPARE_PACKET:-…}`, which lets a desk shell's variable choose
the packet. Every test passes. The shipped code is right; one assertion in `ChainEnvironmentTests` (set the
variable to a decoy path and assert the argv still names the fixed path) would pin it.

## test_run_night: `4c41fe241` against `e74b64793`

318 tests each, run back to back, 487 s and 492 s.

| | `4c41fe241` | `e74b64793` |
|---|---|---|
| Result | 18 failures, 4 errors | 10 failures, 0 errors |
| In both | 8 | 8 |
| Only at this commit | 14 | 2 |

**No round-5 regression.** `scripts/run_night.py` and `tests/test_run_night.py` are byte-identical across the
range, and the module imports neither changed file.

The two that failed only at `e74b64793`, both in `NightProbeTests`:

- `test_probe_success_receipt_binds_every_field_without_capture`
- `test_supervised_probe_success_and_refusal_with_fixture_census` (`mode='ok'`)

I reran the pair in isolation three times at each commit. At `4c41fe241`: 2, 1 and 1 failures. At
`e74b64793`: 1, 1 and 0. They fail at the base too, so they are load-dependent.

The fourteen that failed only at `4c41fe241` are all `BindSupervisionProcessTests` timing cases (4 errors,
10 failures) and passed at the head. The seat's count of 15 failures and 2 errors is the same population
under a different draw.

The eight in both runs:

| Test | Class |
|---|---|
| `test_blocked_journal_never_blocks_deadline_or_grants_go` | `BindSupervisionProcessTests` |
| `test_blocking_join_startup_and_post_publication` | `BindSupervisionProcessTests` |
| `test_header_plus_one_byte_never_blocks_recv` | `BindSupervisionProcessTests` |
| `test_pre_send_local_timeout_and_late_global_expiry` | `BindSupervisionProcessTests` |
| `test_signalled_child_cannot_hold_cleanup_past_budget` | `BindSupervisionProcessTests` |
| `test_startup_hang_is_nonblocking` | `BindSupervisionProcessTests` |
| `test_probe_timeout_kills_reservation_and_descendant` | `NightProbeTests` |
| `test_R8_no_launchd_template_can_carry_the_replay_variable` (magistrate template) | `NightProbeTests` |

Seven are deadline tests on a host at load 70; I did not rerun them on a quiet host, so "load" is my reading
of their messages, not a demonstrated cause. **The eighth is not timing.** The magistrate plist template
carries `MAGISTRATE_WATCHDOG_STATUS_HOST`, which the test's expected key set does not list. It is
deterministic, predates round 5, and concerns the magistrate agent, not the night agent the R1 chain runs
under. It needs an owner.

## Dynamic closure at `e74b64793`

`tests.align.test_v4_dynamic_closure -v`: **10 tests, OK, 74 s**, run alone to completion. The seat's
timeout was its sandbox cap, not the code.

## Other modules at `e74b64793`

| Module | Result |
|---|---|
| `tests.align.test_r1_followup` | 12 OK |
| `tests.align.test_r1_round2` | 14 OK |
| `tests.align.test_r1_round3`, `test_r1_round4`, `test_r1_rehearsal` (one invocation) | 95 OK |
| `tests.align.test_v4_registration` | 24 OK |
| `tests.align.test_r1_runtime_contract` | 11 OK |

Not run by me: `test_v4_executed_closure`, `test_v4_next_arm_packet`, `test_w1_prequal`, the full-profile
dynamic trace.

## Mutants

One at a time in `jw-wt/kit-r5-mut`, each reverted; the worktree was clean at the end.

| Mutant | Result | Killed by |
|---|---|---|
| R1 R0 filter back on the ranking (was N10, survived) | **KILLED** | both new `SelectionAndTableTests` cases |
| R2a chain does not pass `--prepare-packet` | **KILLED** | `ChainEnvironmentTests` (packet present) |
| R2b chain drops the missing-file refusal | **KILLED** | `ChainEnvironmentTests` (packet absent) |
| R2c check moved above the traps and restore | **KILLED** | `ChainEnvironmentTests` (restore count) |
| R2d inherited `ALIGN_R1_PREPARE_PACKET` overrides the fixed path | **SURVIVED** | none (D-8) |
| R2e chain reads a different fixed path | **KILLED** | `ChainEnvironmentTests` and two `R1Tests` chain cases |
| R2f driver accepts a packet naming another commit | **KILLED** | `test_requires_matching_commit_and_both_ok_and_records_packet_identity` |
| R2g driver accepts differing source hashes | **KILLED** | same |
| R2h production driver does not require the packet | **KILLED** | `test_production_driver_refuses_before_any_host_command_without_prepare` |

A same-commit stale packet is not a mutant: the shipped code accepts it (D-7).

## Owed before the native smoke

1. Nothing in round 5 blocks Part A or Part B. The Part B table may go to the lead for the sensor ruling on
   `e74b64793`.
2. The native D-load length, read from the smoke journal, against D-4's 150 s line.
3. `test_v4_next_arm_packet`, `test_w1_prequal` and the full-profile dynamic trace, where the orchestrator has
   not already reported them on this head.

## Owed before the arm

1. D-7: the packet deleted and regenerated on the final commit as part of the arm step, and its SHA-256
   compared with the arm record; or the driver consumes it (which repeats the smoke).
2. D-8: the decoy-variable assertion. Test only.
3. An owner for the `MAGISTRATE_WATCHDOG_STATUS_HOST` failure, and one run of `tests.test_run_night` on a
   quiet host to confirm the other seven are load.
4. The real prepare packet at `<measurement_root>/.align-r1-prepare.json`, with the real weight and
   installed-stack preflights.
5. Unchanged from the earlier list: RL-84 P-2 on the W1 branch before W1 signing.
