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
