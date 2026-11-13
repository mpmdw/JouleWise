# R1 post-smoke tests and trace: executing cold review

Reviewer: Claude Fable 5.2, independent executing seat (did not write the branch; Sonnet and Opus did). Written 2026-11-11 22:36 PST on the analysis Air. Blind: code, review text, rulings and synthetic test output only; no v4, Block 6 or BYTES outcome was read.

Target: `ops/2026-11-11-r1-post-smoke-tests` @ `f02bf13469b529747d97af71b4a884acd88108cf`, range `9c5ba057e..f02bf1346` (four commits) over `ops/2026-11-11-w1-presign`.

## Verdict: ADMIT-WITH-FIXES

**The branch may merge into presign as it stands.** It changes no production byte, all ten modules are green, and every mutant the authors claimed is killed.

The fixes are test-only and can follow the merge:

- **F-1:** one witness was lost in the migration. No test now holds the "accepted step-d result lacks slots" refusal. A witness is given below.
- **F-2:** one migrated test carries a comment that says the opposite of what it asserts.

Of the 14 migrated tests, none passes trivially and none asserts behaviour that contradicts RL-59, RL-64, RL-72 or RL-78.

## Scope

```
 docs/align/v4/dynamic_closure_trace.json  |  38 ++++--
 tests/align/test_r1_round6_exec_review.py |  15 ++-
 tests/align/test_r1_round6_lows.py        |  29 +++--
 tests/align/test_r1_round6_power.py       |  39 +++---
 tests/align/test_r1_round7_science.py     |  45 +++++++
 tests/align/test_r1_runtime.py            | 190 ++++++++++++++++++++----------
 tests/align/test_r1_smoke_launcher.py     |  61 ++++++++++
 7 files changed, 313 insertions(+), 104 deletions(-)
```

`git diff --stat 9c5ba057e f02bf1346 -- . ':!tests' ':!docs'` is empty. `scripts/test_timings.json` is untouched; it is keyed by module, so the renamed and deleted tests need no entry.

## Per commit

| Commit | Content | Result |
|---|---|---|
| `c21e2eac6` | Full-profile dynamic closure trace, 195 executed paths | **Pass.** The path set still matches presign. Three statements around it are inaccurate (F-3); none changes the conclusion. |
| `0ac0caaa5` | `SpanAndDeadlineTests` (R7-2 review F1) | **Pass.** M3 and M4 killed, plus three variants of mine. |
| `09138a1da` | Migration of 14 stale tests | **Pass with F-1, F-2.** 21 of 22 targeted mutants killed; the survivor is not a regression (F-5). One coverage probe survives (F-1). |
| `f02bf1346` | `SmokeAdmissionScopeTests` (RUN_STATE 276 review F-1, F-2) | **Pass.** All five of that review's surviving mutants killed, in the committed in-module form. |

## Commit 1: the trace

- **Dropping the zsh chain is sound.** `scripts/night_chains/align_r1_rehearsal.zsh` is in `ARTIFACTS`, is strict, and is in `EXECUTED_CLOSURE`. The static closure test takes every file under `scripts/night_chains/` as an entry point and names this one as required (`test_v4_executed_closure.py:151`). It is not on the amendment allowlist.
- **The three added paths are bound and strict.** `align_r1_followup_kit.py` and `align_r1_thermal_replay.py` are not in the static `EXECUTED_CLOSURE`; the dynamic trace is what shows them executed, which is its purpose.
- **The path set still matches presign.** The trace was made at `322f7f1cd`. Between it and `9c5ba057e`, three production files changed, not one: `r1_runtime.py`, `scripts/align_r1_followup_kit.py` and `scripts/launch_align_r0.py`. None adds an import, a subprocess launch or a script path, so the executed set cannot have changed.
- **Live check at the head.** I re-ran the `r1_synthetic_arm` and `r1_to_w1_chain` scenarios through `run_scenarios`: 47 and 49 tests OK, 156 paths, none outside the committed set. The zsh chain is not executed; the three added paths are.
- The file's SHA-256 is `e7152f98...624d`, as the commit states. `test_v4_dynamic_closure` (10) and `test_v4_executed_closure` (6) pass.

## Commit 2: span and deadline witnesses

Each mutant applied to `scripts/align_r1_rehearsal.py` in a scratch worktree, run against `SpanAndDeadlineTests`, then restored.

| Mutant | Outcome |
|---|---|
| M3: the bound goes to another local, `span_cap` stays `None` | Killed (span test: night ends `complete`) |
| M4: `_R1_WORK_DEADLINE` never armed | Killed (deadline test) |
| Deadline armed at `+ 900` instead of `- 900` | Killed |
| Deadline not cleared after `run()` | Killed |
| Span check loosened by 900 s | Killed |

## Commit 3: the 14 migrated tests

All 14 fail at `9c5ba057e` and pass at the head; I ran both. Module prefixes: RT = `test_r1_runtime`, EX = `test_r1_round6_exec_review`, LO = `test_r1_round6_lows`, PW = `test_r1_round6_power`.

| # | Test | What changed | Judgement |
|---|---|---|---|
| 1 | RT `ConformanceTests.test_every_kind_conforms_and_feeds_the_driver` | S6 status `adopted`; consumers' G0 reference is step-D R_D by value and source; 1,200 s cap asserted for step-30b and the legs too | **Sound, stricter.** RL-59: "1,200 s stays, for every R1 gate". The old `assertIsNone` for step-30b and the legs is rightly gone. |
| 2 | RT `IncompleteMemberTests.test_planning_turn_with_an_unreleased_g0_is_inconclusive` | Builds a real step-d first; asserts the turn ran flagged `r1.g0_timeout_run`, `candidate_only`, null release temperature, one turn, G0 `timeout` | **Sound.** RL-72 E3. The name no longer describes it (F-2). |
| 3 | RT `IncompleteMemberTests.test_planning_turn_cut_by_the_deadman_fails_the_segment` | Fixture only: step-d sibling made under the ordinary deadman | **Sound, assertions unchanged.** |
| 4 | RT `IncompleteMemberTests.test_step_d_with_an_unreleased_g0_is_inconclusive` | Step-d runs flagged with slots; a gated consumer now succeeds and reads the same reference | **Sound, with F-1 and F-2.** The contract says "A captured R_D survives a timeout" and RL-59 says step-D's timeout does not skip the gated block. The old consumer-refusal assertion had no replacement. |
| 5 | RT `Round5RuntimeTests.test_planning_deadman_is_armed_after_the_preheat_and_g0` | Fixture only | **Sound, assertions unchanged.** |
| 6 | RT `Round5RuntimeTests.test_gated_d_run_gates_against_the_step_d_reference_not_the_soak` (renamed) | Real step-d; refusal with no step-d sibling; reference equals R_D and differs from the soak value; `_check_d_reference_consumed` | **Sound, stricter.** |
| 7 | RT `Round5RuntimeTests.test_aba_leg_without_its_own_g0_release_is_inconclusive_not_a_failure` | Leg runs flagged, exit 0, `g0_released` false; the result is fed to `r1.aba_adoption`, which returns inconclusive for leg B | **Sound.** The driver line that maps an unreleased leg to `None` is not exercised here, but `test_r1_rehearsal` kills a mutant on it. |
| 8 | RT `Round5RuntimeTests.test_cooldown_releases_on_the_one_sided_g0_band` | Reference is R_D; a second case with R_D 5 °C above the world | **Sound, stricter.** The second case is what kills the two-sided mutant. |
| 9 | RT `Round5Tests.test_step_d_consumer_requires_complete_digest_bound_custody` | A real `Segment`; `accepted_result` and `consume_d_reference` asserted directly; wrong-kind refusal | **Sound, stricter.** |
| 10 | EX `PhaseOrderTests.test_gated_runs_follow_a_d_turn_and_calibrations_follow_a_bounded_precool` | Planning kinds still follow a bounded idle-until-soak; the other G0 kinds are pinned to their exact predecessor | **Sound, stricter.** RL-72: the 30B predecessor and step-D are one unit; RL-59: no soak release before a leg. |
| 11 | LO `RehearsalLowTests.test_soak_reference_checks_slow_role_only_and_records_roles` | Targets `_check_d_reference_consumed`: fast value refused, slow accepted, soak source refused, empty step-d refused | **Sound.** |
| 12 | LO `RuntimeLowTests.test_g0_timeout_alone_remains_inconclusive` | No diff; it calls test 7 | **Sound**, as test 7. |
| 13 | PW `R1NightWorstCaseTests.test_worst_case_sums_every_phase_cap` | On `admission_units`; step-d unit is 1,800 + 5,763.9952; `largest_unit_s` added | **Sound.** |
| 14 | PW `test_worst_case_uses_the_round6_table_and_counts_the_r6_2_retries` | Deleted | **Sound.** Its keys no longer exist. The pointer is right: `test_r1_round7_science.G0TimeoutTests.test_night_worst_case_with_the_round8_bounds` asserts the full unit table and RL-72 E2's 126,480 s. |

### Mutants

Each is a production change the old test was meant to catch, applied in a scratch worktree, run against the migrated test, then restored.

| Test | Mutant | Outcome |
|---|---|---|
| 1 | S6 status back to `TODO` | Killed |
| 1 | `step-30b` removed from `G0_TIMEOUT_KINDS` | Killed |
| 6 | Gated D captures its own reference | Killed |
| 6 | Gated D's session reference overwritten with the soak values | Killed |
| 8 | `Segment.reference()` returns the soak values | Killed. Test 6 stays green under it, correctly: the gated hook overwrites that value with the authenticated R_D |
| 9 | Custody status check dropped | Killed |
| 9 | Result digest check dropped | Killed |
| 8 | Cooldown band made two-sided | Killed |
| 5 | Planning deadman not re-armed after G0 | Killed |
| 5 | Planning deadman left armed through G0, still re-armed after | **Survived** (F-5) |
| 4 | `step-d` removed from `TIMEOUT_RUN_KINDS` | Killed |
| 2 | Planning hook does not install the timeout-run hook | Killed |
| 7, 12 | A-B-A kinds removed from `TIMEOUT_RUN_KINDS` | Killed (both) |
| 7 | `aba_adoption` ignores the legs' own G0 | Killed |
| 3 | `episode.deadman:` removed from the incomplete-member flags | Killed |
| 11 | Check accepts the fast value | Killed |
| 11 | Check ignores the source | Killed |
| 13 | Blackout 3,600 s | Killed |
| 13 | Capture pair no longer one unit | Killed |
| 13 | X-G dropped from the units | Killed |
| 10 | A precool inserted between the predecessor and step-d | Killed |
| 10 | Planning precools removed | Killed |

Coverage probes, run against whole modules:

| Probe | Outcome |
|---|---|
| Driver treats every leg as G0-released | Killed by `test_r1_rehearsal` (2 tests) |
| Driver keeps an unreleased leg's `t_decline_s` | Survives; `aba_adoption` still returns inconclusive from `leg_g0`, so only the recorded value differs |
| `step_d_result` slots check removed | **Survives** `test_r1_runtime`, `test_r1_round6_lows` and `test_r1_followup` (F-1) |

## Commit 4: smoke admission scope

Run against `SmokeAdmissionScopeTests` as committed in the module. The RUN_STATE 276 review had run these kills only from a scratch copy.

| Mutant | Outcome |
|---|---|
| Itimer armed on a non-smoke step-D (guard reduced to the kind) | Killed, FAIL: timer armed with 2,999.99 s |
| Itimer armed for every kind (`if True`) | Killed, FAIL |
| G0-return guard on all paths (`if True`) | Killed, ERROR (`smoke_started` missing), both outcomes |
| Launcher A cap `3000 + 120` | Killed, FAIL |
| Launcher B cap `3000 + post_g0 + 120` | Killed, FAIL |

## Tests at the head

One module at a time, `nice -n 10 python3.13 -B -m unittest`, 29 GB free before each.

| Module | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 44 OK |
| `tests.align.test_r1_runtime` | 33 OK |
| `tests.align.test_r1_round6_exec_review` | 9 OK |
| `tests.align.test_r1_round6_lows` | 18 OK |
| `tests.align.test_r1_round6_power` | 24 OK |
| `tests.align.test_r1_round7_science` | 20 OK |
| `tests.align.test_r1_rehearsal` | 77 OK |
| `tests.align.test_v4_executed_closure` | 6 OK |
| `tests.align.test_v4_dynamic_closure` | 10 OK |
| `tests.align.test_v4_registration` | 24 OK |

At `9c5ba057e` the four migrated modules fail exactly the 14 tests: 9, 1, 2 and 2.

## Findings

**F-1 (LOW, tests only). The migration dropped the only witness of the slots refusal.** `Segment.step_d_result` refuses a custody-bound step-d result that has no `slots` ("accepted step-d result lacks slots"). Before `a85ee8ec6` that check was part of the same condition the old test 4 exercised, when a gated consumer read an inconclusive step-d and exited `EXIT_REFUSED`. The rewrite rightly replaced that case, because a timed-out step-d now has slots. Nothing took its place, and with the check removed all of `test_r1_runtime`, `test_r1_round6_lows` and `test_r1_followup` stay green. By reading, a slot-less, custody-complete step-d is still reachable: `k_step` returns the inconclusive record when G0 ends unobserved or by deadman with no turn (`only_g0_unreleased`). I did not execute that path. The witness below passes at the head and fails under the mutant; it belongs in `Round5Tests`.

```python
    def test_a_custody_bound_step_d_result_without_slots_is_refused(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            step_dir = root / rt.STEP_D_SEGMENT
            step_dir.mkdir()
            (step_dir / rt.RESULT_NAME).write_text(json.dumps(
                {"kind": "step-d", "segment_status": "inconclusive", "g0_released": False}))
            rt.write_custody(step_dir, {"status": "complete"})
            segment = object.__new__(rt.Segment)
            segment.out, segment.kind = root / "consumer", "d-spam-benign-s1-a"
            self.assertEqual(segment.accepted_result(rt.STEP_D_SEGMENT, "step-d")["kind"], "step-d")
            with self.assertRaisesRegex(rt.Refused, "lacks slots"):
                segment.step_d_result()
```

**F-2 (LOW, test comments and names).**
- `test_r1_runtime.py:520-523` says the timed-out step-d's "captured reference is not an admitted R_D, so no consumer may read it". The same test then asserts that a gated consumer exits 0 and reads exactly that reference, which is what the contract requires. The comment should go; the later one at the consumer call is right.
- The conformance test keeps the old R7-2 comment "every other member keeps the 600 s default" a few lines above the new assertion that step-30b and the legs arm 1,200 s.
- Four names now describe the old behaviour: tests 2 and 4 (`..._is_inconclusive`, while test 4 asserts `is_g0_inconclusive` false), test 10 (`calibrations_follow_a_bounded_precool`) and test 11 (`test_soak_reference_checks_...`).

**F-3 (INFO). Three statements about the trace are inaccurate; the trace itself is right.**
- The commit message says the previous lane "moved a --bounded trace in place". The presign trace has nine scenarios, no `profile` key and 78 tests in `r1_synthetic_arm`. It is the pre-kit full trace from `7d2f50ba1`, made before `a85ee8ec6` narrowed that scenario.
- "Only the full R1 night executes" the zsh chain is not quite it. Two shimmed wrapper tests execute it: `test_r1_rehearsal.R1Tests.test_zsh_chain_signal_burst_still_restores_automatic` and `test_zsh_chain_passes_the_inputs_entrypoint_unless_overridden`. The scenario stopped including them at `a85ee8ec6`.
- Three production files changed after the trace's base, not only `r1_runtime.py` (see commit 1).

**F-4 (INFO, next regeneration).** Since `a85ee8ec6` the dynamic trace no longer observes the zsh chain; its binding rests on the static closure alone. Adding the two wrapper tests named in F-3 to `r1_synthetic_arm` would restore the dynamic observation for about a second of test time. That edits the trace tool, so it is not for this branch.

**F-5 (INFO, older than this branch).** If the planning hook leaves the deadman armed through preheat and G0 and still re-arms it afterwards, test 5 stays green, because it only checks the deadline after G0. The migration did not touch those assertions.

**F-6 (INFO, production, for the next driver rebind).** `_check_d_reference_consumed(name, {}, {})` passes: a missing source and value on both sides compare equal. I found no path that reaches it with both empty.

**F-7 (INFO).** `test_launcher_caps_follow_the_constant` hard-codes the post-G0 budget as 2,600. It will need editing if `STEP_QUIET_S`, the step deadman or the recovery cap move.

## Method and limits

- Worktrees `/Volumes/JW-EXT/jw-wt/rev-postsmoke{,-base,-mut}`, removed after this report. TMPDIR on the SSD. No host-changing command, no MBP access.
- Mutants were applied by exact-text replacement in the `-mut` worktree and reverted after each run; the worktree was clean at the end. Logs and the mutant script are in `/Volumes/JW-EXT/scratch/rev-postsmoke` (scratch, not committed).
- I did not re-run the full nine-scenario trace (86 minutes for the author). The two R1 scenarios were re-run live; the other seven rest on the diff showing no new import or launch edge.
- A first live-trace attempt fed the script on stdin, which a spawned child cannot re-import; its one failure was that artefact. The clean re-run from a file is the one reported.
- Rulings read: RL-59, RL-64, RL-72 and RL-78 in `RESEARCH-LEAD-DECISIONS.md` on `origin/audit/2026-11-10-fable`, and `docs/align/r1_runtime_contract.md`.
