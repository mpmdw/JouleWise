# R1 smoke admission budget (RUN_STATE 276): executing cold delta review

Reviewer: Claude Fable 5.2, independent executing seat (did not write the change; Opus built it). Written 2026-11-11 22:09 PST on the analysis Air. Blind: code, review text and wall-clock durations only; no v4, Block 6 or BYTES outcome and no energy or power value was read.

Target: `fix/2026-11-11-r1-smoke-276` @ `8546865375d0309db783cf359c2dec49b270df5b`, parent `dbd121c4e`. RL-84 P-5 requires this delta review before the smoke because the change alters executed bytes of `joulewise/align/apple/r1_runtime.py` (condition 13).

## Verdict: ADMIT-WITH-FIXES

**The executed bytes are admitted as they stand. Nothing in this review blocks tonight's smoke.**

The one fix is test-only and touches no condition-13 file. The committed suite does not kill the "constant applied to the non-smoke path" mutant, nor an equal-value literal in the launcher caps (F-1, F-2). I proved the non-smoke path unchanged by other means (check 1), so the gap is in the tests, not in the behaviour. Three witnesses that kill all five surviving mutants are given at the end; they can land before or after the smoke without a further review of executed bytes.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | Non-smoke behaviour unaffected | **Pass.** See "Non-smoke equivalence" below. |
| 2 | Arithmetic and Part B | **Pass.** 2,407.5 s needed, 592.5 s slack; worst admissible case 2,566 s. Part B's rise is justified. The post-G0 2,600 s does not depend on the old 1,800. |
| 3 | Binding | **Pass.** Engineering watchdog under RL-84 P-5. The ruled G0 cap is untouched. Condition 13 passes at the head. No pin or plan_tree to regenerate. |
| 4 | Fail-first | **Pass.** The head test file on parent source: 4 failures and 3 errors, covering all four new tests and both updated expectations. |
| 5 | Mutants | **Partly.** 8 of 12 killed. The four survivors are the non-smoke itimer (2) and equal-value literals in the caps (2); a fifth is killed only by a test that is already red (F-1). |
| 6 | Tests | **Pass.** Seven modules green; `test_r1_runtime` fails the same 9 as the parent. |
| 7 | Author's flagged risk (G0 timeout) | **Designed refusal, unchanged by this diff.** Nothing here makes a release less likely. See F-3. |
| 8 | Magistrate checks | **Both right.** 11,400 s is under the only deadline bound (12 h). |

## Non-smoke equivalence (check 1)

- **Static.** The diff changes four definitions: `Segment.reference_hook.hook.wait` and `main` in the runtime, `smoke` in the kit, `r1_part_caps` in the launcher. With the new constant and the bodies of the two smoke guards (`getattr(segment, "smoke_part", None)` and `args.smoke_part and args.r1_kind == "step-d"`) removed, the parent's and the head's `r1_runtime.py` have identical ASTs. The constant is read at three runtime lines (1693, 1694, 2378), all inside those guards.
- **The night driver never passes the flag.** `--smoke-part` and `--smoke-started` are built in one place, `scripts/align_r1_followup_kit.py:294`, inside `smoke()`. `scripts/align_r1_rehearsal.py` and `scripts/align_r1_runtime.py` contain neither. Executed: the full follow-up night under `FakeWorld` (108 commands, 20 runtime invocations, and again with a step-D G0 timeout) uses only `--r1-kind`, `--output`, `--host-lock-fd`, `--soak-reference` and `--duration-s`. The argv sequence is identical at the parent and the head.
- **Executed probe, parent against head.** A non-smoke step-D through `rt.main` on the synthetic backend, once releasing and once with a G0 that never releases: exit code, custody status, the 24 output files and the result are equal, apart from the probe's own pid and the digest of a config that embeds its temp path. Neither commit arms an itimer or installs a SIGALRM handler. The changed closure called directly without a smoke part (three kinds, released and timeout, elapsed 100, 2,500 and 3,500 s): 18 rows equal, no itimer, no `smoke_part_a.json`, same re-arm and quiet span.
- `r1_part_caps` and `r1_minimum_seconds` are reached only from the `r1-smoke` runner kind (`launch_align_r0.py:276`, `run_align_r1_smoke.py:318`). The R0 desk path does not call them.

## Arithmetic (check 2)

- Evidence against RUN_STATE 276: Part A started 20:52:45 and step D entered G0 at 21:10:37, which is 1,072 s; the author's 551.3 + 521.6 = 1,072.9 s agrees. The itimer fired at 1,800 s, 727 s into G0. The R1 night's whole step-D member took 1,849 s, which leaves about 131 s after start-up and a full G0; the author's 134.6 s agrees to within 4 s. I could not read the MBP records, so the tenths are the author's.
- Need: 551.3 + 521.6 + 1,200 + 134.6 = 2,407.5 s. Budget 3,000 s, slack 592.5 s.
- **Slow predecessor.** Each of the two 3,000-frame idle baselines (predecessor and step D) is cut by its own capture timeout at 300 x 1.5 + 10 = 460 s (`powermetrics.py:1468`), against 381 s measured. The worst run that is still admitted therefore adds about 2 x 79 s: 2,566 s, with 434 s to spare and a full G0. At the old 240 ms a frame a baseline would take 720 s; two of them would need 3,086 s and would not fit, but that case cannot arrive, because the capture refuses at 460 s as it did in item 274.
- **Part B.** The kit's `smoke()` runs the same predecessor and the same step-D start-up for B, and the runtime arms the same pre-G0 itimer from the same kit clock. So B needed the same rise: 3,000 + 2,600 + 120 = 5,720 s.
- **Post-G0.** At G0 release the runtime replaces the itimer with `smoke_post_g0_budget`: 300 quiet + 1,580 turn + 600 recovery + 120 close = 2,600 s. It is counted from the release and reads neither 1,800 nor the new constant. `MEMBER_CAP_S = 1800` is a different, unchanged constant.
- The launcher's 120 s outside the kit clock held in smoke 276: Part A ran 1,855 s against an 1,800 s itimer.

## Binding (check 3)

- RL-84 P-5: "The ruled 1,200 s is the G0 cap and nothing else", and an engineering fix that changes executed bytes "gets its delta review before the smoke". `g0_timeout_s` stays 1,200 in `configs/align/v4/r1_runtime.json`, which the diff does not touch (RL-59). RL-72 E5's twenty minutes is an estimate by the same ruling. RL-78 and RL-84 P-1 are untouched: no sidecar or predecessor change.
- Of the ten condition-13 files (RL-84 P-4) only `r1_runtime.py` changed. `verify_r1_executed_sources` executed at the head returns the head; against the parent commit it reports the drift in that one file, as it should. The smoke's W1 thermal-gate check (bytes at `82c14c9ea`) passes.
- Condition 13 compares the working tree with the commit and stores no digest. No blob or sha256 of the three changed sources is pinned anywhere in the tree. `test_v4_registration`, both closure tests and the refusal census pass, so no identity pin, registry guard or plan_tree needs regenerating.

## Tests (check 6)

One module at a time, `nice -n 10 python3.13 -B -m unittest`, 29 GB free throughout.

| Module | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 41 OK |
| `tests.align.test_r1_followup` | 12 OK |
| `tests.align.test_r1_round7_science` | 18 OK |
| `tests.align.test_v4_registration` | 24 OK |
| `tests.align.test_v4_executed_closure` | 6 OK |
| `tests.align.test_v4_dynamic_closure` | 10 OK |
| `tests.hazards.test_refusal_allowlist` | 24 OK, 1 skipped (as in the author's run) |
| `tests.align.test_r1_runtime` | 33 run, 7 failures and 2 errors: the same 9 names as `base_fail.txt` and `after_fail.txt` |

Fail-first: the head's `test_r1_smoke_launcher.py` on parent source gives `{'A': 1920, 'B': 4520} != {'A': 3120, 'B': 5720}`, `4520 != 5720`, `1800.0 not greater than or equal to 2407.5` (both parts), and three errors on the missing constant.

## Mutants (check 5)

Each applied to a scratch worktree at the head and restored.

| Mutant | Outcome | Killed by |
|---|---|---|
| Pre-G0 itimer left at 1,800 | Killed | `test_runtime_pre_g0_itimer_is_the_admission_budget` (A and B) |
| G0-return check left at 1,800 | Killed | `test_g0_released_after_1800_s_but_inside_budget_admits_and_stops_part_a` |
| G0-return message left at 1,800 | Killed | same |
| Kit predecessor check at 1,800 | Killed | `test_kit_part_a_checks_use_the_admission_budget` |
| Kit close check at 1,800 | Killed | same |
| Launcher A cap `1800 + 120` | Killed | `test_caps_derive_post_g0_budget_from_runtime_config`, `test_part_a_budget_covers_...` |
| Launcher B cap `1800 + post_g0 + 120` | Killed | those two and `test_part_b_may_finish_after_1800_seconds` |
| Launcher A cap `3000 + 120` (not derived) | **Survived** | F-2 |
| Launcher B cap `3000 + post_g0 + 120` (not derived) | **Survived** | F-2 |
| Itimer armed on a non-smoke step-D (guard reduced to the kind) | **Survived** | F-1 |
| Itimer armed for every kind (guard `if True`) | **Survived** | F-1 |
| G0-return check on the non-smoke path (guard `if True`) | **Not cleanly killed** | Only `test_step_d_with_an_unreleased_g0_is_inconclusive` changes, from ERROR to FAIL; it is one of the 9 already red (F-1) |

## Findings

**F-1 (MEDIUM, tests only; does not block the smoke). No green test holds the smoke budget off the non-smoke path.** With the `main` guard reduced to `args.r1_kind == "step-d"`, every night step-D would run under a 3,000 s SIGALRM that nothing clears, and all eight modules stay as they are. The cause is older than this change: the tests that drive a real step-D through `rt.main` are among the 9 stale failures in `test_r1_runtime`, so that path has no green coverage. The head itself is right (check 1). Fix: the first two witnesses below.

**F-2 (LOW, tests only). The cap tests do not prove derivation.** They compare the caps with `rt.SMOKE_ADMISSION_S + 120` without moving the constant, so a literal of the same value passes. Fix: the third witness.

**F-3 (LOW, note for tonight). A G0 timeout in the smoke is a refusal, and its message names the wrong number.** If step D's G0 runs to its 1,200 s cap, the wrapper writes `smoke_part_a.json` with the timeout row and raises "smoke Part A did not release within 3000 s", at about 1,073 + 1,200 = 2,273 s on the kit clock. Part A exits non-zero and Part B does not run. The `outcome != "released"` condition is the parent's and this diff does not touch it; under the old 1,800 s it could never be reached, because the wall cap always fired first. So the change makes the designed refusal visible and creates no new one. Nothing in the diff touches the gate, the reference, the bands or the host, so a release is no less likely than before. The timeout is not mis-classified as a pass or as a budget overrun, but the text reads like one. **If Part A fails tonight with that message, read `g0.outcome` in `smoke_part_a.json` first: a `timeout` there is a finding about the gate (RL-59), not a reason to resize the budget again.** In smoke 276 the gate had not released after 727 s. Part B raises the same text, still saying "Part A". Rewording it would change condition-13 bytes, so not before this smoke.

**F-4 (INFO).** If the phases before G0 ever exceed 1,800 s and G0 then also times out, the itimer and the G0 return coincide near 3,000 s and the refusal may read "smoke part wall cap reached" instead. Either way it is a refusal.

**F-5 (INFO, not from this change).** `r1_minimum_seconds()` allows 300 + 10 s before Part A; smoke 276 used 334 s from launch to Part A. A deadline at exactly the 9,510 s minimum could admit the launch and then refuse Part B after a worst-case Part A. At 11,400 s there are about 1,840 s to spare at that point.

## Magistrate checks (check 8)

Executed at the head:

```
c = launcher.r1_part_caps()
assert c=={"A":3120,"B":5720}
DEADLINE = now + 11400
```

- `r1_minimum_seconds()` returns 9,510 = 3,120 + 5,720 + 300 + 2 x 180 + 10. 11,400 leaves 1,890 s over the minimum, the same margin the earlier 9,000 left over 7,110.
- The only bound on the deadline is `MAX_DESK_SECONDS` = 43,200 s (12 h, `launch_align_r0.py:268`). The plist's `ExitTimeOut` (2 x 180 + 40 = 400 s) is teardown grace and does not bound the run. The wrapper script and the smoke runner add no other ceiling.
- Condition 13 in the smoke compares against the checkout's HEAD. This report's commit changes no executed file, so the smoke may name either this commit or `854686537`; the checkout must be at the commit it names.

## Proposed witnesses (F-1, F-2)

Run on the unmutated head: 3 pass. Run under the five surviving mutants: each is killed. Not committed as code, by this review's constraint. They belong beside `SmokeAdmissionBudgetTests` in `tests/align/test_r1_smoke_launcher.py`, which already has the imports.

```python
class SmokeAdmissionScopeTests(unittest.TestCase):
    def test_runs_without_a_step_d_smoke_part_arm_no_itimer_or_alarm(self):
        from joulewise.align.apple import r1_runtime as rt

        class Stop(Exception):
            pass

        def segment(**_):
            return SimpleNamespace(run=lambda: (_ for _ in ()).throw(Stop()), close=lambda: [])

        root = launcher.Path(launcher.__file__).resolve().parents[1]
        cases = ((["--r1-kind", "step-d"], []),
                 (["--r1-kind", "step-30b"], []),
                 # --smoke-part on another kind arms nothing; main only clears on exit
                 (["--r1-kind", "step-30b", "--smoke-part", "A", "--smoke-started", "0"],
                  [(signal.ITIMER_REAL, 0)]))
        for extra, timers in cases:
            alarms = []
            real = signal.signal

            def record(num, handler):
                if num == signal.SIGALRM and callable(handler):
                    alarms.append(getattr(handler, "__name__", ""))
                return real(num, handler)

            with self.subTest(argv=extra), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(rt, "read_soak_reference", return_value={}), \
                    patch.object(rt, "Segment", side_effect=segment), \
                    patch.object(rt.signal, "signal", side_effect=record), \
                    patch.object(rt.signal, "setitimer") as timer:
                code = rt.main(["--config", str(root / "configs/align/v4/r1_runtime.json"),
                                "--output", str(Path(tmp) / "out"), *extra],
                               backend_factory=lambda _config: SimpleNamespace(close=lambda: None),
                               stdout=__import__("io").StringIO())
                self.assertNotEqual(code, 0)
                self.assertEqual([c.args for c in timer.call_args_list], timers)
                self.assertNotIn("smoke_timeout", alarms)

    def test_non_smoke_g0_return_ignores_the_admission_budget(self):
        from joulewise.align.apple import r1_runtime as rt
        for outcome in ("released", "timeout"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as tmp:
                segment = object.__new__(rt.Segment)
                segment.kind, segment.out, segment.quiet_spans = "step-d", Path(tmp), []
                session = SimpleNamespace(reference={"fast_c": 40., "slow_c": 40.}, flags=[],
                                          wait=lambda *a, **kw: {"outcome": outcome})
                with patch.object(rt.time, "monotonic", return_value=rt.SMOKE_ADMISSION_S + 500.0), \
                        patch.object(rt.signal, "setitimer") as timer, \
                        patch.object(rt, "rearm_deadman") as rearm:
                    segment.reference_hook({}, quiet_s=0, rearm_s=1580, capture=True)(session)
                    self.assertEqual(session.wait("G0", deadman="d")["outcome"], outcome)
                timer.assert_not_called()
                rearm.assert_called_once_with("d", 1580, "R1_after_G0_release")
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_launcher_caps_follow_the_constant(self):
        from joulewise.align.apple import r1_runtime as rt
        with patch.object(rt, "SMOKE_ADMISSION_S", 3333):
            self.assertEqual(launcher.r1_part_caps(), {"A": 3333 + 120, "B": 3333 + 2600 + 120})
```

## Method and limits

- Worktrees `/Volumes/JW-EXT/jw-wt/rev-smoke276{,-base,-mut}`, removed after this report; TMPDIR on the SSD; no host-changing command; no MBP access. The author's worktree was not touched.
- The measured phase durations are the author's and the magistrate's; I checked them against RUN_STATE 276 only.
- The mutant kills of the proposed witnesses were run from a scratch test file with its own imports. The text above, as adapted to the launcher test module, was then run in place in that module on the unmutated head (3 pass); it was not re-run under the mutants in that form.
