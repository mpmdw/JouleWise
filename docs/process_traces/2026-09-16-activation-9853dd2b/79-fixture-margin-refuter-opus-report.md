# 79 — Opus refuter report (contract + execution lenses, read-only) on the TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 fix, 2026-09-17 13:51–13:58 PDT

Worktree `/Users/edr/code/JouleWise-wt-flake`, fix commit `bf303ca3`. Verbatim hand-back follows.

VERDICT: **CONFIRM** — the fix is sufficient and the test is still defect-shaped. One non-blocking evidence-custody finding (item 3) and a scope note: HEAD now carries 3 files, not 1.

(1) CONTRACT LENS — defect shape preserved; mutant killed
Runway arithmetic, from scripts/run_night.py:841,849-851 — deadline_monotonic = now_mono + (t0 + window_max_s + GRACE − probes.now_epoch_s()), and the fixture clock is a constant t0+1 — so real runway = window_max_s − 1 + grace. Window end stays t0+2 regardless of grace, and the chain runs 3 s from t0+1, so it still crosses the window end by ~2 s and the "not interrupted" property is what is proven. Production inequality is read from a *separate* module object (_load_driver(module_name="run_night_wallclock_constants")), which mock.patch.object(self.driver, …) cannot reach; 120 ≤ 300 − 70 asserted and passing.
Mutant = grace patched to 0.0 (deadline at the window end, no allowance), via a throwaway subclass in /tmp (repo test untouched, harness since deleted):
```
FAIL: test_an_abort_that_spends_its_whole_budget_is_not_interrupted (GraceZeroMutant)
  File ".../tests/test_run_night.py", line 3775, in test_an_abort...
    self.assertEqual(self.driver.EXIT_GO, exit_code)
AssertionError: 0 != 4
Ran 1 test in 1.245s
FAILED (failures=1)
MUTANT_KILLED
```
Same assertion, same message as hosted CI. Grace-*scaling* mutants are still killed by sibling tests in the class, which pin the arithmetic exactly at the default grace 1.0 (assertEqual(t0+2+1, deadline["deadline_epoch_s"]) and the "window end + 1 s" detail string).

(2) EXECUTION LENS — 10/10 single test, class 6/6, duration unchanged
```
run 1: Ran 1 test in 3.193s |OK|real 3.35   run 6: Ran 1 test in 3.417s |OK|real 3.57
run 2: 3.192s OK real 3.35   run 3: 3.313s OK real 3.47   run 4: 3.354s OK real 3.51
run 5: 3.238s OK real 3.39   run 7: 3.199s   run 8: 3.312s   run 9: 3.184s   run 10: 3.197s
Ran 6 tests in 17.334s / OK      (python3 -m unittest -v ...WindowDeadlineTests; real 17.49)
```
Duration is set by the chain's own 3 s exit, not the grace — 3.184–3.417 s, no growth.

Margin quantified (grace bisect, unloaded): FAIL at runway 2.0/2.5/3.0 s, PASS at 3.5/4.0/5.0 s → consumption 3.0–3.5 s. Old fixture runway 4.0 s = 0.5–1.0 s headroom (1.15–1.3×); new runway 9.0 s = 5.5–6.0 s headroom (2.6–3.0×).
Causal reproduction under 16 busy loops (2× ncpu), cleaned up afterwards (0 remaining):
```
g3.0 run1 PASS | g8.0 run1 PASS
g3.0 run2: AssertionError: 0 != 4 ... GRACE=3.0 FAIL   | g8.0 run2: 4.144s GRACE=8.0 PASS
g3.0 run3 PASS | g8.0 run3 PASS   g3.0 run4 PASS | g8.0 run4 PASS
```
The old value fails under load with the exact CI signature; the new value survives the same load 4/4.

(3) DIFF SCOPE — the worktree was committed by another seat mid-review
At my first read the change was uncommitted and `git diff origin/main --stat` was indeed `tests/test_run_night.py | 9 +++++++--`. It is now commit bf303ca3, and `git diff origin/main --stat` is:
```
.../78-fixture-margin-evidence/quick-tier-full.log.gz | Bin 0 -> 5403 bytes
.../78-fixture-margin-fix-record.md                   |  47 +++++++++
tests/test_run_night.py                               |   9 +++-
3 files changed, 54 insertions(+), 2 deletions(-)
```
The committed test hunk is byte-identical to what I tested (blob 540d3b9f→175d73a1): one literal 3.0→8.0 plus the comment, nothing else; no production file touched; py_compile OK; working tree clean.

(4) THE "0 != 4" READ — confirmed, and uniquely the deadline
`EXIT_ABORTED = 4` (scripts/run_night.py:112; EXIT_GO=0, EXIT_REFUSED=3, EXIT_CHAIN_FAILED=5, EXIT_COURIER_FAILED=6). Exit 4 is reachable only at :2231 `base_exit_code = EXIT_REFUSED if refused else EXIT_ABORTED`, i.e. the abort path with termination proven. The other exit-4 candidate — an agent-present census abort — is impossible in this fixture: ProbeSource.run returns `_probe(argv, exit_code=1)` for AGENT_CENSUS_ARGV with no seeded responses (tests/test_run_night.py:232-236). So the wall-clock deadline is the only route to 4 here; a chain fault would have been 5, a refusal 3. Consistent with the driver aborting the chain at the deadline on a slow runner, not another defect.

RESIDUAL RISK
- This test no longer discriminates partial-grace mutants (grace/2 → runway 5 s survives; at 3.0 it would have died). Covered by the sibling exact-arithmetic assertions, but no longer here.
- The test never asserts that the chain actually outlived the window end; that rests on fixture arithmetic stated only in the comment. A later `window_max_s` edit could make it pass vacuously. An assertion on chain end vs window end would close it — not a blocker.
- Record 78 cites `78-fixture-margin-evidence/eight-runs-and-class.log` and `quick-tier-tail.log`; `.gitignore:45` (`docs/process_traces/**/*.log`) excludes both, so only the .gz lands and the merged history will not carry the cited files. The files do exist on disk and their content matches the record (8× OK, `Ran 6 tests in 17.507s OK`; `QUICK SUMMARY … failures=0 result=PASS rc=0`). Suggest renaming them to `.log.txt`/gzipping, or dropping the citation.
- Record 78's line "`git diff origin/main --stat` → tests/test_run_night.py | 9 +++++++--" went stale on its own commit (now 3 files). Cosmetic.
- Headroom is 2.6–3.0× local consumption; no bound is proven for the hosted runner (my repro is local M3 hardware under a synthetic 2× load proxy). If it recurs, the structural cure is to drive the deadline off a fake monotonic clock instead of real wall time.
- Requested heavy-load probe (64 loops) was denied by the sandbox classifier; the grace bisect substitutes for it. All runs were at 13:51–13:56 PDT, ~1 h 34 m before t0 15:30 — outside the armed window; no load processes left alive; canonical root and custody roots untouched.

## Magistrate disposition

CONFIRM accepted. The two custody nits are applied in the same commit as this record (evidence files renamed to `.txt`; record 78's stat line corrected). The two residual-risk test-strength points (partial-grace discrimination; an explicit chain-outlived-window assertion) are recorded on the lane TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 as follow-ups, not blockers. No fix round followed the refutation, so no delta re-audit is owed. The refuter's busy-loop probes ran 13:51–13:56 PDT, outside the armed span; the magistrate re-checked for surviving load processes below.
