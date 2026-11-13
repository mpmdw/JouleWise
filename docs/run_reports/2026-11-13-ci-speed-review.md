# Cold review: CI-speed PRs #755, #756, #758

Reviewer: Opus 5.5, an independent cold seat. Written 2026-11-13 09:25 PST.
This is an engineering review, not a paper-bound one. The verdict is final for merge.

Heads reviewed:
- #755: `75379522586a` onto `ops/2026-11-11-w1-presign`. Its merge-base is `c1d8fa8b2`; the lane is now at `e2696f023` and still merges clean.
- #756: `d610eac279c6` onto main.
- #758: `e28f1629e41e` onto main.

Each PR merges clean onto its current base, and #756 and #758 merge clean with each other (`git merge-tree`).

Evidence: the diffs, plus these CI logs:
- 43459892780: the #755 run.
- 43463516682: the #758 run.
- 43435838556: the main push at #758's base `0101ee536`.
- 43386791770, job 131757311309: a serial lane run at `880e7fca0`.
- A shell probe of `ci_state_only.sh` in a scratch repository.

I ran no test modules on the Air.

## Verdicts

| PR | Verdict |
|---|---|
| #755 (W1 lane: BYTES world split and seed pool) | **ADMIT** |
| #756 (state-only classifier) | **ADMIT** (fold in the comment nit N1 if convenient; it does not block) |
| #758 (60-minute shards, 900 s watchdog, 6 shards × 4 workers) | **ADMIT-WITH-FIXES** (F1 and F2 are required) |

None of these PRs comes from an untrusted audit, so the open-PR rule does not apply. The `gate-ledger` check is red on all three. Each fails on "row 1 / row 5: full tier needs RUN evidence here, not N/A", so each PR body needs its ledger rows filled, citing this review for the review row.

---

## #755: ADMIT

**Coverage.**
- All 60 seeds run. Run 43459892780 has exactly 20 `BYTES synthetic <world> seed … complete` lines for each of bytes, time and resident, with no duplicates.
- The module ran 114 tests across its units (1+1+1+2+105+1+2+1). That equals the base's 112, minus the one unsplit method, plus the three world methods.
- The method body (tests/test_bytes_analysis.py:1069-1159) is a mechanical move:
  - D3 runs in the worker on a fresh `NumericTestCase()` (:1039), with the same assertions and the same messages.
  - The `unavailable == []` check, the H1 word counts and the H2 coverage and estimate accumulators run in the parent, on the returned outputs, in seed order.
  - Every per-world aggregate assertion is unchanged.
  - The new `assertEqual(set(design["seeds"]), {"bytes","time","resident"})` stops a fourth world from silently going unrun.
- A failure in a worker comes back through `pool.map` as an `AssertionError` at that seed's position. The test fails at the same seed it would have failed at serially, and `cancel_futures` plus `wait=True` leave no orphans.

**Determinism.**
- Strong evidence. I took the per-world `BYTES_SIMULATION_REPORT` dicts from the pooled run and from the serial run 43386791770 (`880e7fca0`, one three-world line) and compared their JSON with `sort_keys`. All three worlds are byte-identical, including the D3 minima, H2 method coverage, mean estimates and word rates.
- The design is also sound:
  - The fixture uses `random.Random(seed)` and `random.Random(seed*7919+1)` (tests/fixtures/bytes/campaign.py:107-108). It touches no global RNG.
  - Each seed has its own TemporaryDirectory.
  - The CLI stages are subprocesses.
  - The only cache in `bytes_analysis` is `_registered_predictors`, an `lru_cache` over a hash-checked file.
- The spawn workers import `tests.*`, so `tests/__init__.py` installs the host-command guard in each worker. The workers inherit the test's guard report, which is the right attribution.

**Condition-13 and RL-95.**
- The diff touches only `scripts/test_timings.json` and `tests/test_bytes_analysis.py`. It touches nothing in `R1_EXECUTED_SOURCES` (v4_registration.py:484-490) and no Block 6 program file.
- `joulewise/bytes_analysis.py` is blob `dffccd8d…` at the base, the PR head and the lane head. Its sha256 is `18582818c7e0…a71`, the version pinned in `configs/b6/packs/bytes-*/registration.json`.
- `scripts/test_timings.json` appears in `configs/pins/registry.json:4818` and in the v5 sealed inventory only as `file@c27485347…`, a historical blob, so editing it now breaks no pin.

**Notes. None blocks; all concern the next main-to-lane merge.**
- L1, the log format: there are now three one-world `BYTES_SIMULATION_REPORT=` lines in place of one three-world line. Anyone harvesting it for the BYTES validation section must join the three lines in world order. The values are identical, so this is a format change only.
- L2, pool size: `_campaign_runner` defaults to `os.cpu_count()` workers (:1055). Once the lane takes #758 (4 shard workers per 4-vCPU runner), each world's pool contends with 3 other workers. The world methods measured 454-649 s with an uncontended 4-process pool, and a serial world is about 1,914 s. Under contention they can pass the 900 s watchdog.
- L3, a stale pin test on main: `tests/test_bytes_campaign_split.py`, `docs/perf/2026-11-08-bytes-world-split.patch` and `tests/fixtures/ci/bytes_campaign_word_rates.py.txt` on main pin the old patch-based split. That test applies the patch to a copy of the repository's `scripts/test_timings.json`. On the lane after this PR, the BYTES declaration is the three-world one, so `git apply` will fail and the test goes red on the next main-to-lane merge. `test_timings.json` will also conflict.
  - Fix: prune all three on main (superseded by #755) and give main's inactive BYTES declaration the three world ids, either before or in the main-to-lane merge.

---

## #756: ADMIT

**Classifier** (scripts/ci_state_only.sh):
- It exits 0 only when every path in `git diff --name-only --no-renames before..after` is exactly `RUN_STATE.md`, `TASK_QUEUE.md` or `docs/process/CURRENT.json`.
- Malformed, zero or unknown SHAs, an empty range and any git error all exit 1, which runs the full suite.
- `--no-renames` turns a rename into delete plus add, so the source path still has to be on the allow-list.

My probe in a scratch repository gave these results:

| Case | Result |
|---|---|
| Delete `RUN_STATE.md`, then `git mv joulewise/x.py RUN_STATE.md` | 1 (full) |
| Delete code plus a state edit | 1 |
| Add `.gitattributes` plus a state edit | 1 |
| Odd path name | 1 (git quotes the name, so it fails to match) |
| Empty range | 1 |
| chmod of RUN_STATE | 0 |
| RUN_STATE replaced by a symlink | 0 |

The chmod and symlink cases are harmless: no code executes from them, and quick's `test_gen_current.test_real_repository_agrees` would fail on a broken record. Code cannot slip through as state-only.

**Base-commit read.**
- ci.yml:84-89 runs `git show "$before:scripts/$1" | bash`, so a PR cannot weaken the classifier it is judged by.
- A PR can still rewrite `ci.yml` itself, as before. Such a PR is never state-only, so the full suite runs, but its own edited workflow decides what "full" means. That is a pre-existing property that review covers, not something new here.
- On a lane that lacks the script, `cat-file -e` fails and the full suite runs.

**What still runs on a state-only range.**
- quick, because `state=true`.
- fences, because it has no `if`. Fences runs `gen_state --check`, `repin --check`, `test_docs_freshness` and the receipt check.

**Live-content readers.**
- Of the 16 test files that name a state file, only `test_gen_state`, `test_gen_current` and `test_docs_freshness` read the live content.
- The others use the names as fixture strings or forbidden-write lists: flags_collect, harvest_b5_window, quiet_guard, air_watch_agent, night_results_watch, and comment references.
- The repository walkers (`git ls-files` users) look only at path sets, which a state edit cannot change. The one generic Markdown scanner is `test_docs_freshness`, which is in quick and in fences.
- `test_live_state_readers_are_in_the_quick_tier` keeps these three modules in the quick tier when the timing map changes.
- Base run 43435838556 shows the mechanism working: quick caught a stale `CURRENT.json`.

**Required contexts.**
- A state-only range sets `code=false`, so `test (3.13, 1..12)` and both exclusive jobs report success through their existing echo step. This is the same contract as docs-only, and intended.
- A false success is impossible in a non-state-only run. `state` is set only in the `elif`, so `code=true` and `state=true` never occur together, and the step outputs default to `code=true` and `state=false`.

**Nits.**
- N1: the ci.yml:76-78 comment says a state-only range "runs quick plus the modules that name the changed files" and cites `tests/test_ci_state_only.py`.
  - The implementation since `d610eac27` runs the plain quick tier, and the tests live in `tests/test_ci_docs_only.py`.
  - The PR title still says "plus the tests that name the state files".
  - Fix the comment and the title so the merge commit is accurate.
- N2: the state-only path cannot run in CI until it is on main. Watch the first `RUN_STATE`-only push after merge. Expect quick to run tests, fences to run, and the shards to echo.

---

## #758: ADMIT-WITH-FIXES

**Coverage: every test runs exactly once.**
- I compared per-module test counts between run 43463516682 (6 shards × 4 workers) and base push run 43435838556 (12 × 1, at `0101ee536`).
- There are 507 modules on both sides, and every module's count is identical except two:
  - `test_shard_split` grew from 36 to 46. That is the 10 new tests; the PR body says 9.
  - The base log shows `test_gen_current` once more, from its failing quick tier.
- Each child gets the shard's units through the same LPT packer, and `--units-file` runs exactly those units. A child that exits non-zero, prints no `SHARD SUMMARY`, or prints a FAIL summary fails the shard.
- Main's wall time fell to 23.5 min for the slowest shard, inside the 60-minute limit.

**Watchdog safety.**
- On expiry the watchdog prints the label, runs `faulthandler.dump_traceback`, then `os._exit(124)` (scripts/shard_tests.py:723). It sends no signal and calls no kill or reap, so it cannot reach another process.
- `run_units_in_workers` only waits on its children.
- The tests that make the watchdog fire do so in their own `subprocess.run([... -c ...])` children. The in-process test patches `_TestWatchdog` with a recorder.
- Binding the clock at import (:637) defeats the `time.monotonic` patches in `test_run_night`. `Condition.wait(timeout)` uses the C-level lock timeout, so patches to `time` cannot starve it.
- Thread-count tests on main and on the lane (`test_member_pool`, `test_r1_smoke_launcher`) compare deltas, and the single watchdog thread is started before any test.
- Nesting is handled: a run nested inside a test gets no watchdog.
- No test on main or the lane patches `os._exit`.

**Required fixes.**

- **F1: the 900 s margin is too thin for one main test.**
  - `test_controller_g2b_attachment.G2bAttachmentTests.test_tracked_bound_corpus_and_all_window_references_attach` ran 802 s in the #758 run, under 4-worker contention. That is 89% of the limit. It ran 624 s at the base and 526 s in the #755 lane run when it had a runner to itself.
  - A slower runner will trip the watchdog, giving a red that names the test. The failure is not silent, but it is a flake on a required gate. The test already exceeds RL-127's 10-minute unit budget.
  - Fix with one of:
    - (a) Set `JW_TEST_TIMEOUT_SECONDS` to 1200 (ci.yml:136, :306) until that test is split or sped up, with a comment naming it.
    - (b) Split or accelerate it in this PR.
  - Every other main test is at 389 s or less in this run.

- **F2: the retired-slot step can hide real shards** (ci.yml:164-165).
  - Slots 7-12 report success whenever `matrix.shard > 6`, and the literal 6 is held in sync with `SHARD_COUNT` only by a comment.
  - If `SHARD_COUNT` is ever raised to 7-12 without the literal, those partitions never run and the required contexts still go green. That is a silent coverage loss. Lowering `SHARD_COUNT` fails closed through an IndexError.
  - Fix with one of:
    - Make the step guard itself: `run: '[ "${{ matrix.shard }}" -gt "$SHARD_COUNT" ] || { echo "slot ${{ matrix.shard }} <= SHARD_COUNT=$SHARD_COUNT but marked retired"; exit 1; }; echo …'`.
    - Use `fromJSON(env.SHARD_COUNT)` in place of the literal in all the `if:` conditions; `env` is available in step `if`.
    - Add a quick-tier test asserting that the literal equals `SHARD_COUNT`.

**Optional.**
- O1: `run_units_in_workers` takes the first `SHARD_SUMMARY_RE` match (:1199). Pass or fail cannot be spoofed, because exit code 0 is also required. The counts could still be skewed if a test ever prints a nested summary to real stdout. Use the last match. The existing `run_workers` (:1084) has the same pattern.
- O2: the watchdog thread needs the GIL. A hang in C code that holds the GIL defeats it, and the job's 60-minute limit then fires with no name. A `faulthandler.dump_traceback_later(seconds + 120, exit=True)` backstop, re-armed in `arm()`, would name the stack anyway.
- O3: if a hung test leaves a grandchild holding the inherited stdout pipe, the parent's relay thread blocks after the child's `os._exit`. The job timeout ends it, and the TEST TIMEOUT line has already been relayed. Acceptable as is.

**Lane hazards: these must be settled before the lane merges main with #758.**
- The builder's list of 1,059-2,294 s lane tests is incomplete. In lane run 43459892780, `tests.test_bytes_coverage_map` took 3,321 s; its `OutputCoverageTests.setUpClass` and first test took about 3,218 s. #758 arms setUpClass under the module-import label, so it would be killed at 900 s.
- The BYTES world methods are at risk (L2 above).
- Lane shards 7, 3 and 1 took 62.8, 59.7 and 58.3 min at 12 × 1. That is at or over the new `timeout-minutes: 60`.
- Either split all of these first, or let the main-to-lane merge commit carry a lane-only `JW_TEST_TIMEOUT_SECONDS` and job timeout. Name the tests in that commit and remove the override when the splits land.
- The lane merge also needs the L3 prune.

---

## Merge order

1. **#755 to the lane, now.** It is independent of main, its CI is green, and the reports match serial byte for byte. Fill its ledger rows first.
2. **#756 to main.** Optionally fold in N1 first; no re-review is needed for a comment and title change.
3. **#758 to main after F1 and F2.** Its new head needs a green PR run. A delta check of the F1 and F2 lines is enough; no full re-review.
4. **A main follow-up, before the next main-to-lane merge:**
   - Prune L3.
   - Then the main-to-lane merge, with the lane long-test splits or a named lane-only override.

## Branch protection

- Keep `test (3.13, 7)` through `(3.13, 12)` required only until #758 is on main. Then do it in two steps, in this order:
  - (a) Remove contexts 7-12 from the required list for main, and for any lane branch that requires them.
  - (b) Merge a PR that deletes matrix slots 7-12 and the retired-slot step.
  - Reversing the order leaves the required contexts pending forever, which blocks every merge.
- Until then, F2 is what makes slots 7-12 trustworthy. Without F2 they are unconditional green lights in every run.
- Changing the setting is the lead's call. I changed nothing.

## Merge-tier proposal (/Volumes/JW-EXT/scratch/ci-merge-tier-proposal.md)

**Recommendation: defer the tiering, adopt rule 4 now, and re-measure.**

- **The premise is out of date.** The proposal prices a full run at hours, citing #752's 4 h 55 min. With #758, main's full suite takes about 24 min, which is inside RL-127's 30-minute PR budget. A light tier would save about 20 min per covered PR, not about 5 h per night cycle. It would buy that with two gate meanings ("merge-green" and "sign-green") that every ledger row and seat brief must then keep apart. At about 24 min, that complexity is not worth it on main.
- The lane is where the time goes: about 60 min at 12 × 1, plus the long tests above. The fix there is the splits, not a weaker merge gate.
- **Adopt rule 4 now.** No re-runs against a known-red base: revert or fix the base first. This is cheap, and it addresses the real #752 failure, a merge while red.
- **If tiering is revisited** after post-#758 measurements:
  - Narrow "tests only" to leaf `tests/**/test_*.py` modules. Shared helpers (`tests/__init__.py`, `host_command_guard.py`, `_host_guard_site/**`, `git_fixture.py`, `fixtures/**`, support modules) affect modules that import them by module name, not by path. A path-text "touched" selector misses those importers.
  - Admit "config-token" only through a mechanical classifier: key-set diff, read from the base. It must refuse:
    - any path named in `configs/pins/registry.json`, the sealed inventories or `R1_EXECUTED_SOURCES` (which includes `configs/align/v4/r1_runtime.json`);
    - anything under `configs/b6/packs/**`.
  - Do not rely on the Impact line for this.
  - Keep the "full suite on the lane head before sign, pin or arm" rule in any case. It is a good rule on its own.
